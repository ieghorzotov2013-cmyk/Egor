"""Real-time hand gesture recognition using MediaPipe and OpenCV.

Usage:
    python hand_gesture_recognition.py [--camera <index>] [--image <path>]

Arguments:
    --camera  Camera device index (default: 0)
    --image   Path to a static image to process instead of webcam
"""

import argparse
import sys

import cv2
import mediapipe as mp

from gestures import classify

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def draw_results(image, results):
    """Overlay landmarks and gesture labels on the frame."""
    if not results.multi_hand_landmarks:
        return image

    h, w, _ = image.shape
    for hand_landmarks in results.multi_hand_landmarks:
        # Draw skeleton
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style(),
        )

        # Gesture label near the wrist
        gesture = classify(hand_landmarks)
        wrist = hand_landmarks.landmark[0]
        cx, cy = int(wrist.x * w), int(wrist.y * h)
        cv2.putText(
            image,
            gesture,
            (cx - 40, cy + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    return image


def process_image(path):
    """Run gesture recognition on a single image file."""
    image = cv2.imread(path)
    if image is None:
        print(f"Error: cannot read image '{path}'")
        sys.exit(1)

    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5,
    ) as hands:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if not results.multi_hand_landmarks:
            print("No hands detected.")
        else:
            for i, lm in enumerate(results.multi_hand_landmarks):
                print(f"Hand {i + 1}: {classify(lm)}")

        output = draw_results(image, results)
        out_path = path.rsplit(".", 1)[0] + "_annotated.jpg"
        cv2.imwrite(out_path, output)
        print(f"Annotated image saved to: {out_path}")


def process_webcam(camera_index):
    """Run real-time gesture recognition from webcam."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: cannot open camera {camera_index}")
        sys.exit(1)

    print("Press 'q' to quit.")

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
    ) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: failed to read frame.")
                break

            frame = cv2.flip(frame, 1)  # mirror for natural interaction
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            results = hands.process(rgb)
            rgb.flags.writeable = True

            frame = draw_results(frame, results)

            cv2.imshow("Hand Gesture Recognition  [q to quit]", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="Hand Gesture Recognition")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--camera", type=int, default=0, help="Camera device index (default: 0)")
    group.add_argument("--image", type=str, help="Path to a static image")
    args = parser.parse_args()

    if args.image:
        process_image(args.image)
    else:
        process_webcam(args.camera)


if __name__ == "__main__":
    main()
