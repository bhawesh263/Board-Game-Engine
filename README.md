# Python Board Game

A simple race-to-the-finish board game simulation for 2-4 players built in Python. The first player to pass field 30 wins. You can see and control the game through a clean 2D interface using Matplotlib.

## Features
- Interactive 2D board visualization
- Special fields distributed randomly every game (Bonus fields like +2 moves, and Trap fields like -2 moves or skipping turns)
- Play with up to 4 players
- Auto-play mode to watch the game unfold

## How to play
First, make sure you install the dependencies:
for mac users
```bash
pip3 install -r requirements.txt
```
for windows users
```bash
pip install -r requirements.txt
```

Then, just run the main file:
for mac users   
```bash
python3 main.py
```
for windows users
```bash
python main.py
```

## Running the tests
If you want to run the unit tests, just use pytest:
for mac users
```bash
python3 -m pytest tests/
```
for windows users 
```bash
python -m pytest tests/
```