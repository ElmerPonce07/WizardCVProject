#!/usr/bin/env python3
"""
Debug script to test attack animation and spell announcement
"""

import cv2
import time

def debug_attack_animation():
    """Debug the attack animation and spell announcement"""
    print("🔍 Debugging Attack Animation 🔍")
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
    
    # Test attack animation with spell announcement
    print("3. Testing attack animation with spell announcement...")
    print("   - Starting attack animation for 2.5 seconds")
    print("   - Spell announcement should be visible")
    
    game_display.start_attack_animation(2.5)  # 2.5 seconds like Easy mode
    start_time = time.time()
    
    while time.time() - start_time < 3.0:  # Test for 3 seconds
        ret, img = cap.read()
        if ret:
            # Create display with spell announcement
            display = game_display.create_game_display(
                camera_frame=img,
                mage_spell="FIRE",  # This should be visible
                player_spell="WATER",
                countdown=2.5 - (time.time() - start_time),
                player_hp=100,
                mage_hp=90,
                round_num=1
            )
            
            cv2.imshow("Debug - Attack Animation", display)
            
            # Check current animation state
            if game_display.current_animation == "attack":
                print(f"   - Animation: ATTACK (elapsed: {time.time() - start_time:.1f}s)")
            else:
                print(f"   - Animation: IDLE (elapsed: {time.time() - start_time:.1f}s)")
            
            if cv2.waitKey(8) & 0xFF == ord('q'):  # ~120 FPS
                break
    
    # Test return to idle
    print("4. Testing return to idle...")
    game_display.return_to_idle()
    
    start_time = time.time()
    while time.time() - start_time < 2.0:  # Test idle for 2 seconds
        ret, img = cap.read()
        if ret:
            display = game_display.create_game_display(
                camera_frame=img,
                player_hp=100,
                mage_hp=90,
                round_num=1
            )
            
            cv2.imshow("Debug - Idle Animation", display)
            
            if game_display.current_animation == "idle":
                print(f"   - Animation: IDLE (elapsed: {time.time() - start_time:.1f}s)")
            else:
                print(f"   - Animation: ATTACK (elapsed: {time.time() - start_time:.1f}s)")
            
            if cv2.waitKey(8) & 0xFF == ord('q'):
                break
    
    # Cleanup
    cap.release()
    game_display.cleanup()
    cv2.destroyAllWindows()
    
    print("✅ Debug test completed!")

if __name__ == "__main__":
    debug_attack_animation() 