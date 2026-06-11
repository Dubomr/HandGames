# Hand-Controlled Mini Games

A computer vision based mini-game project developed with Python, OpenCV, MediaPipe, and Pygame.

This project allows players to control games using hand gestures captured through a webcam instead of using a traditional mouse or keyboard.

## Features

- Real-time hand tracking using MediaPipe
- Webcam integration with OpenCV
- Interactive menu controlled by hand movements
- Smooth cursor movement based on finger tracking
- Multiple mini-games in a single application
- Sound effects and game UI
- Pause and game over menus

---

## Technologies Used

- Python
- OpenCV
- MediaPipe
- Pygame
- NumPy

---

## Games Included

### 1. Fruit Ninja
- Slice fruits using hand movements.
- Score points by cutting fruits.
- Avoid missing too many fruits.

### 2. Pong (2-Hand Control)
- Classic Pong game controlled with hand tracking.
- One hand controls the left paddle and the other controls the right paddle.
- Includes power-ups:
  - Bigger Ball
  - Faster Ball
  - Wider Paddles

### 3. AI Dodge
- Dodge incoming obstacles using hand movements.
- Uses hand landmark data captured by MediaPipe.

---

## How It Works

The webcam captures video frames using OpenCV.

MediaPipe detects hand landmarks in real time and tracks finger positions.

The tracked hand coordinates are converted into game coordinates and used to control the cursor or game objects inside the Pygame window.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Dubomr/HandGames.git
cd HandGames
```

### 2. Create a Virtual Environment

Windows:

```bash
py -3.11 -m venv venv
```

### 3. Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

## Common Issues

### PowerShell Execution Policy Error

If you get an error similar to:

```text
running scripts is disabled on this system
```

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then try again:

```powershell
venv\Scripts\activate
```

If activation is successful, you should see `(venv)` at the beginning of your terminal line.

### 4. Install Required Libraries

```bash
pip install -r requirements.txt
```

## Running the Project

Run the main file:

```bash
python main.py
```
