import cv2
import mediapipe as mp
from gestureUtils import get_fingers_up, get_spells_from_fingers

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
draw = mp.solutions.drawing_utils

# Health Bar Configuration
MAX_HP = 100
player_hp = MAX_HP
mage_hp = MAX_HP

BAR_WIDTH = 200
BAR_HEIGHT = 25
HP_BAR_COLOR_PLAYER = (0, 255, 0)  # Green
HP_BAR_COLOR_MAGE = (0, 0, 255)    # Red
HP_BAR_BACKGROUND_COLOR = (100, 100, 100) # Dark Gray
TEXT_COLOR = (255, 255, 255) # White

def draw_health_bar(image, current_hp, max_hp, x, y, label, bar_color):
    # Draw background
    cv2.rectangle(image, (x, y), (x + BAR_WIDTH, y + BAR_HEIGHT), HP_BAR_BACKGROUND_COLOR, -1)
    # Draw current health
    current_bar_width = int(BAR_WIDTH * (current_hp / max_hp))
    cv2.rectangle(image, (x, y), (x + current_bar_width, y + BAR_HEIGHT), bar_color, -1)
    # Draw border
    cv2.rectangle(image, (x, y), (x + BAR_WIDTH, y + BAR_HEIGHT), (50,50,50), 2)
    # Draw text
    cv2.putText(image, f"{label}: {current_hp}/{max_hp}", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, TEXT_COLOR, 2)

while True:
    success, img = cap.read()
    if not success:
        print("Failed to grab frame.")
        break

    frame_height, frame_width, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            fingers = get_fingers_up(hand_landmarks)
            spell = get_spells_from_fingers(fingers)

            if spell:
                cv2.putText(img, f"Spell: {spell}", (frame_width // 2 - 100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3, cv2.LINE_AA)
                # Mage takes damage when a spell is cast
                if mage_hp > 0:
                    mage_hp = max(0, mage_hp - 10) # Decrease mage HP, ensure it doesn't go below 0

    # Draw Player Health Bar (Bottom Left)
    player_bar_x = 20
    player_bar_y = frame_height - BAR_HEIGHT - 20
    draw_health_bar(img, player_hp, MAX_HP, player_bar_x, player_bar_y, "Player", HP_BAR_COLOR_PLAYER)

    # Draw Mage Health Bar (Bottom Right)
    mage_bar_x = frame_width - BAR_WIDTH - 20
    mage_bar_y = frame_height - BAR_HEIGHT - 20
    draw_health_bar(img, mage_hp, MAX_HP, mage_bar_x, mage_bar_y, "Mage", HP_BAR_COLOR_MAGE)
    
    cv2.imshow("Wizard Duel - Hand Tracker", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
