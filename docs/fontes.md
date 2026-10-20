# Catálogo de fontes — Porto Feliz em Dados

Uma seção por fonte: o que é usado, como é coletado, o recorte de Porto Feliz e as limitações conhecidas. Origem, data de acesso e hash de cada coleta ficam no `manifesto.json` de `data/raw/<fonte>/`; a data de referência de cada número aparece no painel.

## Identificação do município

| Item | Valor | Onde é usado |
|---|---|---|
| Código IBGE | 3540606 | perfil, comparativo, malha, INEP, Infosiga, Inmetro |
| Código IBGE de 6 dígitos | 354060 | CAGED, CNES, SIH, SIM/SINASC |
| Código TSE | 69132 | representantes (o TSE usa código próprio) |
| Centro | −23,2144 / −47,5242 | clima e previsão (Open-Meteo) |

Porto Feliz pertence à região imediata e à microrregião de Sorocaba, o que justifica o rótulo "Microrregião de Sorocaba" no comparativo. Nome, códigos, coordenadas e URLs ficam em `scripts/municipio.py`; scripts de coleta, builds, `render.py` e templates ainda repetem alguns desses valores.

## IBGE — perfil, comparativo e malha

- **Perfil:** Censo 2022, estimativas populacionais e PIB municipal (`fetch_perfil`).
- **Comparativo:** indicadores do IBGE e do INEP para os municípios da microrregião (`fetch_comparativo`).
- **Malha municipal:** contorno do município para o mapa da home (`fetch_ibge`).
- Atualização anual. Estimativa não é contagem: o painel marca o que é `estimativa`.

## Novo CAGED — Ministério do Trabalho e Emprego

- FTP do MTE, janela de 24 meses (`fetch_caged --auto 24`); filtro pelo código de 6 dígitos.
- Saldo = movimentações + fora de prazo − exclusões, por competência. Os ajustes retroativos mudam meses já publicados, então cada coleta reescreve a janela inteira.
- Atualização mensal (`emprego.yml`).

## INEP — IDEB e Censo Escolar

- Zips de IDEB por escola (anos iniciais e finais) e Censo Escolar (`fetch_inep`); 44 escolas no recorte atual.
- O servidor não envia o certificado intermediário. Ele está em `certs/` e a validação TLS continua ativa.
- Sem ranking: o painel mostra os dados de cada escola, sem ordenar por IDEB. Escola sem IDEB (rede pequena, sem divulgação) aparece como `pendente`.
- Endereço vem do Censo Escolar; a posição no mapa vem do Nominatim (ver OpenStreetMap).

## DATASUS — CNES, SIH/SUS, SIM e SINASC

- **CNES** (estabelecimentos e leitos), **SIH/SUS** (internações), **SIM** (óbitos) e **SINASC** (nascimentos) por FTP, em `.dbc`, descomprimidos por `scripts/dbc.py`.
- O recorte de Porto Feliz tem 1 hospital, 11 UBS, 1 UPA/pronto-socorro e 1 CAPS. Por serem poucos estabelecimentos, o piso de plausibilidade do `fetch_cnes` é baixo (pelo menos 1 hospital e 20 leitos existentes).
- Atualização mensal (`hospitais.yml`, `vitais.yml`).

## InfoDengue — Fiocruz/FGV

- API pública por município; dengue e chikungunya por semana epidemiológica (`fetch_infodengue`).
- Atualização semanal (`infodengue.yml`). É estimativa de notificações, não casos confirmados.

## SSP-SP — segurança pública

- Planilhas de ocorrências (`fetch_ssp`, cerca de 1 GB por baixada); guarda só o recorte do município.
- Registro policial não é crime ocorrido: parte nunca é registrada. O painel mostra tendência e distribuição, não "cidade mais ou menos segura".
- Atualização mensal (`seguranca.yml`).

## Infosiga SP (Detran-SP) — sinistros de trânsito

