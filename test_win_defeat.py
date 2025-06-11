#!/usr/bin/env python3
"""
Test script for win/defeat screens
"""

import cv2
import time

def test_win_defeat_screens():
    """Test the win/defeat screens quickly"""
    print("🎮 Testing Win/Defeat Screens 🎮")
    print("=" * 40)
    
    # Initialize camera (needed for game display)
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
    
    # Test defeat screen (player loses, mage wins)
    print("\n3. Testing DEFEAT screen (player loses)...")
    print("   - Should show mageVictory.mkv animation")
    print("   - Press any key to continue...")
    
    game_display.start_victory_animation()
    
    start_time = time.time()
    while time.time() - start_time < 5.0:  # Test for 5 seconds
        ret, img = cap.read()
        if ret:
            defeat_display = game_display.create_win_defeat_screen("player", 0, 50, 8)
            cv2.imshow("Test - DEFEAT Screen", defeat_display)
            
            key = cv2.waitKey(8) & 0xFF
            if key != -1:  # Any key pressed
                break
    
    # Test victory screen (player wins, mage loses)
    print("\n4. Testing VICTORY screen (player wins)...")
    print("   - Should show mageDefeat.mkv animation")
    print("   - Press any key to continue...")
    
    game_display.start_defeat_animation()
    
    start_time = time.time()
    while time.time() - start_time < 5.0:  # Test for 5 seconds
        ret, img = cap.read()
        if ret:
            victory_display = game_display.create_win_defeat_screen("mage", 80, 0, 12)
            cv2.imshow("Test - VICTORY Screen", victory_display)
            
            key = cv2.waitKey(8) & 0xFF
            if key != -1:  # Any key pressed
                break
    
    # Test restart functionality
    print("\n5. Testing restart functionality...")
    print("   - Press ENTER to simulate restart")
    print("   - Press Q to quit")
    
    while True:
        ret, img = cap.read()
        if ret:
            victory_display = game_display.create_win_defeat_screen("mage", 80, 0, 12)
            cv2.imshow("Test - Restart Functionality", victory_display)
            
            key = cv2.waitKey(8) & 0xFF
            if key == 13:  # Enter key
                print("   ✅ Restart detected!")
                game_display.return_to_idle()
                break
            elif key == ord('q'):  # Q key
                print("   ✅ Quit detected!")
                break
    
    # Cleanup
    cap.release()
    game_display.cleanup()
    cv2.destroyAllWindows()
    
    print("\n✅ Win/Defeat screen test completed!")

if __name__ == "__main__":
    test_win_defeat_screens() 