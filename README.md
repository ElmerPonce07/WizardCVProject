# Wizard Fight - Hand Gesture Magic Duel Game

## Overview

Wizard Fight is an interactive computer vision-based game that allows players to engage in magical duels using hand gestures. Players cast spells by making specific hand gestures that are detected through their computer's webcam using MediaPipe hand tracking technology.

## Features

### Core Gameplay

- **Real-time Hand Gesture Recognition**: Uses MediaPipe to track hand movements and detect finger positions
- **Three Elemental Spells**: Fire, Water, and Earth with rock-paper-scissors mechanics
- **Multiple Difficulty Levels**: Easy (2.5s reaction time), Medium (1.5s), and Hard (0.75s)
- **Dynamic Health System**: Both player and AI mage have 100 HP with damage tracking
- **Round-based Combat**: Turn-based spell casting with reaction time mechanics

### Visual Elements

- **Animated Title Screen**: Interactive menu with difficulty selection
- **Mage Animations**: Idle, attack, victory, and defeat animations using video files
- **Real-time Camera Feed**: Live webcam display with hand tracking visualization
- **Health Bars**: Visual HP tracking for both player and mage
- **Spell Announcements**: Dynamic text display showing current spells and countdown timers

### Technical Features

- **Cross-platform Compatibility**: Works on Windows, macOS, and Linux
- **High Performance**: Optimized for 120 FPS display
- **Modular Architecture**: Clean separation of core logic, UI, and game mechanics
- **Error Handling**: Graceful fallbacks for missing camera or video files

## Installation

### Prerequisites

- Python 3.7 or higher
- Webcam
- Sufficient lighting for hand tracking

### Dependencies

Install the required packages using pip:

```bash
pip install opencv-python mediapipe numpy
```

### Project Setup

1. Clone or download the project
2. Navigate to the project directory
3. Ensure all video assets are in the `assets/` folder:
   - `mageIdle.mkv` - Mage idle animation
   - `MageAttack.mkv` - Mage attack animation
   - `mageDefeat.mkv` - Mage defeat animation (player wins)
   - `mageVictory.mkv` - Mage victory animation (mage wins)

## How to Play

### Launching the Game

```bash
python3 core/launch_game.py
```

### Game Controls

- **W/S Keys**: Navigate difficulty selection in title screen
- **Enter Key**: Confirm selection and start game
- **Q Key**: Quit game at any time
- **Hand Gestures**: Cast spells (see Spell System below)

### Spell System

#### Fire Spell

- **Gesture**: Index and middle fingers up, others down
- **Variations Accepted**:
  - Thumb down, index + middle up
  - Thumb up, index + middle up
  - Thumb down, index + middle + ring up
  - Thumb up, index + middle + ring up
- **Counters**: Water
- **Weak Against**: Earth

#### Water Spell

- **Gesture**: All five fingers extended
- **Counters**: Earth
- **Weak Against**: Fire

#### Earth Spell

- **Gesture**: All fingers closed (fist)
- **Counters**: Fire
- **Weak Against**: Water

### Game Mechanics

#### Round Structure

1. **Spell Announcement**: Mage announces their spell
2. **Reaction Phase**: Player has limited time to cast a counter spell
3. **Resolution**: Spells are compared and damage is calculated
4. **Health Update**: HP is adjusted based on spell effectiveness
5. **Idle Phase**: Brief pause before next round

#### Damage System

- **Successful Counter**: Mage takes 10 damage
- **Failed Counter**: Player takes 10 damage
- **No Spell Cast**: Player takes 10 damage
- **Game Over**: When either player reaches 0 HP

#### Difficulty Levels

- **Easy**: 2.5 seconds to react
- **Medium**: 1.5 seconds to react
- **Hard**: 0.75 seconds to react

## Project Structure

```
WizardCVProject/
├── core/                          # Core game logic and utilities
│   ├── main.py                    # Basic hand tracking demo
│   ├── launch_game.py             # Game launcher script
│   ├── gameLogic.py               # Game mechanics and rules
│   └── gestureUtils.py            # Hand gesture recognition
├── ui/                            # User interface components
│   ├── wizard_duel_game.py        # Main game loop and logic
│   ├── title_screen.py            # Title screen and menu
│   └── game_display.py            # Visual display and animations
├── assets/                        # Video and media files
│   ├── mageIdle.mkv               # Mage idle animation
│   ├── MageAttack.mkv             # Mage attack animation
│   ├── mageDefeat.mkv             # Mage defeat animation
│   └── mageVictory.mkv            # Mage victory animation
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
└── readMe.md                      # This documentation
```

