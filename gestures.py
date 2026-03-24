"""Gesture definitions based on finger landmark positions."""

# Finger tip and pip landmark indices (MediaPipe Hands)
FINGER_TIPS = [4, 8, 12, 16, 20]   # thumb, index, middle, ring, pinky
FINGER_PIPS = [3, 6, 10, 14, 18]   # second joint of each finger


def fingers_up(hand_landmarks):
    """Return list of booleans: True if finger is extended."""
    lm = hand_landmarks.landmark
    up = []

    # Thumb: compare x-axis (works for right hand; flipped for left)
    up.append(lm[FINGER_TIPS[0]].x < lm[FINGER_PIPS[0]].x)

    # Other fingers: tip y < pip y means finger is up
    for tip, pip in zip(FINGER_TIPS[1:], FINGER_PIPS[1:]):
        up.append(lm[tip].y < lm[pip].y)

    return up  # [thumb, index, middle, ring, pinky]


def classify(hand_landmarks):
    """Return gesture name string for the given hand landmarks."""
    up = fingers_up(hand_landmarks)
    thumb, index, middle, ring, pinky = up

    if not any(up):
        return "Fist"
    if all(up):
        return "Open Hand"
    if thumb and not index and not middle and not ring and not pinky:
        return "Thumbs Up"
    if not thumb and index and middle and not ring and not pinky:
        return "Peace / V"
    if not thumb and index and not middle and not ring and not pinky:
        return "Point"
    if not thumb and index and middle and ring and pinky:
        return "Four"
    if not thumb and not index and not middle and not ring and pinky:
        return "Pinky"
    if thumb and index and not middle and not ring and not pinky:
        return "Gun"
    if thumb and not index and not middle and not ring and pinky:
        return "Rock On"
    if not thumb and index and middle and ring and not pinky:
        return "Three"
    return "Unknown"
