import cv2
import mediapipe as mp
from gestureUtils import get_fingers_up, get_spells_from_fingers

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
draw = mp.solutions.drawing_utils

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            fingers = get_fingers_up(hand_landmarks)
            spell = get_spells_from_fingers(fingers)

            if spell:
                cv2.putText(img, f"Spell: {spell}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)

    cv2.imshow("Wizard Duel - Hand Tracker", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
