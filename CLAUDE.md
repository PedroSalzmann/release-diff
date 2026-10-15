# CLAUDE.md — release-diff

Projeto de portfólio (Pedro Salsman): compara dois releases de resultado trimestral de uma empresa listada na B3 e entrega um diff de guidance, tom da gestão, temas e alocação de capital — o que mudou e o que a empresa parou ou começou a dizer, cada achado com página e trecho literal. Todo número citado num achado segue a regra dos números abaixo. Parsing de tabelas de KPI fica para a v2.

## Mapa do repo

```
raw/       insumos baixados, NUNCA editados (PDFs de releases, planilhas da CVM)
wiki/      conhecimento destilado: glossário de métricas, notas sobre cada empresa, decisões de parsing
output/    o que o projeto entrega (diffs em .md/.html/.csv) — gerado, não escrito à mão
src/       código Python
tests/     testes (pytest)
docs/      STATUS.md (handoff entre chats), DECISOES.md, ROTEAMENTO.md
```

Comece toda sessão lendo `docs/STATUS.md`. Termine toda sessão atualizando ele.

## 4 regras de trabalho

1. **Pense antes de codar.** Diga as premissas em voz alta. Se o pedido for ambíguo, pergunte — não escolha em silêncio.
2. **Simples primeiro.** O mínimo de código que resolve. Nada de abstração, config ou feature "pra depois" que ninguém pediu.
3. **Mudança cirúrgica.** Toque só no que o pedido exige. Não reformate, renomeie ou "melhore" código vizinho.
4. **Defina o "pronto" e verifique.** Antes de começar, escreva como vamos saber que funcionou (um teste, um número conferido). Só diga "terminei" depois de rodar a verificação.

## Regra dos números (inegociável)

Projeto financeiro com número errado é projeto morto.

- Todo número extraído de um release carrega a origem: arquivo, página e a linha/tabela de onde veio.
- Nenhum número vai pro `output/` sem passar pela verificação: um segundo agente, que **não participou da extração**, confere cada valor contra o PDF original e marca ✅ / ❌.
- Divergência de unidade (R$ mil × R$ milhões), período (3T × 9M) ou critério (ajustado × contábil) conta como erro, não como detalhe.
- Na dúvida, o número sai como "não verificado" — nunca é chutado.

## Stack

- Python 3.11+, PyMuPDF (`import pymupdf`) para PDF, `pydantic` para schemas, `pytest` para testes.
- Dados oficiais antes de scraping: preferir dados abertos da CVM / documentos do RI em PDF a raspar HTML.

## Modelos

Ver `docs/ROTEAMENTO.md` — o que vai pro Haiku/Sonnet e o que fica no Opus.
