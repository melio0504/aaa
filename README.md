## Final Project in Python Programming

Two Pygame projects live in this repo:

1. **Boat Racing** - a head to head race against an AI with paddle based speed control.
2. **Drawing and Paint App** - an Etch a Sketch inspired drawing app with brush, eraser, color picker, and save/load.

Both apps are standalone and run from their own folders.

## Requirements

- Python 3.10+
- pip

Each project has its own `requirements.txt`.

## Boat Racing

**Location:** `boat-racing/`

**Features**

- Fullscreen racing with HUD, round system, and match scoring.
- Human player vs AI opponent.
- Simple paddle mechanics (alternate left/right paddles to build speed).

**Install & Run**

```bash
cd boat-racing
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

**Controls**

- Paddle left: `A` or `Left Arrow`
- Paddle right: `D` or `Right Arrow`
- Start round / continue: `Space` or `Enter`
- Restart round: `R`
- Quit: `Esc`

## Drawing and Paint App

**Location:** `drawing-and-paint-app/`

**Features**

- Grid based drawing canvas with brush size control.
- Eraser mode and right mouse button erase.
- Color picker with custom colors.
- Save and load drawings (PNG).
- Shake to clear the canvas with undo support.

**Install & Run**

```bash
cd drawing-and-paint-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

**Controls**

- Draw: Left mouse or arrow keys / WASD
- Erase: `X` toggle or right mouse button
- Brush mode: `B`
- Color picker: `C`
- Save: `P`
- Load: `L`
- Undo: `Ctrl+Z`
- Brush size: `[` and `]` (hold `Shift` to jump)
- Shake to clear: `R`
- Quit: `Esc`
