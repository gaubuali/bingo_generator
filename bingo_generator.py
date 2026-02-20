#!/usr/bin/env python3
"""
Bingo Card Generator  —  ink-saving print version
===================================================
- White background throughout (no solid colour fills)
- Blue outlines and text only (minimal ink)
- BINGO header: white cells with blue border + blue text
- Caller sheet: outlined box, no filled banner
- 2 cards per A4 page; lone card centred & enlarged
- Caller's reference sheet on the last page

Requirements:  pip install matplotlib
"""

import random
import math
import matplotlib
matplotlib.rcParams.update({
    'figure.facecolor':  'white',
    'axes.facecolor':    'white',
    'savefig.facecolor': 'white',
})
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

H_CLR    = "#1565C0"   # deep blue  (borders / text)
T_CLR    = "#1A237E"   # navy       (numbers)
FREE_CLR = "#FFF9C4"   # pale amber (FREE cell — very light, saves ink)


def grid_dims(n: int) -> tuple:
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    return rows, cols


def build_grid(numbers: list, rows: int, cols: int, free_center: bool) -> list:
    nums = numbers[:]
    random.shuffle(nums)
    grid = [[""] * cols for _ in range(rows)]
    cr, cc, idx = rows // 2, cols // 2, 0
    for r in range(rows):
        for c in range(cols):
            if free_center and rows == cols and r == cr and c == cc:
                grid[r][c] = "FREE"
            elif idx < len(nums):
                grid[r][c] = str(nums[idx]); idx += 1
    return grid


def draw_card_ax(ax, grid: list, rows: int, cols: int,
                 title: str, bingo_header: bool, font_scale: float = 1.0):
    extra = 1 if bingo_header else 0
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows + extra)
    ax.set_facecolor("white")
    ax.axis("off")
    ax.set_title(title, fontsize=13 * font_scale, fontweight="bold", color=T_CLR, pad=8)

    # BINGO header — white fill, blue border, blue text (no ink-heavy fill)
    if bingo_header:
        for j, lbl in enumerate("BINGO"):
            ax.add_patch(patches.Rectangle(
                (j, rows), 1, 1,
                facecolor="white", edgecolor=H_CLR, linewidth=2.5))
            ax.text(j + 0.5, rows + 0.5, lbl, ha="center", va="center",
                    fontsize=22 * font_scale, fontweight="bold", color=H_CLR)

    # Number cells
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]; ry = rows - 1 - r
            fc  = FREE_CLR if val == "FREE" else "white"
            ax.add_patch(patches.Rectangle(
                (c, ry), 1, 1, facecolor=fc, edgecolor=H_CLR, linewidth=1.5))
            if val:
                fs = 10 * font_scale if val == "FREE" else 20 * font_scale
                ax.text(c + 0.5, ry + 0.5, val, ha="center", va="center",
                        fontsize=fs, fontweight="bold", color=T_CLR)


def draw_caller_ax(ax, start: int, end: int):
    nums    = list(range(start, end + 1))
    cols_cs = 10
    rows_cs = math.ceil(len(nums) / cols_cs)
    ax.set_xlim(0, cols_cs)
    ax.set_ylim(0, rows_cs + 2.2)
    ax.set_facecolor("white")
    ax.axis("off")

    # Outlined banner — no solid fill
    ax.add_patch(patches.FancyBboxPatch(
        (0, rows_cs + 0.3), cols_cs, 1.7,
        boxstyle="round,pad=0.1",
        facecolor="white", edgecolor=H_CLR, linewidth=2))
    ax.text(cols_cs / 2, rows_cs + 1.15, "CALLER'S REFERENCE SHEET",
            ha="center", va="center", fontsize=16, fontweight="bold", color=H_CLR)
    ax.text(cols_cs / 2, rows_cs + 0.55,
            f"Numbers {start}\u2013{end}  \u00b7  Cross off each number as you call it",
            ha="center", va="center", fontsize=9, color=T_CLR)

    for idx, num in enumerate(nums):
        r = idx // cols_cs; c = idx % cols_cs; ry = rows_cs - 1 - r
        ax.add_patch(patches.Rectangle(
            (c, ry), 1, 1, facecolor="white", edgecolor=H_CLR, linewidth=0.7))
        ax.text(c + 0.5, ry + 0.5, str(num), ha="center", va="center",
                fontsize=13, fontweight="bold", color=T_CLR)


