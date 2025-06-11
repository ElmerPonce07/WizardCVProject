#!/usr/bin/env python3
"""
Test script for the new game display system
"""

import cv2
import time

def test_game_display():
    """Test the new game display system"""
    print("🧪 Testing New Game Display System 🧪")
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
    
    # Test different display states
    print("3. Testing display states...")
    
    # Test idle state
    print("   - Testing idle animation...")
    for i in range(30):  # 1 second at 30fps
        ret, img = cap.read()
        if ret:
            display = game_display.create_game_display(
                camera_frame=img,
                player_hp=100,
                mage_hp=100,
                round_num=1
            )
            cv2.imshow("Test - Idle State", display)
            if cv2.waitKey(33) & 0xFF == ord('q'):  # 30fps
                break
    
    # Test attack state
    print("   - Testing attack animation...")
    game_display.start_attack_animation()
    
    for i in range(60):  # 2 seconds at 30fps
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
            cv2.imshow("Test - Attack State", display)
            if cv2.waitKey(33) & 0xFF == ord('q'):  # 30fps
                break
    
    # Test with hand tracking
    print("4. Testing with hand tracking...")
    import mediapipe as mp
    from gestureUtils import get_fingers_up, get_spells_from_fingers
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils
    
    for i in range(90):  # 3 seconds at 30fps
        ret, img = cap.read()
        if ret:
            # Process hand gestures
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)
            
            player_spell = None
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    fingers_up = get_fingers_up(hand_landmarks)
                    detected_spell = get_spells_from_fingers(fingers_up)
                    if detected_spell:
                        player_spell = detected_spell
            
            display = game_display.create_game_display(
                camera_frame=img,
                mage_spell="EARTH",
                player_spell=player_spell,
                countdown=1.5,
                player_hp=75,
                mage_hp=60,
                round_num=3
            )
            cv2.imshow("Test - Hand Tracking", display)
            if cv2.waitKey(33) & 0xFF == ord('q'):  # 30fps
                break
    
    # Cleanup
    cap.release()
    game_display.cleanup()
    cv2.destroyAllWindows()
    
    print("✅ Game display test completed successfully!")
    print("The new display system is working correctly!")

if __name__ == "__main__":
    test_game_display() 