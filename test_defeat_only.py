#!/usr/bin/env python3
"""
Test script for DEFEAT screen only (player loses)
"""

import cv2
import time
import os
import numpy as np

def test_defeat_screen():
    """Test only the defeat screen (player loses)"""
    print("💀 Testing DEFEAT Screen Only 💀")
    print("=" * 40)
    
    # Check if video files exist
    print("0. Checking video files...")
    video_files = ["mageVictory.mkv", "mageDefeat.mkv"]
    for video_file in video_files:
        if os.path.exists(video_file):
            print(f"   ✅ {video_file} exists")
        else:
            print(f"   ❌ {video_file} NOT FOUND!")
            return
    
    # Initialize camera
    print("\n1. Initializing camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open camera!")
        return
    
    print("✅ Camera initialized successfully!")
    
    # Initialize game display
    print("\n2. Initializing game display...")
    from game_display import GameDisplay
    
    game_display = GameDisplay(frame_width=1920, frame_height=1080)
    print("✅ Game display initialized!")
    
    # Test defeat screen (player loses, mage wins)
    print("\n3. Testing DEFEAT screen (player loses)...")
    print("   - Should show mageVictory.mkv animation")
    print("   - Should display 'DEFEAT' in red")
    
    # Set the victory animation (mage wins)
    game_display.start_victory_animation()
    
    # Create a simple test window first
    print("\n4. Creating test window...")
    test_img = cv2.imread("test_image.jpg") if os.path.exists("test_image.jpg") else None
    if test_img is None:
        # Create a simple colored image
        test_img = cv2.imread("mageIdle.mkv")  # Try to read video as image (will fail but test window creation)
        if test_img is None:
            # Create a simple colored rectangle
            test_img = np.zeros((480, 640, 3), dtype=np.uint8)
            test_img[:] = (0, 0, 255)  # Red background
            cv2.putText(test_img, "TEST WINDOW", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    window_name = "Test Window - Look for this!"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 640, 480)
    cv2.imshow(window_name, test_img)
    
    print("   🖥️  Test window created!")
    print("   📍 Look for window titled: 'Test Window - Look for this!'")
    print("   ⌨️  Press any key to continue to defeat screen...")
    
    # Wait for key press
    while True:
        key = cv2.waitKey(100) & 0xFF
        if key != -1:
            break
    
    cv2.destroyWindow(window_name)
    
    # Now show the defeat screen
    print("\n5. Showing defeat screen...")
    defeat_window = "DEFEAT SCREEN - Press any key to exit"
    cv2.namedWindow(defeat_window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(defeat_window, 1280, 720)
    
    start_time = time.time()
    while time.time() - start_time < 10.0:
        ret, img = cap.read()
        if ret:
            defeat_display = game_display.create_win_defeat_screen("player", 0, 50, 8)
            cv2.imshow(defeat_window, defeat_display)
            
            key = cv2.waitKey(30) & 0xFF
            if key != -1:
                print("   ✅ Key pressed, ending test...")
                break
    
    # Cleanup
    cap.release()
    game_display.cleanup()
    cv2.destroyAllWindows()
    
    print("\n✅ Defeat screen test completed!")

if __name__ == "__main__":
    test_defeat_screen() 