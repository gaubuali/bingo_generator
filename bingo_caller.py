#!/usr/bin/env python3
"""
Bingo Number Caller
====================
Calls bingo numbers out loud with a natural voice and configurable pace.

Two TTS modes:
  1. edge-tts  (default) — Microsoft Neural voices, very natural, needs internet
  2. pyttsx3   (offline)  — uses Windows built-in SAPI5 voices, works offline

Requirements:
  pip install edge-tts pyttsx3

Usage:
  python bingo_caller.py
"""

import random
import time
import sys
import asyncio
import os
import ctypes
import tempfile

# ── Dependency check ──────────────────────────────────────────────────────────
try:
    import edge_tts
    EDGE_AVAILABLE = True
except ImportError:
    EDGE_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX_AVAILABLE = True
except ImportError:
    PYTTSX_AVAILABLE = False

if not EDGE_AVAILABLE and not PYTTSX_AVAILABLE:
    print("\n  ERROR: No TTS engine found.")
    print("  Install at least one:")
    print("    pip install edge-tts")
    print("    pip install pyttsx3\n")
    sys.exit(1)

# ── edge-tts voices ───────────────────────────────────────────────────────────
EDGE_VOICES = {
    "1": ("en-GB-RyanNeural",    "Ryan (UK Male)   \u2014 recommended"),
    "2": ("en-GB-SoniaNeural",   "Sonia (UK Female)"),
    "3": ("en-US-GuyNeural",     "Guy (US Male)"),
    "4": ("en-US-JennyNeural",   "Jenny (US Female)"),
    "5": ("en-AU-WilliamNeural", "William (AU Male)"),
}

# ── Classic bingo call phrases ────────────────────────────────────────────────
PHRASES = {
    1:  "Kelly's eye, number one",
    2:  "One little duck, two",
    3:  "Cup of tea, three",
    4:  "Knock at the door, four",
    5:  "Man alive, five",
    6:  "Half a dozen, six",
    7:  "Lucky seven",
    8:  "Garden gate, eight",
    9:  "Doctor's orders, nine",
    10: "Prime Minister's den, ten",
    11: "Legs eleven",
    12: "Dozen, twelve",
    13: "Unlucky for some, thirteen",
    14: "Valentine's day, fourteen",
    16: "Sweet sixteen",
    18: "Coming of age, eighteen",
    21: "Key of the door, twenty one",
    22: "Two little ducks, twenty two",
    33: "Dirty knees, thirty three",
    40: "Life begins, forty",
    44: "Droopy drawers, forty four",
    55: "Snakes alive, fifty five",
    60: "Five dozen, sixty",
    66: "Clickety click, sixty six",
    69: "Anyway up, sixty nine",
    77: "Sunset strip, seventy seven",
    88: "Two fat ladies, eighty eight",
    90: "Top of the shop, ninety",
}

