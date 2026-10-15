# Embraer (EMBJ3) — notas sobre os releases

Fonte: Central de Resultados, ri.embraer.com.br. Release em PT, ~26 páginas, InDesign, camada de texto limpa.

## Estrutura (1T26)
- Narrativa nas pp. 3–12 (Destaques → Mercado de Capitais); depois, demonstrações financeiras.
- Guidance anual ("Estimativas 2026") aparece duas vezes: em Destaques (p. 3) e na seção própria (p. 4, texto + tabela de 5 linhas). O texto corrido tem todos os números da tabela.

## Armadilhas para a validação (`src/validate.py`)
- **Separador decimal inconsistente no próprio PDF:** p. 4 do 1T26, margem EBIT ajustada do 1T25 aparece como `5.6%` (ponto), enquanto o resto do documento usa vírgula (`6,4%`) e ponto como milhar (`1.248,7`). Conferido na página renderizada: o erro é da Embraer, não da extração. A normalização de números precisa aceitar isso sem confundir com separador de milhar.
- **Hífen invisível (U+00AD):** palavras hifenizadas na quebra de linha vêm com soft hyphen (`indi­cado`). Remover U+00AD dos dois lados antes de comparar citações.
- Rótulos de gráfico (ex.: `44 aeronaves`, `18%` na p. 3) ficam como blocos soltos entre parágrafos. Não atrapalham citações de frases, mas um número solto desses não serve de evidência.
