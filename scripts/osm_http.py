"""Consultas ao OpenStreetMap (Nominatim e Overpass) compartilhadas pelos geocodificadores e por geo_aprox."""

from __future__ import annotations

import re
import time
import unicodedata
from pathlib import Path

import httpx

RAIZ = Path(__file__).resolve().parent.parent
NOMINATIM = "https://nominatim.openstreetmap.org/search"
OVERPASS = "https://overpass-api.de/api/interpreter"
HOSTS = {"nominatim.openstreetmap.org", "overpass-api.de"}
CAMPOS = ["ponto", "local", "lat", "lon", "precisao", "fonte_osm", "osm_ref", "geocodificado_em", "candidatas", "detalhe"]
AGENTE = "PortoFelizEmDados/1.0 (+https://github.com/civisbr/porto-feliz-em-dados)"
TITULOS = {
    "AV": "AVENIDA", "R": "RUA", "DR": "DOUTOR", "DRA": "DOUTORA", "PROF": "PROFESSOR", "PROFA": "PROFESSORA", "ENG": "ENGENHEIRO",
    "CEL": "CORONEL", "PE": "PADRE", "CAP": "CAPITÃO", "GAL": "GENERAL", "MAL": "MARECHAL", "TEN": "TENENTE", "DEP": "DEPUTADO",
    "SEN": "SENADOR", "ALM": "ALMIRANTE", "VER": "VEREADOR", "PRES": "PRESIDENTE", "STA": "SANTA", "STO": "SANTO", "TRAV": "TRAVESSA",
    "ROD": "RODOVIA", "AL": "ALAMEDA", "PC": "PRAÇA", "PÇA": "PRAÇA", "CÔN": "CÔNEGO", "MONS": "MONSENHOR", "CDOR": "COMENDADOR",
}
CACHE_OSM = RAIZ / "data" / "raw" / "osm" / "cache" / "aproximacao.json"


def so_host_confiavel(r: httpx.Request) -> None:
    if r.url.scheme != "https" or r.url.host not in HOSTS:
        raise ValueError(f"requisição fora dos hosts esperados: {r.url.host}")


def expandir(nome: str) -> str:
    palavras = re.sub(r"[.,]", " ", nome.upper()).split()
    return " ".join(TITULOS.get(p, p) for p in palavras)


REFERENCIA = re.compile(r"\b(?:PR[ÓO]X\.?|APROX\.?|COM)\s+(?=AV|R\b|RUA|PÇA|PRA[ÇC]A|TRAV|ROD|AL\b)")
NUMERO = re.compile(r"N\s*[º°O.]\s*(\d+)\b|,\s*(\d+)\b")


def interpretar(local: str) -> tuple[str, list[str], str | None]:
    """('cruzamento'|'endereco'|'rua', vias, número). Via de referência ("PRÓX RUA X") é descartada."""
    s = re.sub(r"\((?:C/B|B/C)\)", " ", local.upper())
    antes = REFERENCIA.split(s)[0]
    s = antes if antes.strip() else s
    s = re.sub(r"\b(OPOSTO|PR[ÓO]X\.?)\s*(AO|A)?\b", " ", s)
    if re.search(r"\sX\s", s):
        return "cruzamento", [expandir(p) for p in re.split(r"\sX\s", s) if p.strip()], None
    m = NUMERO.search(s)
    rua = expandir(re.split(r",|N\s*[º°O.]\s*\d", s)[0])
    return ("endereco", [rua], m.group(1) or m.group(2)) if m else ("rua", [rua], None)


def contexto_http() -> httpx.Client:
    return httpx.Client(timeout=60, headers={"User-Agent": AGENTE}, follow_redirects=True, max_redirects=3, event_hooks={"request": [so_host_confiavel]})


def buscar_endereco(c: httpx.Client, rua: str, numero: str) -> tuple[float, float, str] | None:
    """Só aceita resultado que seja o próprio imóvel e traga o número pedido; via, bairro ou cidade não servem."""
    r = c.get(NOMINATIM, params={"street": f"{numero} {rua.title()}", "city": "Porto Feliz", "state": "São Paulo", "country": "Brasil", "format": "jsonv2", "addressdetails": 1, "limit": 1})
    r.raise_for_status()
    achados = r.json()
    if not achados:
        return None
    a = achados[0]
    end = a.get("address", {})
    pedida = palavras(rua)
    if a.get("addresstype") not in ("house", "building") or str(end.get("house_number", "")).strip() != numero or not pedida or not pedida <= palavras(end.get("road", "")):
        return None
    return float(a["lat"]), float(a["lon"]), f"{a.get('osm_type')}/{a.get('osm_id')}"


STOP = {"AVENIDA", "RUA", "DE", "DA", "DO", "DAS", "DOS", "DOUTOR", "DOUTORA", "PROFESSOR", "PROFESSORA", "TRAVESSA", "RODOVIA", "ALAMEDA", "PRACA"}


def palavras(nome: str) -> set[str]:
    sem_acento = unicodedata.normalize("NFD", nome.upper()).encode("ascii", "ignore").decode()
    return {w for w in re.sub(r"[^A-Z ]", " ", sem_acento).split() if w not in STOP}



def overpass(c: httpx.Client, consulta: str) -> list[dict]:
    for t in range(5):
        r = c.post(OVERPASS, data={"data": consulta})
        if r.status_code == 200:
            corpo = r.json()
            if corpo.get("remark") or "elements" not in corpo:  # resposta truncada faria outra câmera parecer única
                raise RuntimeError(f"Overpass devolveu resposta incompleta: {corpo.get('remark')}")
            return corpo["elements"]
        if r.status_code < 500 and r.status_code != 429:
            r.raise_for_status()
        time.sleep(15 * (t + 1))
    raise RuntimeError("Overpass indisponível")