# ── Number to words ───────────────────────────────────────────────────────────
_ONES = [
    "zero","one","two","three","four","five","six","seven","eight","nine",
    "ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen",
    "seventeen","eighteen","nineteen"
]
_TENS = ["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]

def _number_to_words(n: int) -> str:
    if n < 20:
        return _ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return (_TENS[t] + (" " + _ONES[o] if o else "")).strip()
    if n < 1000:
        h, r = divmod(n, 100)
        rest = (" and " + _number_to_words(r)) if r else ""
        return _ONES[h] + " hundred" + rest
    return str(n)

def get_phrase(n: int) -> str:
    return str(PHRASES[n]) if n in PHRASES else str(_number_to_words(n))


# ── Windows MCI audio player (no extra dependencies) ─────────────────────────
def _play_mp3_windows(path: str):
    """Play an MP3 file using Windows MCI — handles edge-tts output reliably."""
    mci = ctypes.windll.winmm.mciSendStringW
    alias = "bingo_tts"
    mci(f'open "{path}" type mpegvideo alias {alias}', None, 0, None)
    mci(f'play {alias} wait', None, 0, None)
    mci(f'close {alias}', None, 0, None)


# ── edge-tts engine ───────────────────────────────────────────────────────────
async def _speak_edge_async(text: str, voice: str, rate: str, volume: str):
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
    # Use mkstemp so the file handle is closed before edge-tts writes to it
    fd, tmp = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        await communicate.save(tmp)
        _play_mp3_windows(tmp)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass

def speak_edge(text: str, voice: str, rate_pct: int, volume_pct: int):
    text       = str(text)
    rate_str   = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"
    volume_str = f"+{volume_pct}%" if volume_pct >= 0 else f"{volume_pct}%"
    asyncio.run(_speak_edge_async(text, voice, rate_str, volume_str))


# ── pyttsx3 engine ────────────────────────────────────────────────────────────
def speak_pyttsx(text: str, engine, rate: int):
    engine.setProperty("rate", rate)
    engine.say(str(text))
    engine.runAndWait()


# ── Helpers ───────────────────────────────────────────────────────────────────
def pick_voice_menu() -> tuple:
    if EDGE_AVAILABLE:
        print("\n  Available voices (edge-tts, natural neural):")
        for k, (_, desc) in EDGE_VOICES.items():
            print(f"    [{k}] {desc}")
        if PYTTSX_AVAILABLE:
            print(f"    [6] Windows built-in offline voice")
        choice = input("\n  Choose voice [1]: ").strip() or "1"
        if choice == "6" and PYTTSX_AVAILABLE:
            return None, "pyttsx"
        voice_id = EDGE_VOICES.get(choice, EDGE_VOICES["1"])[0]
        return voice_id, "edge"
    else:
        print("  edge-tts not available \u2014 using offline Windows voice.")
        return None, "pyttsx"

def get_int(prompt: str, default: int, lo: int, hi: int) -> int:
    val = input(prompt).strip()
    if not val:
        return default
    try:
        return max(lo, min(hi, int(val)))
    except ValueError:
        return default

def clear_line():
    print("\r" + " " * 60 + "\r", end="", flush=True)


# ── Main caller loop ──────────────────────────────────────────────────────────
def run_caller():
    print()
    print("=" * 54)
    print("   \U0001F3B1   BINGO NUMBER CALLER")
    print("=" * 54)

    start = get_int("  Range START (default 1)  : ", 1,   1, 999)
    end   = get_int("  Range END   (default 90) : ", 90, start+1, 999)

    voice_id, mode = pick_voice_menu()

    print("\n  Pace \u2014 seconds between each number call")
    print("  Tip: 5s = fast, 10s = relaxed, 15s = slow family game")
    pace = get_int("  Pace in seconds [10]     : ", 10, 1, 60)

    if mode == "edge":
        print("\n  Speaking rate adjustment  (-50 = slow, 0 = normal, +50 = fast)")
        rate   = get_int("  Rate adjustment [0]      : ",   0, -100, 100)
        volume = get_int("  Volume adjustment [0]    : ",   0,  -50,  50)
    else:
        print("\n  Speaking rate (words per minute, default 150)")
        rate   = get_int("  Rate [150]               : ", 150,  50, 400)
        volume = None

    pyttsx_engine = None
    if mode == "pyttsx":
        pyttsx_engine = pyttsx3.init()

    numbers = list(range(start, end + 1))
    random.shuffle(numbers)
    total = len(numbers)

    print(f"\n  Ready! Calling {total} numbers with {pace}s pace.")
    print("  Press ENTER to start, then CTRL+C to stop at any time.\n")
    input("  >> Press ENTER to begin...")
    print()

    called = []
    try:
        for i, n in enumerate(numbers, 1):
            phrase = get_phrase(n)
            called.append(n)
            print(f"  [{i:>3}/{total}]  #{n:>3}  \u2014  {phrase}")

            if mode == "edge":
                speak_edge(phrase, voice_id, rate, volume)
            else:
                speak_pyttsx(phrase, pyttsx_engine, rate)

            if i < total:
                for remaining in range(pace, 0, -1):
                    print(f"          next number in {remaining}s ...   ", end="\r", flush=True)
                    time.sleep(1)
                clear_line()

    except KeyboardInterrupt:
        print("\n\n  Stopped early.")

    print(f"\n  Game over! Called {len(called)}/{total} numbers.")
    uncalled = sorted(set(numbers) - set(called))
    if uncalled:
        print(f"  Uncalled: {uncalled}")
    print()


if __name__ == "__main__":
    run_caller()
