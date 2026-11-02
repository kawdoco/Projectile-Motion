# Projectile Motion Simulator

A projectile motion simulator written in Python. You give it a launch speed, angle and height, pick how much air resistance there is, and it works out the full flight path step by step. You can run it in a pygame window with sliders and playback controls, or in the terminal if you just want the numbers.

It was built as an OOP project, so the code is split into small classes (physics, drag models, UI, visualizer) instead of one big script.

## What it does

- Simulates a projectile with or without air resistance (quadratic drag)
- Gives you max height, range and flight time for every run
- Has drag presets for a basketball, a golf ball and a cannonball
- Lets you change gravity, so you can try Moon or Mars style launches
- Animates the flight with a speed-coloured trail, a ground shadow and live stats
- Playback controls: play/pause, restart, 0.25x to 4x speed and a timeline you can drag
- Saves the current view as a PNG, or the whole flight as a GIF
- Also has a plain command line mode

## Requirements

- Python 3.12 (that's what it was written with, newer 3.x should be fine)
- `pygame` for the GUI
- `pillow` for saving GIFs
- `numpy` and `matplotlib` only if you want to use `visualizer_animation.py`

```bash
pip install pygame pillow numpy matplotlib
```

## Running it

```bash
git clone <your-repo-url>
cd Projectile-Motion
python main.py
```

You'll get a prompt:

```
Run as (1) GUI or (2) command line? [1]:
```

Press Enter for the GUI, or type `2` for the terminal version.

### GUI

Set your values in the sidebar and hit **Simulate**.

| Field | Range |
| --- | --- |
| Initial speed | 0 to 100 m/s |
| Launch angle | 0 to 90 degrees |
| Launch height | 0 m and up |
| Gravity | 0.1 to 25 m/s² |
| Mass | 0.01 to 20 kg |
| Drag coefficient | 0 to 1 |

Picking a preset (Basketball, Golf Ball, Cannonball) fills in the mass and drag coefficient for you. If you edit those fields afterwards it switches back to Custom.

Shortcuts: `Space` pauses or resumes, `R` restarts the animation. `Tab` moves between input boxes. These only work while you're not typing in a box.

Saved files (`trajectory.png` and `trajectory.gif`) are written to the folder you ran the program from.

### Command line

The terminal version asks for speed, angle, launch height, gravity and drag coefficient. Press Enter on any question to keep the default shown in brackets. It prints the results and asks if you want to run another one.

## How the physics works

Without drag, the projectile only feels gravity. With drag, the acceleration is

```
a = -(k / m) * |v| * v
```

where `k` is the drag coefficient, `m` is the mass and `v` is the velocity. The simulation steps through time with `dt = 0.001 s`, updating velocity and then position at every step, and stops once the projectile drops below ground level. Max height, range and flight time are all read from that stored path.

Drag presets used by the GUI:

| Preset | Drag coefficient | Mass (kg) |
| --- | --- | --- |
| Basketball | 0.013 | 0.624 |
| Golf ball | 0.00022 | 0.0459 |
| Cannonball | 0.0033 | 5.4 |

## Project structure

```
Projectile-Motion/
├── main.py                       # entry point, picks GUI or CLI
├── projectile_physics_engine.py  # drag models and the simulation itself
├── gui.py                        # pygame interface
├── ui.py                         # terminal input and output
└── visualizer_animation.py       # matplotlib plots and animation
```

`visualizer_animation.py` is separate from the pygame GUI. It uses matplotlib to draw a static trajectory graph or an animated one. You can try it with:

```bash
python visualizer_animation.py
```

That saves `static_preview.png` in the current folder.

## OOP concepts used

- **Abstraction:** `DragModel`, `SimulationRunner` and `BaseVisualizer` are abstract base classes
- **Inheritance:** `NoDrag` and `QuadraticDrag` extend `DragModel`, and the ball presets extend `QuadraticDrag`
- **Polymorphism:** every drag model implements `acceleration()`, so the simulation doesn't care which one it's given
- **Encapsulation:** the trajectory data is private inside `ProjectilePhysics` and only exposed through methods

## Contributors

- Add your names and roles here

## License

Add a license here (MIT is a common choice for student projects).
