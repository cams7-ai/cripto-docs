# Relatórios de processamento

Emissão: 25/10/2026. Escopo: evidências históricas das Sprints 01 a 03.

- [Relatório consolidado em PDF, seis páginas](pdf/relatorio-sprints-01-a-03.pdf)
- [Versão HTML para leitura no navegador](html/relatorio-sprints-01-a-03.html)
- [Inventário das fontes e hashes SHA-256](fontes-relatorio-sprints-01-a-03.txt)

Conteúdo: resumo executivo, base segura da Sprint 01, coleta sintética da Sprint 02, operações e composição do resultado financeiro da Sprint 03, risco, reconciliação, testes, proveniência e limitações. PDF e HTML apresentam o mesmo conteúdo.

As fontes são os guias e evidências em `docs/testes/`, o relatório/manifesto da verificação financeira final e a exportação da coleta fixture. No inventário, caminhos iniciados por `testes/` são relativos a `docs`; caminhos iniciados por `cripto-bot/` são relativos ao workspace `/home/cams7/Dev/Cripto`.

Nesta emissão foram conferidos os cálculos financeiros, o replay sem novos fills, o balanceamento do ledger por evento e ativo e os hashes dos arquivos exportados consultados. O PDF foi renderizado e suas seis páginas revisadas visualmente. As suítes automatizadas e as operações financeiras não foram repetidas; o banco operacional não foi revalidado. Os números de testes por Sprint são acumulados e não devem ser somados.

Os valores são fictícios, com decisões de compra e venda roteirizadas; o resultado positivo não avalia uma estratégia automática. Estes arquivos são apresentações retrospectivas dos dados existentes e não implementam geração automática de PDF/HTML na aplicação. Os JSONs e aceites históricos permanecem preservados.


## Sprint 04 — estratégia SMA em fixture

- [Relatório HTML gerado automaticamente pela aplicação](html/relatorio-sprint-04.html)
- [Validação e resultados observados](../testes/sprint-04-validacao.md)
- [Evidências estruturadas, hashes e schema](../testes/sprint-04-evidencias.json)

A cópia HTML é idêntica à primeira exportação da demonstração final de 71 ciclos.
Inclui 2 fills, perda fictícia de 94.53818742 USDT e replay verificado sem efeitos
novos. O gerador da Sprint 04 publica JSON/HTML/manifesto por execução; os
relatórios consolidados 01–03 acima continuam apresentações retrospectivas.
Revisão visual feita em Chrome headless com perfil temporário e rede externa
bloqueada. A revisão não executou novas operações.
