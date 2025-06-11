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
        cv2.destroyAllWindows()
        exit()
    cv2.putText(img, "Press any key to START", (50, int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    cv2.imshow("Wizard Duel - Get Ready!", img)
    if cv2.waitKey(10) != -1: # Wait for any key press
        break

print("\nWizard Duel Begins!")

while player_hp > 0 and mage_hp > 0:
    print(f"\nROUND {round_num}")
    print(f"Mage HP: {mage_hp} | YOUR HP: {player_hp}")
    
    mage_spell = get_random_spell()
    print(f"The mage casts: {mage_spell.upper()}! Counter it!")

    player_spell = None
    start_time = time.time()

    # Get frame dimensions for text placement
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    while time.time() - start_time < reaction_time:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame from camera.")
            player_hp = 0
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Display Mage's spell and countdown
        remaining_time = reaction_time - (time.time() - start_time)
        countdown_text = f"Counter in: {remaining_time:.1f}s"
        mage_spell_text = f"Mage casts: {mage_spell.upper()}"

        cv2.putText(img, mage_spell_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(img, countdown_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

        # Draw Player Health Bar (Bottom Left)
        player_bar_x = 20
        player_bar_y = frame_height - BAR_HEIGHT - 20
        draw_health_bar(img, player_hp, MAX_HP, player_bar_x, player_bar_y, "Player", HP_BAR_COLOR_PLAYER)

        # Draw Mage Health Bar (Bottom Right)
        mage_bar_x = frame_width - BAR_WIDTH - 20
        mage_bar_y = frame_height - BAR_HEIGHT - 20
        draw_health_bar(img, mage_hp, MAX_HP, mage_bar_x, mage_bar_y, "Mage", HP_BAR_COLOR_MAGE)

        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                fingers_up = get_fingers_up(hand_landmarks)
                detected_spell_this_frame = get_spells_from_fingers(fingers_up)

                if detected_spell_this_frame:
                    player_spell = detected_spell_this_frame # Update the "locked" spell for the round
                
                # Display the current "locked" player spell
                player_display_text = f"Your Spell: {player_spell.upper() if player_spell else '...'}"
                cv2.putText(img, player_display_text, (frame_width - 300, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)


        cv2.imshow("Wizard Duel - Cast YOUR SPELL!", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            player_hp = 0
            break

    cv2.destroyAllWindows()

    if player_spell:
        send_spell_to_unity(player_spell)
        print(f"You cast: {player_spell.upper()}")
    elif player_hp > 0:
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

    round_num += 1
    time.sleep(1.2)

cap.release()
cv2.destroyAllWindows()
