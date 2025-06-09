import cv2
import mediapipe as mp
from gestureUtils import getFingersUp,getSpellsFromFingers

cap = cv2.VideoCapture(0)

mapHands = mp.solutions.hands
hands = mapHands.Hands()
draw = mp.solutions.drawing_utils

while True:
    success, img = cap.read()
    imgRgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            draw.draw_landmarks(img, handLms, mapHands.HAND_CONNECTIONS)

            fingers = getFingersUp(handLms)
            spell = getSpellsFromFingers(fingers)

            if spell:
                cv2.putText(img, f"Spell: {spell}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)

    cv2.imshow("Wizard Duel - Hand Tracker", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
