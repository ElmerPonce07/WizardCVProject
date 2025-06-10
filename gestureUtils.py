def get_fingers_up (hand_landmarks):
    ##"Returns a list of booleans that indicate which fingers are up "
    ##"[Thumb, Index, Middle, Ring, Pinky]"

    fingers = []

    TIP_IDS = [4, 8, 12, 16, 20] # Finger tip landmark IDs

    #Thumb (Compare X , NOT Y, Since thumbs goes sideways)
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)


    #Other fingers : tip highers than the pip join = finger Up

    for tip_id in TIP_IDS[1:]: # Skip thumb
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

def get_spells_from_fingers(fingers):
    if fingers == [0,1,1,0,0]:
        return "Fire"
    elif fingers == [1,1,1,1,1]:
        return "Water"
    elif fingers == [0,0,0,0,0]:
        return "Earth"
    else:
        return None