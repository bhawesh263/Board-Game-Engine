# Board Game Engine

A simple race-to-the-finish board game simulation for 2-4 players built in Python. The first player to pass field 30 wins. You can see and control the game through a clean 2D interface using Matplotlib.

## Screenshot

![Board Game Engine in action]
  <img width="320" height="179" alt="screenshot png " src="https://github.com/user-attachments/assets/3cf34730-34a1-4bcf-b511-dc2e380c6f31" />

## Features
- Interactive 2D board visualization
- Special fields distributed randomly every game (Bonus fields like +2 moves, and Trap fields like -2 moves or skipping turns)
- Play with up to 4 players
- Auto-play mode to watch the game unfold

## Project Structure
Board-Game-Engine/
├── main.py              # Entry point
├── requirements.txt     # Python dependencies
├── tests/              
├── README.md
└── screenshot.png


## What This Project Demonstrates

- **Object-oriented design** — modeling a board game as classes (board, players, fields)
- **Game state management** — tracking turns, positions, and special-field effects
- **2D visualization** — rendering the game state with Matplotlib
- **Unit testing** — automated tests with pytest covering core game logic
- **Random event handling** — bonus and trap fields generated each game



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
