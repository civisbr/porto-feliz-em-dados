# Porto Feliz em Dados

Dados públicos de Porto Feliz/SP em um site estático, leve e com fonte à vista. Uma iniciativa [CivisBR](https://github.com/civisbr).

**Site:** https://civisbr.github.io/porto-feliz-em-dados/

## Painéis

O menu agrupa os painéis em cinco áreas.

| Área | Painel | Pergunta | Fonte | Atualização |
|---|---|---|---|---|
| A cidade | [Perfil da cidade](https://civisbr.github.io/porto-feliz-em-dados/cidade/) | Quanta gente mora em Porto Feliz e o que a economia produz? | Censo 2022, estimativas e PIB (IBGE) | anual |
| A cidade | [Comparativo](https://civisbr.github.io/porto-feliz-em-dados/comparativo/) | Em que posição Porto Feliz está entre os municípios, e como isso mudou? | IBGE e INEP | anual |
| A cidade | [Clima](https://civisbr.github.io/porto-feliz-em-dados/clima/) | Como é o clima e o que esperar nesta semana? | INMET e Open-Meteo (ERA5) | diária (previsão) |
| Economia | [Emprego](https://civisbr.github.io/porto-feliz-em-dados/emprego/) | Porto Feliz está gerando mais ou menos empregos? | Novo CAGED (MTE) | mensal |
| Saúde | [Doenças do momento](https://civisbr.github.io/porto-feliz-em-dados/saude/) | Como estão a dengue e a chikungunya? | InfoDengue (Fiocruz/FGV) | semanal |
| Saúde | [Hospitais e leitos](https://civisbr.github.io/porto-feliz-em-dados/hospitais/) | Quais estabelecimentos atendem e o que cada um trata? Mapa dos estabelecimentos. | CNES e SIH/SUS (DATASUS) | mensal |
| Saúde | [Mortes e nascimentos](https://civisbr.github.io/porto-feliz-em-dados/panorama/) | De que as pessoas morrem e quantas crianças nascem? | SIM e SINASC (DATASUS) | mensal |
| Saúde | [Vacinas](https://civisbr.github.io/porto-feliz-em-dados/vacinas/) | Quais vacinas tomar em cada idade e há campanha acontecendo? | Calendário Nacional (Ministério da Saúde) e campanhas da Prefeitura | curadoria manual, com aviso quando passa de 120 dias |
| Serviços e segurança | [Escolas](https://civisbr.github.io/porto-feliz-em-dados/escolas/) | O que os dados mostram sobre cada escola? Mapa e página por escola, sem ranking. | Censo Escolar e IDEB (INEP) | anual |
| Serviços e segurança | [Segurança](https://civisbr.github.io/porto-feliz-em-dados/seguranca/) | Que ocorrências são registradas, quando e com que tendência? Mapa de roubos e furtos com "registros perto de você". | SSP-SP | mensal |
| Serviços e segurança | [Trânsito](https://civisbr.github.io/porto-feliz-em-dados/transito/) | Como estão os sinistros e os medidores de velocidade estão com a verificação em dia? | Infosiga SP (Detran-SP), Inmetro e ARTESP (rodovias, opcional) | mensal (Inmetro: coleta manual) |
| Política | [Representantes](https://civisbr.github.io/porto-feliz-em-dados/representantes/) | Quem governa e quem representa Porto Feliz? Posição ideológica dos partidos (esquerda, centro, direita), segundo especialistas. | TSE, Câmara dos Deputados, Alesp e Bolognesi et al. (2025) | por eleição |

### Mapas interativos

Hospitais, escolas, segurança e trânsito usam um mapa único (`static/mapa-interativo.js`, SVG sobre uma base do OpenStreetMap guardada no repositório). Dá para filtrar por tipo, tocar num ponto para ver os detalhes e, se a pessoa permitir, achar o mais próximo. A localização fica só no navegador e nunca é enviada; o link "Como chegar" arredonda a posição a 3 casas decimais.

### Trânsito: medidores e verificação

- A verificação metrológica dos medidores vem do Portal de Serviços do Inmetro (dados abertos, CC0), filtrada por município. O host do Inmetro bloqueia os servidores do GitHub, então essa coleta é manual (`fetch_inmetro` e `build_inmetro`, de uma máquina no Brasil); o workflow `inmetro-aviso.yml` abre uma issue quando a última coleta passa de 14 dias.
- Sem lista oficial de radares da prefeitura, o painel mostra só os medidores registrados no Inmetro, com a posição obtida do OpenStreetMap.
- O bloco de rodovias (ARTESP) só aparece quando existe `data/public/artesp.json`, que depende da chave `ARTESP_API_KEY`.

Cada painel mostra a fonte primária, a data de referência, a data da coleta e as limitações conhecidas. Os dados publicados ficam em `data/public/*.json` e também são servidos pelo site em `/data/`.

## Princípios

1. **Nenhum número sem origem.** Todo valor é rastreável até o arquivo baixado da fonte. O que a fonte não publica fica vazio ou `pendente`, nunca estimado em silêncio.
2. **Todo dado é classificado** como `real`, `estimativa` ou `pendente`, e isso aparece na interface.
3. **Data de referência obrigatória.** Dado sem ela não entra no build.
4. **Pipeline determinístico e offline.** Rodar o build duas vezes sobre o mesmo bruto gera bytes idênticos. A data de coleta entra por parâmetro, não pelo relógio.
5. **Sem ranking onde o dado não suporta.** Escolas não são ordenadas por IDEB.

## Como funciona

```
fetch (só rede)  →  data/raw/  →  build (puro, offline)  →  data/public/*.json  →  render  →  dist/
```

- `scripts/fetch_*.py` baixam da fonte e guardam apenas o recorte de Porto Feliz, com hash no manifesto. Não há microdado individual no repositório.
- `scripts/build_*.py` transformam o bruto em JSON validado pelo contrato em `schemas/envelope.py`.
- `scripts/render.py` gera o HTML estático (Jinja2) e os gráficos em SVG. O site funciona sem JavaScript; a busca é um acréscimo opcional.
- Workflows em `.github/workflows/` atualizam os dados no agendamento, rodam os testes e publicam no GitHub Pages.
- `scripts/municipio.py` concentra nome, códigos IBGE/TSE, coordenadas e URLs do município.

| Fonte | Coleta | Observação |
|---|---|---|
| CAGED | FTP do MTE, janela de 24 meses | saldo = movimentações + fora de prazo − exclusões, por competência |
| INEP | zips de IDEB por escola e Censo Escolar | o servidor não envia o certificado intermediário; ele está em `certs/` e a cadeia TLS segue validada |
| ARTESP (CCM) | API de ocorrências rodoviárias, com chave pessoal no segredo `ARTESP_API_KEY` | opcional; só contagens por mês, rodovia, tipo e trecho de 5 km; `data/public/artesp.json` herda a licença CC BY-NC 4.0 (uso não comercial, com atribuição) |
| SSP-SP, Infosiga | planilhas de ocorrências e de sinistros | só o recorte de Porto Feliz; células pequenas são suprimidas na coleta (limites em `scripts/infosiga_regras.py`) |
| DATASUS | CNES, SIH/SUS (FTP), SIM e SINASC | `scripts/dbc.py` descomprime os `.dbc` em Python puro |
| Inmetro | `medidores.json` do PSIE (SP) | coleta manual; guarda só os medidores de Porto Feliz, com hash |
| OpenStreetMap | Overpass e Nominatim, à mão | `geocode_*.py` e `fetch_osm_base.py` rodam manualmente; uso moderado, ODbL |

## Rodando localmente

Requer Python 3.12+ e [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest -q

# atualizar dados (rede)
uv run python -m scripts.fetch_caged --auto 24 --acesso-em "$(date -u +%F)"
uv run python -m scripts.fetch_inep  --acesso-em "$(date -u +%F)"
uv run python -m scripts.fetch_perfil --acesso-em "$(date -u +%F)"
uv run python -m scripts.fetch_comparativo --acesso-em "$(date -u +%F)"
uv run python -m scripts.fetch_ssp --acesso-em "$(date -u +%F)"  # baixa ~1 GB da SSP-SP
uv run python -m scripts.fetch_representantes --acesso-em "$(date -u +%F)"  # baixa ~1 GB do TSE
uv run python -m scripts.fetch_inmetro --acesso-em "$(date +%F)"  # de uma máquina no Brasil
uv run python -m scripts.geocode_inmetro

# transformar e gerar o site (offline)
uv run python -m scripts.build_emprego
uv run python -m scripts.build_escolas
uv run python -m scripts.build_perfil
uv run python -m scripts.build_comparativo
uv run python -m scripts.build_seguranca
uv run python -m scripts.build_representantes
uv run python -m scripts.build_inmetro
uv run python -m scripts.render

python3 -m http.server --directory dist 8080
```

## Estrutura

```
data/raw/        recortes de Porto Feliz + manifestos com hash
data/public/     JSON publicado, um por painel
schemas/         contrato dos dados (pydantic)
scripts/         fetch, build, geocode (manual) e render
templates/       HTML (Jinja2)
static/          CSS e JS
tests/           testes, incluindo determinismo e orçamento de peso por página
```

## Contribuindo

Abra uma issue ou um pull request. O CI roda os testes e o render em todo PR. Mudanças que exibam números novos precisam citar a fonte primária e a data de referência.

## Licença e dados

Os dados pertencem às fontes originais e seguem as licenças delas, citadas em cada painel. A licença do código ainda não foi definida.

Dados derivados do OpenStreetMap: © colaboradores do OpenStreetMap, licença ODbL 1.0 (https://www.openstreetmap.org/copyright). As posições dos medidores do Inmetro (`data/raw/inmetro/coordenadas.csv`), as das escolas (`data/raw/inep/coordenadas.csv`, do Nominatim) e a base cartográfica do mapa (`data/raw/osm/base_porto_feliz.json`, com vias, rios e 149 bairros do município) vêm do OSM. A base cartográfica é um extrato substancial: ela, o `mapa-base.svg` e o `data/mapa-bairros.json` publicados no site estão sob a ODbL 1.0.

Fonte do logotipo: Orbitron, © 2018 The Orbitron Project Authors (https://github.com/theleagueof/orbitron), licença SIL Open Font License 1.1 (`static/fonts/OFL-Orbitron.txt`). O arquivo `static/fonts/orbitron-subset.woff2` é uma versão modificada (subconjunto de glifos), renomeada "SED Wordmark" conforme a condição de nome reservado da licença.
