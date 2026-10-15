# DECISÕES

Registro curto de decisões que não devem ser rediscutidas a cada chat. Formato: data · decisão · motivo.

- 2026-10-15 · Começar pelo release diff · escopo mais fechado; o monitor de deal flow reaproveita o parser depois
- 2026-10-15 · Dados oficiais (CVM/RI) antes de scraping · mais robusto e mais forte como argumento de portfólio
- 2026-10-15 · Números vêm do código e toda citação é validada contra a página (doc 00, princípios 1–2) · número errado invalida o projeto
- 2026-10-15 · MVP = diff de texto (guidance, tom, temas, alocação de capital); a regra dos números vale para todo número citado num achado · é o que diferencia o projeto; parsing de tabela é frágil e caro para o MVP
- 2026-10-15 · Sem parsing de tabela no MVP · o guidance da Embraer aparece por extenso na narrativa (pp. 3 e 4), então a tabela é redundante
- 2026-10-15 · PyMuPDF em modo blocks, ordem coluna → y · `pdftotext -layout` mistura rótulos de gráfico nas frases (p. 5 do 1T26) e quebraria a validação de citação literal
- 2026-10-15 · Primeiro teste: Embraer 1T26 vs 2T26 · guidance com itens mantidos e elevados no mesmo par
- 2026-10-15 · Mudança de guidance = só metas quantitativas explícitas; LLM extrai e pareia, código classifica · auditável e sem LLM comparando números (detalhe: doc 01, decisão 1)
- 2026-10-15 · Tom = mudança por dimensão em frases prospectivas que mudaram; rótulo geral por regra no código · separa resultado de expectativa (doc 01, decisão 2)
- 2026-10-15 · Tema = assunto específico e nomeável; novo/sumiu confirmados por palavra-chave específica no outro release · evita "novo" por troca de palavras (doc 01, decisão 3)
- 2026-10-15 · Empresas do MVP: Embraer, Vale, Localiza; par 1T26→2T26, 2T26→3T26 como teste · guidance forte, alocação de capital, controle negativo (doc 01, decisão 4)
