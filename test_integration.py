#!/usr/bin/env python3
"""
Test script to verify title screen integration with main game
"""

import sys
import cv2

def test_title_screen():
    """Test just the title screen functionality"""
    print("Testing title screen...")
    from title_screen import TitleScreen
    
    title_screen = TitleScreen()
    difficulty = title_screen.show()
    
    print(f"Title screen returned: {difficulty}")
    return difficulty

def test_camera_after_title():
    """Test that camera works after title screen"""
    print("Testing camera after title screen...")
    
    # Test title screen
    difficulty = test_title_screen()
    
    if difficulty == "quit":
        print("User quit, exiting test")
        return
    
    # Test camera initialization
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Camera not available after title screen!")
        return False
    
    print("Camera is working after title screen!")
    
    # Test a few frames
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"Frame {i+1}: {frame.shape}")
        else:
            print(f"Frame {i+1}: Failed to read")
    
    cap.release()
    cv2.destroyAllWindows()
    print("Camera test completed successfully!")
    return True

if __name__ == "__main__":
    print("🧪 Testing Wizard Fight Integration 🧪")
    print("=" * 40)
    
    try:
        test_camera_after_title()
        print("\n✅ Integration test completed successfully!")
        print("You can now run the full game with: python3 launch_game.py")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc() 