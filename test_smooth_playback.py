#!/usr/bin/env python3
"""
Test script for smooth video playback and full attack animation duration
"""

import cv2
import time

def test_smooth_playback():
    """Test smooth video playback and attack animation duration"""
    print("🧪 Testing Smooth Video Playback 🧪")
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
    
    # Test smooth idle animation
    print("3. Testing smooth idle animation (3 seconds)...")
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 3:
        ret, img = cap.read()
        if ret:
            display = game_display.create_game_display(
                camera_frame=img,
                player_hp=100,
                mage_hp=100,
                round_num=1
            )
            cv2.imshow("Test - Smooth Idle", display)
            frame_count += 1
            
            # Use consistent 30 FPS timing
            if cv2.waitKey(33) & 0xFF == ord('q'):  # ~30 FPS
                break
    
    fps = frame_count / (time.time() - start_time)
    print(f"   - Average FPS: {fps:.1f}")
    print(f"   - Frame count: {frame_count}")
    
    # Test attack animation with full duration
    print("4. Testing attack animation with full duration...")
    game_display.start_attack_animation()
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < game_display.attack_duration + 1:  # Extra second for safety
        ret, img = cap.read()
        if ret:
            display = game_display.create_game_display(
                camera_frame=img,
                mage_spell="FIRE",
                player_spell="WATER",
                countdown=2.5,
                player_hp=90,
                mage_hp=80,
                round_num=2
            )
            cv2.imshow("Test - Full Attack Animation", display)
            frame_count += 1
            
            # Use consistent 30 FPS timing
            if cv2.waitKey(33) & 0xFF == ord('q'):  # ~30 FPS
                break
    
    attack_fps = frame_count / (time.time() - start_time)
    print(f"   - Attack animation duration: {game_display.attack_duration:.2f} seconds")
    print(f"   - Attack FPS: {attack_fps:.1f}")
    print(f"   - Attack frame count: {frame_count}")
    
    # Test transition back to idle
    print("5. Testing transition back to idle...")
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 2:
        ret, img = cap.read()
        if ret:
            display = game_display.create_game_display(
                camera_frame=img,
                player_hp=85,
                mage_hp=75,
                round_num=3
            )
            cv2.imshow("Test - Back to Idle", display)
            frame_count += 1
            
            # Use consistent 30 FPS timing
            if cv2.waitKey(33) & 0xFF == ord('q'):  # ~30 FPS
                break
    
    transition_fps = frame_count / (time.time() - start_time)
    print(f"   - Transition FPS: {transition_fps:.1f}")
    
    # Cleanup
    cap.release()
    game_display.cleanup()
    cv2.destroyAllWindows()
    
    print("✅ Smooth playback test completed!")
    print(f"📊 Performance Summary:")
    print(f"   - Idle FPS: {fps:.1f}")
    print(f"   - Attack FPS: {attack_fps:.1f}")
    print(f"   - Transition FPS: {transition_fps:.1f}")
    print(f"   - Attack duration: {game_display.attack_duration:.2f} seconds")
    
    if fps > 25 and attack_fps > 25 and transition_fps > 25:
        print("🎉 All tests passed! Smooth playback achieved!")
    else:
        print("⚠️  Some performance issues detected. Consider optimizing.")

if __name__ == "__main__":
    test_smooth_playback() 