- Planilhas de sinistros e vítimas (`fetch_infosiga`); só o recorte de Porto Feliz.
- Células pequenas são suprimidas na coleta (limites em `scripts/infosiga_regras.py`), para não identificar pessoas.
- Atualização mensal (`infosiga.yml`).

## ARTESP (CCM) — ocorrências em rodovias

- API de ocorrências rodoviárias, com chave pessoal no segredo `ARTESP_API_KEY` (`fetch_artesp`, `build_artesp`).
- Guarda só contagens por mês, rodovia, tipo e trecho de 5 km; relato, veículos e pontos exatos não são guardados.
- Só rodovias concedidas monitoradas pelo CCM: não é o total de acidentes nas rodovias, e meses sem registro podem ser lacuna da fonte. As rodovias com acidentes no recorte são a SP 280 e a SP 300.
- `data/public/artesp.json` herda a licença CC BY-NC 4.0 (uso não comercial, com atribuição). Se o arquivo não existir, o bloco de rodovias some do painel de Trânsito.
- Coleta mensal (`artesp.yml`, dia 17).

## Inmetro (PSIE) — verificação dos medidores de velocidade

- Portal de Serviços do Inmetro (dados abertos, CC0), `medidores.json` do estado de SP, filtrado por município (`fetch_inmetro`, `build_inmetro`).
- O host do Inmetro bloqueia os servidores do GitHub; a coleta é manual, de uma máquina no Brasil. O workflow `inmetro-aviso.yml` abre uma issue quando a última coleta passa de 14 dias.
- O recorte atual tem 5 medidores. A posição de cada um vem do OpenStreetMap (`geocode_inmetro`).
- A prefeitura não publica lista de radares, então o painel não afirma quantos radares existem nem onde estão todos: mostra só o que o Inmetro registra.

## INMET e Open-Meteo — clima

- **Clima histórico:** reanálise ERA5 pela API do Open-Meteo, na célula de grade mais próxima do centro do município (`fetch_clima`).
- **Previsão:** Open-Meteo, atualizada diariamente; o arquivo não é versionado.
- A estação convencional do INMET mais próxima é a de Iperó, a cerca de 24 km: o painel não a apresenta como "a estação da cidade".

## TSE, Câmara, Alesp e especialistas — representantes

- Resultados da eleição pelo TSE (código 69132), deputados da Câmara e da Alesp, e a classificação ideológica dos partidos de Bolognesi et al. (2025) (`fetch_representantes`, `fetch_ideologia`).
- Partidos fora da classificação aparecem como "não classificado", sem chute. Atualização por eleição.

## Vacinas — curadoria manual

- **Calendário Nacional de Vacinação** (Ministério da Saúde), em `data/raw/vacinas/calendario.csv`; conferido em 2026-10-11.
- **Campanhas** da Prefeitura de Porto Feliz em `campanhas.csv`. Sem campanha cadastrada, o painel diz isso e avisa que a busca por campanhas locais é parcial.
- O workflow `vacinas-aviso.yml` abre uma issue quando a conferência passa de 120 dias.

## OpenStreetMap — base cartográfica e posições

- `fetch_osm_base` extrai vias principais, rios e 149 bairros do município (Overpass) em `data/raw/osm/base_porto_feliz.json`; `geocode_escolas` e `geocode_inmetro` usam Nominatim e Overpass.
- Coletas manuais e moderadas, com identificação do agente (`PortoFelizEmDados/1.0`). Licença ODbL 1.0, com os avisos em `LICENCA*.txt` de cada pasta.

## Fontes não usadas em Porto Feliz

| Fonte | Motivo |
|---|---|
| ANP — Levantamento de Preços de Combustíveis | A amostra da ANP cobre 100 municípios de SP e Porto Feliz não tem nenhuma linha. O painel de Combustível não existe aqui. |
| Semob (radares) | Órgão de outra cidade; Porto Feliz não publica lista equivalente. |
| Câmeras da cidade | Não há fonte aberta verificada. |