def generate_pdf(start: int, end: int, count: int,
                 num_cards: int, free_center: bool, output_file: str):
    rows, cols   = grid_dims(count)
    bingo_header = (cols == 5)
    FW, FH       = 8.27, 11.69   # A4 inches
    pages = [list(range(num_cards))[i:i + 2] for i in range(0, num_cards, 2)]

    with PdfPages(output_file) as pdf:
        for page_cards in pages:
            fig = plt.figure(figsize=(FW, FH))
            fig.patch.set_facecolor("white")

            if len(page_cards) == 2:
                for slot, card_idx in enumerate(page_cards):
                    yb = 0.54 if slot == 0 else 0.06
                    ax = fig.add_axes([0.06, yb, 0.88, 0.40])
                    chosen = random.sample(range(start, end + 1), count)
                    g = build_grid(chosen, rows, cols, free_center)
                    draw_card_ax(ax, g, rows, cols,
                                 f"\u2726  BINGO  \u00b7  Card #{card_idx + 1}  \u2726",
                                 bingo_header, font_scale=1.0)
                fig.add_artist(plt.Line2D(
                    [0.05, 0.95], [0.52, 0.52],
                    transform=fig.transFigure,
                    color="#aaaaaa", lw=1.5, linestyle="--"))
                fig.text(0.5, 0.518, "\u2702  cut here  \u2702",
                         ha="center", va="top", fontsize=8, color="#999999")
            else:
                ax = fig.add_axes([0.06, 0.25, 0.88, 0.50])
                card_idx = page_cards[0]
                chosen = random.sample(range(start, end + 1), count)
                g = build_grid(chosen, rows, cols, free_center)
                draw_card_ax(ax, g, rows, cols,
                             f"\u2726  BINGO  \u00b7  Card #{card_idx + 1}  \u2726",
                             bingo_header, font_scale=1.4)

            pdf.savefig(fig, bbox_inches="tight", facecolor="white"); plt.close(fig)

        # Caller sheet
        cf = plt.figure(figsize=(FW, FH)); cf.patch.set_facecolor("white")
        cax = cf.add_axes([0.04, 0.04, 0.92, 0.90])
        draw_caller_ax(cax, start, end)
        pdf.savefig(cf, bbox_inches="tight", facecolor="white"); plt.close(cf)

    print(f"\n  PDF saved  \u2192  '{output_file}'")
    print(f"  Cards: {num_cards}  |  Numbers per card: {count}")
    print(f"  Grid:  {rows} rows x {cols} cols  |  BINGO header: {bingo_header}")
    print(f"  Pages: {math.ceil(num_cards / 2)} card page(s) + 1 caller page\n")


def get_inputs():
    print()
    print("=" * 54)
    print("   \U0001f3b1   BINGO CARD GENERATOR  \u00b7  Printable PDF   \U0001f3b1")
    print("=" * 54)
    print()

    while True:
        try:
            start = int(input("  Number range  START  (e.g. 1)   : "))
            end   = int(input("  Number range  END    (e.g. 100) : "))
            if start < end: break
            print("  \u274c  Start must be less than End.\n")
        except ValueError:
            print("  \u274c  Integers only.\n")

    max_n = end - start + 1
    while True:
        try:
            count = int(input(f"  Numbers per card     (1\u2013{max_n})  : "))
            if 1 <= count <= max_n: break
            print(f"  \u274c  Must be 1\u2013{max_n}.\n")
        except ValueError:
            print("  \u274c  Integer only.\n")

    rows, cols = grid_dims(count)
    free_center = False
    if rows == cols:
        fc = input(f"  FREE center cell? (grid {rows}\u00d7{cols})  [y/n]: ").strip().lower()
        if fc == "y":
            free_center = True
            count = rows * cols - 1
            print(f"  \u2139\ufe0f   Adjusted to {count} numbers + 1 FREE center cell.")

    while True:
        try:
            num_cards = int(input("  How many cards to generate?      : "))
            if num_cards >= 1: break
            print("  \u274c  At least 1.\n")
        except ValueError:
            print("  \u274c  Integer only.\n")

    fname = input("  Output filename  [bingo.pdf]      : ").strip() or "bingo.pdf"
    if not fname.endswith(".pdf"):
        fname += ".pdf"
    return start, end, count, num_cards, free_center, fname


if __name__ == "__main__":
    start, end, count, num_cards, free_center, fname = get_inputs()
    rows, cols = grid_dims(count)
    print(f"\n  Generating {num_cards} card(s)  \u00b7  {count} numbers  \u00b7  Grid {rows}\u00d7{cols} ...")
    generate_pdf(start, end, count, num_cards, free_center, fname)
    print(f"  \U0001f5a8\ufe0f   Open '{fname}' and print  \u2014  Enjoy!\n")
