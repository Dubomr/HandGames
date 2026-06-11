import cv2
import mediapipe as mp
import csv
import os

def collect_data():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)
    csv_file = "gesture_dataset.csv"

    if not os.path.exists(csv_file):
        with open(csv_file, mode='w', newline='') as f:
            writer = csv.writer(f)
            header = ['label']
            for i in range(21):
                header.extend([f'x{i}', f'y{i}'])
            writer.writerow(header)

    print("--- NEW DATA COLLECTION BEGINS ---")
    print("0: Fist (Shield) | 1: Open Hand (Ineffective) | 2: One Finger (Dash)")
    print("Usage: Perform the action and PRESS AND HOLD on the corresponding number.")

    while True:
        success, img = cap.read()
        if not success: break
        img = cv2.flip(img, 1)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_img)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            wrist_x = hand_landmarks.landmark[0].x
            wrist_y = hand_landmarks.landmark[0].y

            landmarks_list = []
            for lm in hand_landmarks.landmark:
                relative_x = lm.x - wrist_x
                relative_y = lm.y - wrist_y
                landmarks_list.extend([relative_x, relative_y])

            key = cv2.waitKey(1) & 0xFF
            # Now we are listening to the 0, 1 and 2 keys.
            if key in [ord('0'), ord('1'), ord('2')]:
                label = chr(key)
                row = [label] + landmarks_list
                with open(csv_file, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
                cv2.putText(img, f"KAYDEDILIYOR: {label}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        cv2.putText(img, "0:Yumruk 1:Acik El 2:Tek Parmak Q:Cikis", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("Veri Toplama", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    collect_data()