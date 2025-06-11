#!/usr/bin/env python3
"""
Wizard Fight Game Launcher
This script launches the wizard fight game with the title screen.
"""

import sys
import os

def main():
    print("🎮 Welcome to Wizard Fight! 🎮")
    print("Loading game...")
    
    try:
        # Import and run the main game
        import wizard_duel_game
        
        # The game will automatically show the title screen first
        # and then proceed with the selected difficulty
        
    except ImportError as e:
        print(f"Error: Could not import required modules: {e}")
        print("Make sure all required packages are installed:")
        print("pip install opencv-python mediapipe numpy")
        return 1
    except Exception as e:
        print(f"Error running game: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 