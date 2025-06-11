import time
import socket
import cv2
import mediapipe as mp
from gestureUtils import get_fingers_up, get_spells_from_fingers
from gameLogic import (
    evaluate_spell,
    is_game_over,
    get_random_spell,
    get_reaction_time,
)
from title_screen import TitleScreen
from game_display import GameDisplay

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Health Bar Configuration (adapted from main.py)
MAX_HP = 100
BAR_WIDTH = 200
BAR_HEIGHT = 25
HP_BAR_COLOR_PLAYER = (0, 255, 0)  # Green
HP_BAR_COLOR_MAGE = (0, 0, 255)    # Red
HP_BAR_BACKGROUND_COLOR = (100, 100, 100) # Dark Gray
TEXT_COLOR = (255, 255, 255) # White

difficulty = None # Will be set by player
player_hp = 100
mage_hp = 100
round_num = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_spell_to_unity(spell):
    sock.sendto(spell.encode(), (UDP_IP, UDP_PORT))

# Initialize camera first, before title screen
print("Initializing camera...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera!")
    exit()

# Get camera dimensions
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Initialize game display
game_display = GameDisplay(frame_width=1920, frame_height=1080)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

def draw_health_bar(image, current_hp, max_hp, x, y, label, bar_color):
    # Draw background
    cv2.rectangle(image, (x, y), (x + BAR_WIDTH, y + BAR_HEIGHT), HP_BAR_BACKGROUND_COLOR, -1)
    # Draw current health
    current_bar_width = int(BAR_WIDTH * (max(0, current_hp) / max_hp)) # Ensure current_hp isn't negative for drawing
    cv2.rectangle(image, (x, y), (x + current_bar_width, y + BAR_HEIGHT), bar_color, -1)
    # Draw border
    cv2.rectangle(image, (x, y), (x + BAR_WIDTH, y + BAR_HEIGHT), (50,50,50), 2)
    # Draw text
    cv2.putText(image, f"{label}: {max(0,current_hp)}/{max_hp}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 2)

# Show the new title screen with idle animation
print("Starting Wizard Fight...")
title_screen = TitleScreen()
difficulty = title_screen.show()

if difficulty == "quit":
    cap.release()
    game_display.cleanup()
    cv2.destroyAllWindows()
    exit()

reaction_time = get_reaction_time(difficulty)
print(f"Difficulty set to: {difficulty.upper()}. Reaction time: {reaction_time}s")
print("Press any key on the OpenCV window to start the duel...")

# Wait for a key press to start the game, showing a blank or camera feed
while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame. Exiting.")
        cap.release()
        game_display.cleanup()
        cv2.destroyAllWindows()
        exit()
    
    # Create a simple ready screen
    ready_display = game_display.create_game_display(
        camera_frame=img,
        player_hp=player_hp,
        mage_hp=mage_hp,
        round_num=round_num
    )
    cv2.putText(ready_display, "Press any key to START", (50, frame_height // 2), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    
    cv2.imshow("Wizard Duel - Get Ready!", ready_display)
    
    # Use consistent frame timing (120 FPS for 120 FPS lock)
    key = cv2.waitKey(8) & 0xFF  # ~120 FPS
    if key != -1: # Wait for any key press
        break

print("\nWizard Duel Begins!")

while player_hp > 0 and mage_hp > 0:
    print(f"\nROUND {round_num}")
    print(f"Mage HP: {mage_hp} | YOUR HP: {player_hp}")
    
    mage_spell = get_random_spell()
    print(f"The mage casts: {mage_spell.upper()}! Counter it!")
    
    # Start mage attack animation
    game_display.start_attack_animation(reaction_time)
    attack_start_time = time.time()

    player_spell = None
    reaction_start_time = time.time()

    # Play the attack animation synchronized with reaction time
    while time.time() - reaction_start_time < reaction_time:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame from camera.")
            player_hp = 0
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        # Gather all hand landmarks for display
        hand_landmarks = results.multi_hand_landmarks if results.multi_hand_landmarks else None

        # Always use the latest detected spell (not just the first)
        if hand_landmarks:
            for handLms in hand_landmarks:
                mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
                fingers_up = get_fingers_up(handLms)
                detected_spell_this_frame = get_spells_from_fingers(fingers_up)
                if detected_spell_this_frame:
                    player_spell = detected_spell_this_frame

        # Calculate remaining time for player reaction
        remaining_time = reaction_time - (time.time() - reaction_start_time)

        # Create the game display with all elements (including spell announcement)
        game_frame = game_display.create_game_display(
            camera_frame=img,
            mage_spell=mage_spell,  # This should show the spell announcement
            player_spell=player_spell,
            countdown=remaining_time,
            player_hp=player_hp,
            mage_hp=mage_hp,
            round_num=round_num,
            hand_landmarks=hand_landmarks,
            mp_draw=mp_draw,
            mp_hands=mp_hands
        )

        # Show the complete game display with consistent timing
        cv2.imshow("Wizard Duel", game_frame)
        
        # Use consistent frame timing (120 FPS for 120 FPS lock)
        key = cv2.waitKey(8) & 0xFF  # ~120 FPS
        if key == ord('q'):
            player_hp = 0
            break

    # Attack phase is over - animation system handles transition to idle automatically

    # Now check if player cast a spell within the reaction time
    if player_spell:
        send_spell_to_unity(player_spell)
        print(f"You cast: {player_spell.upper()}")
    else:
        print("You failed to cast a spell in time!")

    # Evaluate the round
    player_hp, mage_hp, round_result_message = evaluate_spell(player_spell, mage_spell, player_hp, mage_hp)
    print(round_result_message)

    # 🔁 Sync updated HP values with Unity
    send_spell_to_unity(f"PlayerHP:{player_hp}")
    send_spell_to_unity(f"MageHP:{mage_hp}")

    # Check for win/loss
    game_over_status = is_game_over(player_hp, mage_hp)
    if game_over_status == "player":
        print("\nYou have been defeated!")
        send_spell_to_unity("PlayerDead")
        break
    elif game_over_status == "mage":
        print("\nThe mage has been defeated! YOU WIN!")
        send_spell_to_unity("MageDead")
        break

    # Brief idle period between rounds (mage stays in idle)
    print("Preparing for next round...")
    idle_start_time = time.time()
    idle_duration = 1.5  # 1.5 seconds of idle between attacks
    
    while time.time() - idle_start_time < idle_duration:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame during idle phase.")
            break
            
        # Create idle display with preparation message
        game_frame = game_display.create_game_display(
            camera_frame=img,
            player_hp=player_hp,
            mage_hp=mage_hp,
            round_num=round_num,
            hand_landmarks=None,
            mp_draw=mp_draw,
            mp_hands=mp_hands
        )
        
        # Add preparation message to the display
        remaining_idle = idle_duration - (time.time() - idle_start_time)
        cv2.putText(game_frame, f"Preparing for next round... ({remaining_idle:.1f}s)", (50, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3, cv2.LINE_AA)
        
        # Use consistent window name
        cv2.imshow("Wizard Duel", game_frame)
        
        # Use consistent frame timing (120 FPS)
        key = cv2.waitKey(8) & 0xFF
        if key == ord('q'):
            player_hp = 0
            break
        
        # Safety check to prevent infinite loop
        if time.time() - idle_start_time > 5.0:  # Max 5 seconds
            print("Idle phase timeout, continuing to next round...")
            break

    print(f"Idle phase completed, starting round {round_num + 1}")
    round_num += 1

cap.release()
game_display.cleanup()
cv2.destroyAllWindows()