## Technical Architecture

### Core Module (`core/`)

- **gameLogic.py**: Contains spell counters, difficulty settings, and game evaluation logic
- **gestureUtils.py**: Hand landmark processing and spell detection algorithms
- **launch_game.py**: Entry point with proper path handling and error management
- **main.py**: Simple hand tracking demonstration

### UI Module (`ui/`)

- **wizard_duel_game.py**: Main game loop, camera handling, and game state management
- **title_screen.py**: Interactive menu system with difficulty selection
- **game_display.py**: Video animation management and UI rendering

### Key Technologies

- **OpenCV**: Computer vision and video processing
- **MediaPipe**: Hand tracking and landmark detection
- **NumPy**: Numerical operations and array handling

## Hand Tracking System

### Landmark Detection

The game uses MediaPipe's hand tracking to detect 21 hand landmarks:

- **Finger Tips**: Landmarks 4, 8, 12, 16, 20
- **Finger PIP Joints**: Landmarks 3, 7, 11, 15, 19
- **Thumb Special Handling**: Uses X-coordinate comparison for sideways movement

### Gesture Recognition Algorithm

1. **Thumb Detection**: Compares X-coordinates with tolerance for sideways movement
2. **Finger Detection**: Compares Y-coordinates of tips vs PIP joints with tolerance
3. **Spell Mapping**: Maps finger combinations to spell types with multiple acceptable variations

### Tolerance System

- **Thumb Tolerance**: 0.02 units for sideways movement
- **Finger Tolerance**: 0.01 units for vertical movement
- **Multiple Gesture Support**: Accepts variations of the same spell for better reliability

## Performance Optimization

### Frame Rate Management

- **Target FPS**: 120 FPS for smooth animations
- **Frame Timing**: Consistent 8ms intervals between frames
- **Animation Synchronization**: Video playback synchronized with game timing

### Memory Management

- **Video Streaming**: Efficient video file handling with looping
- **Camera Resources**: Proper cleanup of OpenCV camera objects
- **Window Management**: Controlled window creation and destruction

## Troubleshooting

### Common Issues

#### Camera Not Working

- Ensure webcam is connected and not in use by other applications
- Check camera permissions in your operating system
- Try running with `python3 core/main.py` to test basic camera functionality

#### Hand Tracking Issues

- Ensure adequate lighting
- Keep hands clearly visible to the camera
- Avoid rapid hand movements
- Check that MediaPipe is properly installed

#### Video Files Missing

- Ensure all `.mkv` files are in the `assets/` folder
- Check file permissions
- Verify video files are not corrupted

#### Performance Issues

- Close other applications using the camera
- Ensure sufficient system resources
- Try reducing the game window size

### Error Messages

- **"Failed to grab frame"**: Camera access issue
- **"Could not open [video file]"**: Missing or corrupted video assets
- **"Could not import required modules"**: Missing Python dependencies

## Development Notes

### Code Style

- **Modular Design**: Clear separation of concerns between modules
- **Error Handling**: Comprehensive try-catch blocks and fallbacks
- **Documentation**: Inline comments explaining complex logic
- **Consistent Naming**: Descriptive variable and function names

### Extensibility

The project is designed for easy extension:

- **New Spells**: Add to `gestureUtils.py` and `gameLogic.py`
- **New Animations**: Add video files to `assets/` and update `game_display.py`
- **New Difficulty Levels**: Modify `gameLogic.py` difficulty settings
- **New UI Elements**: Extend `game_display.py` display methods

### Future Enhancements

Potential improvements and additions:

- **Multiplayer Support**: Network-based player vs player
- **Custom Gestures**: User-defined spell gestures
- **Sound Effects**: Audio feedback for spells and actions
- **Save System**: Progress tracking and high scores
- **Mobile Support**: Touch-based gesture recognition

## License and Credits

This project demonstrates computer vision and game development concepts using:

- **OpenCV**: Computer vision library
- **MediaPipe**: Hand tracking technology by Google
- **Python**: Programming language and ecosystem

## Support

For issues, questions, or contributions:

1. Check the troubleshooting section above
2. Verify all dependencies are installed correctly
3. Ensure your system meets the minimum requirements
4. Test with the basic hand tracking demo first

---

**Enjoy your magical duels!** 🧙‍♂️⚡
