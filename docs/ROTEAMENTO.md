# ROTEAMENTO — qual modelo faz o quê

Regra geral: **o Opus decide e confere; Sonnet/Haiku executam tarefa fechada.** Tarefa fechada = entrada clara, saída com formato definido, critério de "pronto" objetivo.

| Tarefa | Modelo | Por quê |
|---|---|---|
| Arquitetura, decidir abordagem, revisar diff final | Opus | julgamento; erro aqui custa caro |
| Verificar números contra o PDF | Opus (agente separado) | é a etapa que protege o projeto |
| Escrever código de uma função já especificada | Sonnet | tarefa fechada |
| Escrever testes a partir de exemplos dados | Sonnet | tarefa fechada |
| Extrair tabelas de um PDF para CSV | Sonnet | mecânico, mas precisa de cuidado |
| README, docstrings, comentários | Sonnet | texto com molde |
| Buscar/listar arquivos, renomear, formatar | Haiku | trivial |
| Resumir um documento longo pra contexto | Haiku/Sonnet | leitura, não decisão |

## Dois jeitos de delegar

1. **Automático (preferido):** dentro do chat gestor, o Opus dispara um subagente com Sonnet/Haiku, recebe o resultado e confere. Você não copia nada.
2. **Manual:** abre um chat novo no projeto com Sonnet e cola o pedido abaixo. Quando terminar, ele escreve o resultado no `docs/STATUS.md` (ou você cola a resposta de volta no chat gestor).

### Molde de pedido para um chat Sonnet

```
Leia CLAUDE.md e docs/STATUS.md.
Tarefa: <uma frase>
Entrada: <arquivos>
Saída esperada: <formato exato, onde salvar>
Pronto quando: <critério objetivo — ex.: pytest passa / CSV com N linhas>
Não faça: <o que está fora do escopo>
Ao terminar, adicione uma linha ao Log do docs/STATUS.md.
```

## Economia de token — hábitos

- Plan mode antes de codar qualquer coisa com mais de um arquivo.
- Effort baixo em tarefa trivial; alto só em decisão e verificação.
- Chat novo por tarefa; o contexto vive nos arquivos (CLAUDE.md, STATUS.md), não no histórico do chat.
- Não colar PDF inteiro no chat: deixar em `raw/` e pedir só a página/tabela.
