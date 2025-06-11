#!/usr/bin/env python3
"""
Simple test to verify the main game loop with attack and idle cycling
"""

import cv2
import time

def test_game_loop():
    """Test the main game loop with attack and idle cycling"""
    print("🎮 Testing Game Loop with Attack/Idle Cycling 🎮")
    print("=" * 50)
    
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
    
    # Simulate 3 rounds of the game
    for round_num in range(1, 4):
        print(f"\n--- ROUND {round_num} ---")
        
        # Simulate mage casting a spell
        mage_spell = "FIRE" if round_num == 1 else "WATER" if round_num == 2 else "EARTH"
        print(f"Mage casts: {mage_spell}")
        
        # Start attack animation
        reaction_time = 2.5
        game_display.start_attack_animation(reaction_time)
        print(f"Attack animation started for {reaction_time}s")
        
        # Attack phase
        start_time = time.time()
        while time.time() - start_time < reaction_time:
            ret, img = cap.read()
            if ret:
                remaining_time = reaction_time - (time.time() - start_time)
                
                display = game_display.create_game_display(
                    camera_frame=img,
                    mage_spell=mage_spell,
                    player_spell="WATER",
                    countdown=remaining_time,
                    player_hp=100,
                    mage_hp=90,
                    round_num=round_num
                )
                
                cv2.imshow(f"Round {round_num} - Attack", display)
                
                # Print animation state
                if game_display.current_animation == "attack":
                    print(f"  Attack phase: {remaining_time:.1f}s remaining")
                else:
                    print(f"  Unexpected: {game_display.current_animation}")
                
                if cv2.waitKey(8) & 0xFF == ord('q'):
                    cap.release()
                    game_display.cleanup()
                    cv2.destroyAllWindows()
                    return
        
        # Return to idle
        print("Returning to idle...")
        game_display.return_to_idle()
        
        # Idle phase
        idle_start_time = time.time()
        idle_duration = 1.5
        
        while time.time() - idle_start_time < idle_duration:
            ret, img = cap.read()
            if ret:
                display = game_display.create_game_display(
                    camera_frame=img,
                    player_hp=100,
                    mage_hp=90,
                    round_num=round_num
                )
                
                cv2.imshow(f"Round {round_num} - Idle", display)
                
                # Print animation state
                if game_display.current_animation == "idle":
                    print(f"  Idle phase: {idle_duration - (time.time() - idle_start_time):.1f}s remaining")
                else:
                    print(f"  Unexpected: {game_display.current_animation}")
                
                if cv2.waitKey(8) & 0xFF == ord('q'):
                    cap.release()
                    game_display.cleanup()
                    cv2.destroyAllWindows()
                    return
        
        print(f"Round {round_num} completed!")
    
    # Cleanup
    cap.release()
    game_display.cleanup()
    cv2.destroyAllWindows()
    
    print("\n✅ Game loop test completed successfully!")

if __name__ == "__main__":
    test_game_loop() 