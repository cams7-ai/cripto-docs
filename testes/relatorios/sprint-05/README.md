# Relatórios da Sprint 05

Os relatórios distinguem a fixture técnica do histórico público. Cada segmento, variante e perfil tem carteira independente; patrimônios e retornos não são somados.

| Conteúdo | Leitura humana | Dados selecionados |
|---|---|---|
| Histórico público, BTCUSDT/15m | [PDF](../../../output/pdf/sprint-05-avaliacao-historica.pdf) · [HTML](public/report.html) | [Resultados](public/resultados.json) · [Execução](public/execucao.json) · [Manifesto](public/manifest.json) |
| Fixture sintética, sem valor econômico | [PDF](../../../output/pdf/sprint-05-ensaio-tecnico.pdf) · [HTML](fixture/report.html) | [Resultados](fixture/resultados.json) · [Execução](fixture/execucao.json) · [Manifesto](fixture/manifest.json) |

Os PDFs têm quatro páginas: escopo e resultados, curvas comparáveis, sensibilidade e auditoria. O HTML detalha todas as curvas, com custos, recusas, expirações, travas e posição residual. Gráficos reduzidos não alteram as métricas da série integral.

O bundle documental omite os pontos dos gráficos no JSON selecionado. `result_sha256` identifica o JSON canônico completo do export original, e não esse subconjunto. Cada manifesto documental registra os hashes locais, o PDF e o manifesto original.

Os CSVs integrais e o JSON completo permanecem no diretório de exportação da aplicação, indicado em `execucao.json` e `resultados.json`. Os links dos HTMLs foram ajustados para esses arquivos dentro do workspace, sem alterar valores ou gráficos. Bancos e arquivos operacionais de grande volume não são versionados em docs; após um clone novo, é necessário restaurar/reproduzir o export para usar esses links.

[Guia e critérios](../../sprint-05-validacao.md) · [Evidências](../../sprint-05-evidencias.json) · [Gerador de PDF](../../ferramentas/sprint-05-relatorio-pdf.py).

Os limites de entrada/exposição são verificados na admissão. A exposição marcada varia com o preço; travas de perda não liquidam automaticamente a posição.

Sem autorização LIVE ou início automático da Sprint 06. Filtros são proxy sintético; open OHLC e fill integral são hipóteses, sem garantia de liquidez. O registro local do teste final não prova ausência de conhecimento humano prévio.
