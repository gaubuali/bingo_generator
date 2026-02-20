# Bingo Card Generator

Generates **printable A4 PDF bingo cards** — 2 cards per page plus a caller's sheet.

## Requirements
```
pip install matplotlib
```

## Run
```
python bingo_generator.py
```

## Prompts
| Prompt | Example |
|---|---|
| Range START | `1` |
| Range END | `100` |
| Numbers per card | `20` |
| FREE center? | `y` / `n` (only for square grids) |
| Cards to generate | `8` |
| Output filename | `family_bingo.pdf` |

## Auto Grid Sizing
| Numbers per card | Grid |
|---|---|
| 20 | 4 × 5 (+ BINGO header) |
| 24 + FREE | 5 × 5 (+ BINGO header) |
| 16 | 4 × 4 |
| 9  | 3 × 3 |

## Output
- **Card pages**: 2 bingo cards per A4 page, ready to cut
- **Last page**: Caller's reference sheet (all numbers in the range)
