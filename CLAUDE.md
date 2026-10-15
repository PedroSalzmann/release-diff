# CLAUDE.md — release-diff

Projeto de portfólio (Pedro Salsman): compara dois releases de resultado trimestral de uma empresa da B3 e entrega um diff de guidance, tom da gestão, temas e alocação de capital, cada achado com página e trecho literal. Parsing de tabelas de KPI fica para a v2.

## Leia antes de trabalhar

- `claude/00-contexto-roadmap-principios.md` — contexto, stack e os princípios (números vêm do código; tudo auditável).
- `claude/01-escopo-release-diff.md` — escopo, pipeline, schema e critérios de "pronto".
- `claude/02-padrao-repo-readme.md` — estrutura de pastas e padrão de README.
- `claude/03-log-de-progresso.md` — onde paramos. **Único quadro de handoff: leia ao começar, atualize ao terminar.**

Se este arquivo e os docs divergirem, os docs mandam.

## Mapa do repo (resumo; detalhe no doc 02)

```
raw/     insumos baixados, NUNCA editados
wiki/    notas por empresa, glossário, decisões de parsing
output/  tudo que é gerado — não escrito à mão
src/     código Python
tests/   pytest
docs/    DECISOES.md, ROTEAMENTO.md (qual modelo faz o quê)
```

## 4 regras de trabalho

1. **Pense antes de codar.** Diga as premissas. Se o pedido for ambíguo, pergunte.
2. **Simples primeiro.** O mínimo de código que resolve; nada "pra depois".
3. **Mudança cirúrgica.** Toque só no que o pedido exige.
4. **Defina o "pronto" e verifique.** Só diga "terminei" depois de rodar a verificação.

## Números

Regra inegociável, detalhada no doc 00 (princípios 1–2): número vem do código, nunca do LLM; toda citação é validada contra o texto da página. Unidade, período ou critério trocado conta como erro. Na dúvida, o achado sai marcado como "não verificado".
