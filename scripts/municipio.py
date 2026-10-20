"""Identidade do município: usada pelos scripts de clima, previsão e geocodificação.

O código IBGE (e o do TSE), o nome e a URL também aparecem nos scripts de coleta, nos builds, em render.py e nos templates;
para outra cidade, troque-os também, além da paleta em static/style.css.
"""

from __future__ import annotations

NOME = "Porto Feliz"
NOME_MAIUSCULO = "PORTO FELIZ"
UF = "SP"
UF_NOME = "São Paulo"
SLUG = "porto-feliz"
PRODUTO = "Porto Feliz em Dados"
IBGE = "3540606"
IBGE6 = IBGE[:6]  # CAGED, CNES, SIH e SIM usam o código sem o dígito verificador
TSE = "69132"  # o TSE tem código próprio de município
AGENTE = "PortoFelizEmDados/1.0"
REPO_URL = "https://github.com/civisbr/porto-feliz-em-dados"
SITE_URL = "https://civisbr.github.io/porto-feliz-em-dados/"
# Centro do município; a base de clima (ERA5) usa a célula de grade mais próxima.
LAT, LON = -23.2144, -47.5242
# Caixa (S, O, N, L) um pouco maior que o contorno, para consultas ao Overpass/Nominatim.
BBOX = "-23.40,-47.65,-23.07,-47.38"
