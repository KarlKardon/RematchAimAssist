# Rematch Aim Assist

An external **aim‑assist overlay** for Rematch, using OpenCV to detect teammate blips on the minimap and display a directional arrow.

**This is for proof of concept only, using this in matchmaking makes you a noob loser who may get banned**

<img width="1507" height="1160" alt="image" src="https://github.com/user-attachments/assets/d228a255-f009-4c7d-929e-51db4fee8f17" />


## Features

- Real‑time capture and processing of the Rematch minimap  
- HSV‑based detection of teammate positions  
- Calculation of pass/shoot direction  
- On‑screen arrow overlay indicating where to point your joystick

## Prerequisites

- **Windows 10/11** (64‑bit)  
- **Python 3.8+**  
- **Microsoft PowerToys** (for “Always on Top” window pinning)
   - Not fully required but any clicking on the REMATCH window will make the overlay go behind the REMATCH window if you do not pin the window   
- Python packages listed in `requirements.txt`

## Installation

1. Clone this repository:  
   ```bash
   git clone https://github.com/YourUser/rematch-overlay.git
   cd rematch-overlay
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
3. Install dependencies:
   ```bash
   pip install -r requirements.txt

## Usage

1. Launch Rematch in Windowed (Borderless) mode.
2. Run the script
3. Pin the overlay window above the game (place near player's feet):
   - Focus the window titled Overlay
   - Press Win + Ctrl + T (PowerToys “Always on Top”)
   - The arrow will remain visible over your game.

## Configuration

- Modify the X, Y coordinates in ScreenCap.py to reposition the overlay window.
- Modify upper and lower hsv variables to fit your team color **(Microsoft PowerToys actually has a color picker macro to find this quite easily: Windows Key + Shift + C)**
