# STATUS — quadro de handoff entre chats

Todo chat do projeto lê isto ao começar e atualiza ao terminar. É a "conversa" entre os chats.

## Agora

- **Fase:** semana 1 — extração de PDF funcionando (1T26)
- **Próximo passo:** (1) trazer o release 2T26 da Embraer para raw/EMBJ3/ e rodar os testes nele; (2) push do repo; (3) testar no chat o prompt de extração estruturada com os PDFs reais
- **Bloqueios:** repo `PedroSalzmann/release-diff` ainda não existe no GitHub (criar vazio); download do 2T26 travou no Chrome do Pedro

## Decidido

- Primeiro entregável: release diff (monitor de deal flow vem depois)
- Estrutura raw/ → wiki/ → output/ com verificação independente de números
- MVP = diff de texto (guidance, tom, temas, alocação de capital); regra dos números vale para todo número citado; sem parsing de tabela (ver DECISOES.md)
- Extração: PyMuPDF em modo blocks (`src/extract.py`)
- Primeiro teste: Embraer 1T26 vs 2T26; nome do repo: release-diff

## Em aberto (decisões do Pedro)

- Definição de mudança de guidance, critério de tom, definição de tema (passar pelo painel de personas)
- Vale e Localiza entram como 2ª e 3ª empresa? (proposta do chat de escopo)

## Log (mais recente em cima, uma linha por sessão)

- 2026-10-15 · chat de execução (Opus + subagente Sonnet) · decisões de escopo fechadas, 1T26 baixado do RI, `extract.py` + 5 testes passando, extração conferida contra a p. 4 renderizada; achados em wiki/embraer.md (`5.6%` com ponto no próprio PDF, hífen invisível U+00AD)
- 2026-10-15 · chat gestor (Opus) · esqueleto do repo, CLAUDE.md, roteamento de modelos
