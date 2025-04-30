import os
import tensorflow as tf
import tensorflow_hub as hub
import cv2
import numpy as np
import time
import random
import threading
from playsound import playsound

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

model = hub.load('https://tfhub.dev/google/movenet/multipose/lightning/1')
movenet = model.signatures['serving_default']

EDGES = {
    (0, 1): 'm', (0, 2): 'c', (1, 3): 'm', (2, 4): 'c',
    (0, 5): 'm', (0, 6): 'c', (5, 7): 'm', (7, 9): 'm',
    (6, 8): 'c', (8, 10): 'c', (5, 6): 'y', (5, 11): 'm',
    (6, 12): 'c', (11, 12): 'y', (11, 13): 'm', (13, 15): 'm',
    (12, 14): 'c', (14, 16): 'c'
}

ASSETS = {
    "green_img": r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\im1.png",
    "red_img": r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\im2.png",
    "green_sound": r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\greenLight.mp3",
    "red_sound": r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\redLight.mp3",
    "eliminate": r"D:\Squid-Game-main\Squid-Game-main\Squid-Game-main (1)\Squid-Game-main\gunshots.mp3"
}

def draw_keypoints(frame, keypoints, confidence_threshold):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))
    for ky, kx, kp_conf in shaped:
        if kp_conf > confidence_threshold:
            cv2.circle(frame, (int(kx), int(ky)), 6, (0, 255, 0), -1)

def draw_connections(frame, keypoints, edges, confidence_threshold):
    y, x, c = frame.shape
    shaped = np.squeeze(np.multiply(keypoints, [y, x, 1]))
    for edge in edges:
        p1, p2 = edge
        y1, x1, c1 = shaped[p1]
        y2, x2, c2 = shaped[p2]
        if c1 > confidence_threshold and c2 > confidence_threshold:
            cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)

def play_sound(sound_file):
    threading.Thread(target=playsound, args=(sound_file,), daemon=True).start()

def get_ankle_position(person):
    left_ankle = person[15]
    right_ankle = person[16]
    if left_ankle[2] > 0.5 and right_ankle[2] > 0.5:
        x = (left_ankle[1] + right_ankle[1]) / 2
        y = (left_ankle[0] + right_ankle[0]) / 2
        return (x, y)
    return None

def calculate_distance(p1, p2):
    if p1 is None or p2 is None:
        return 0  # or return a different default value
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)  # corrected formula


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

light_state = "green"
light_change_time = time.time() + random.randint(3, 6)
game_over = False
result_frame = None
moved_distance = 0
movement_threshold = 0.02
prev_ankle_position = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    img = tf.image.resize_with_pad(tf.expand_dims(frame, axis=0), 384, 640)
    input_img = tf.cast(img, dtype=tf.int32)
    results = movenet(input_img)
    keypoints_with_scores = results['output_0'].numpy()[:, :, :51].reshape((-1, 17, 3))

    person = keypoints_with_scores[0]
    draw_connections(frame, person, EDGES, 0.1)
    draw_keypoints(frame, person, 0.1)

    current_ankle_position = get_ankle_position(person)

    if light_state == "green" and current_ankle_position:
        if prev_ankle_position is not None:  # Only accumulate the moved distance when the previous position is valid
            step = calculate_distance(prev_ankle_position, current_ankle_position)
            print(f"[GREEN] Step size: {step:.4f}")
            
            if step > 0.004:  # Threshold for movement
                moved_distance += step
                print(f"[GREEN] Moved distance: {moved_distance:.4f}")
        else:
            print("[GREEN] Skipping movement calculation, no previous ankle position yet.")




    if time.time() >= light_change_time:
        light_state = "red" if light_state == "green" else "green"
        light_change_time = time.time() + random.randint(3, 6)

        light_img = cv2.imread(ASSETS["green_img"] if light_state == "green" else ASSETS["red_img"])
        if light_img is not None:
            cv2.imshow(f"{light_state.title()} Light", light_img)
            play_sound(ASSETS["green_sound"] if light_state == "green" else ASSETS["red_sound"])
            cv2.waitKey(1500)
            try:
                cv2.destroyWindow(f"{light_state.title()} Light")
            except cv2.error:
                pass


    if light_state == "red" and current_ankle_position and prev_ankle_position and not game_over:
        step = calculate_distance(prev_ankle_position, current_ankle_position)
        print(f"[RED] Movement during red: {step:.4f}")
        
        # Eliminate only if the player moves too much during red light
        if step > 0.006:
            result_frame = np.copy(frame)
            cv2.putText(result_frame, "You Moved During Red! Eliminated!", (25, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
            play_sound(ASSETS["eliminate"])
            game_over = True



    if not game_over and moved_distance > movement_threshold:
        result_frame = np.copy(frame)
        cv2.putText(result_frame, "You Walked Safely! Winner!", (25, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        game_over = True

    prev_ankle_position = current_ankle_position

    cv2.putText(frame, f"Moved Distance: {moved_distance:.3f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    if game_over and result_frame is not None:
        cv2.imshow("Result", result_frame)
        print("Game Over! Press 'q' to exit.")
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        break

    cv2.imshow("Main Window", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()