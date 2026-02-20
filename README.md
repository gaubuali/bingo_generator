# Bingo Card Generator + Voice Caller

A small **Python** app to play bingo at home with family and friends.  
It is also great for kids to **learn numbers** in a fun and interactive way, since they see the numbers on their cards and hear them spoken by the caller.

- Generates printable A4 PDF bingo cards (2 cards per page) with a caller’s reference sheet.
- Lets you configure number range, numbers per card, and optional FREE center for square grids.
- Includes a natural-sounding neural voice caller (edge-tts) with configurable pace and classic UK bingo phrases.
- You can use the generated cards on paper, while the app acts as the number caller for the game.


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
