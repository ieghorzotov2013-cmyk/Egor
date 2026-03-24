# Egor — Hand Gesture Recognition

Real-time hand gesture recognition using [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands) and OpenCV.

## Supported Gestures

| Gesture | Description |
|---------|-------------|
| Fist | All fingers closed |
| Open Hand | All five fingers extended |
| Thumbs Up | Only thumb extended |
| Peace / V | Index + middle extended |
| Point | Index finger only |
| Three | Index + middle + ring |
| Four | Index + middle + ring + pinky |
| Gun | Thumb + index |
| Rock On | Thumb + pinky |
| Pinky | Pinky only |

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### Webcam (real-time)

```bash
python hand_gesture_recognition.py
# or specify a different camera index
python hand_gesture_recognition.py --camera 1
```

Press **q** to quit.

### Static image

```bash
python hand_gesture_recognition.py --image photo.jpg
```

An annotated copy is saved as `photo_annotated.jpg`.

## Project Structure

```
.
├── hand_gesture_recognition.py  # Main entry point
├── gestures.py                  # Finger state logic & gesture classifier
└── requirements.txt             # Python dependencies
```

## How It Works

1. **Detection** — MediaPipe Hands locates 21 landmarks on each hand in the frame.
2. **Finger state** — For each finger, the tip y-coordinate is compared against the PIP joint y-coordinate to determine if the finger is extended.
3. **Classification** — The combination of extended fingers maps to a named gesture.
4. **Rendering** — OpenCV draws the skeleton and overlays the gesture label near the wrist.
