#!/usr/bin/env python3
"""
Test script for spell effects (Fire, Water, Earth)
"""

import cv2
import time

def test_spell_effects():
    """Test the spell effects for all spell types"""
    print("🔥 Testing Spell Effects 🔥")
    print("=" * 40)
    
    # Initialize camera
    print("1. Initializing camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open camera!")
        return
    
    print("✅ Camera initialized successfully!")
    
    # Initialize game display
    print("2. Initializing game display...")
    from game_display import GameDisplay
    
    game_display = GameDisplay(frame_width=1920, frame_height=1080)
    print("✅ Game display initialized!")
    
    # Test each spell type
    spells = ["FIRE", "WATER", "EARTH"]
    
    for i, spell in enumerate(spells):
        print(f"\n3.{i+1} Testing {spell} spell effects...")
        print(f"   - Mage casting {spell}")
        print(f"   - Player casting {spell}")
        print(f"   - Press any key to continue...")
        
        # Start attack animation for mage
        game_display.start_attack_animation(3.0)
        
        start_time = time.time()
        while time.time() - start_time < 3.0:  # Test each spell for 3 seconds
            ret, img = cap.read()
            if ret:
                # Create display with both mage and player casting the same spell
                display = game_display.create_game_display(
                    camera_frame=img,
                    mage_spell=spell,  # Mage is casting
                    player_spell=spell,  # Player is also casting
                    countdown=2.0,
                    player_hp=100,
                    mage_hp=90,
                    round_num=i+1
                )
                
                cv2.imshow(f"Test - {spell} Spell Effects", display)
                
                key = cv2.waitKey(30) & 0xFF
                if key != -1:  # Any key pressed
                    print(f"   ✅ Key pressed, moving to next spell...")
                    break
        
        # Return to idle between spells
        game_display.return_to_idle()
        time.sleep(0.5)  # Brief pause
    
    # Cleanup
    cap.release()
    game_display.cleanup()
    cv2.destroyAllWindows()
    
    print("\n✅ Spell effects test completed!")
    print("🔥 Fire: Red/orange particles with glow")
    print("💧 Water: Blue droplets with sparkles")
    print("🌍 Earth: Brown/gray rock particles")

if __name__ == "__main__":
    test_spell_effects() 