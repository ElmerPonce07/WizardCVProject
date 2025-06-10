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


UDP_IP = "127.0.0.1"
UDP_PORT = 5005

difficulty = "medium"
player_hp = 100
mage_hp = 100
round_num = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_spell_to_unity(spell):
    sock.sendto(spell.encode(), (UDP_IP, UDP_PORT))

cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

print("Wizard Duel Begins!\nPress Q to QUIT.")
reaction_time = get_reaction_time(difficulty)

while player_hp > 0 and mage_hp > 0 :
    print (f"\n ROUND {round_num}")
    print (f"Mage HP: {mage_hp} | YOUR HP: {player_hp}")
    
    mage_spell = get_random_spell()
    print (f"The mage casts: {mage_spell.upper()}! Counter it!")


    player_spell = None 
    start_time = time.time()

    while time.time() - start_time < reaction_time:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame from camera.")
            player_hp = 0
            break
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                fingers_up = get_fingers_up(hand_landmarks)
                spell = get_spells_from_fingers(fingers_up)
                if spell:
                    player_spell = spell
                    break
        cv2.imshow("Wizard Duel - Cast YOUR SPELL!", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            player_hp=0
            break

    cv2.destroyAllWindows()

    if player_spell:
        send_spell_to_unity(player_spell)
        print(f"You cast: {player_spell.upper()}")
    elif player_hp > 0:
        print("You failed to cast a spell in time!")

    player_hp, mage_hp, round_result_message = evaluate_spell(player_spell, mage_spell, player_hp, mage_hp)
    print(round_result_message)

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
