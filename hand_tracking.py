import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        # Initialize the MediaPipe hand tracking module
        self.mp_hands = mp.solutions.hands
        # Set up the hands model (configured for up to 2 hands, minimum 70% confidence threshold)
        self.hands = self.mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

    def get_finger_position(self, frame):
        """Reads the frame from the camera and returns the (x, y) pixel coordinates of the index finger."""
        # OpenCV uses the BGR color format, while MediaPipe requires RGB. Converting:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        finger_pos = None # Returns None if no hand is detected
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Landmark point 8 is the tip of the index finger
                index_finger = hand_landmarks.landmark[8]
                
                # MediaPipe returns a ratio between 0 and 1, we convert this to screen pixels (x, y)
                h, w, c = frame.shape
                cx, cy = int(index_finger.x * w), int(index_finger.y * h)
                finger_pos = (cx, cy)
                
                # Draw a pink circle at the tip of our finger on the screen for testing
                cv2.circle(frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                # Uncomment the line below if you want to draw the entire hand skeleton:
                # self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return frame, finger_pos

    def get_multiple_positions(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        positions = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                index_finger = hand_landmarks.landmark[8]

                h, w, c = frame.shape
                cx, cy = int(index_finger.x * w), int(index_finger.y * h)
                positions.append((cx, cy))

                cv2.circle(frame, (cx, cy), 15, (255, 200, 50), cv2.FILLED)
                
        if len(positions) > 1:
            positions.sort(key=lambda pos: pos[0])

        return frame, positions
    
    #AI dodge methods
    def get_dodge_data(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        wrist_x = None
        wrist_y = None 
        ml_landmarks = []
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # To manage the character and menu cursor
            wrist_x = hand_landmarks.landmark[0].x
            wrist_y = hand_landmarks.landmark[0].y
            
            w_x = hand_landmarks.landmark[0].x
            w_y = hand_landmarks.landmark[0].y
            for lm in hand_landmarks.landmark:
                ml_landmarks.extend([lm.x - w_x, lm.y - w_y])
                
        
        return frame, wrist_x, wrist_y, ml_landmarks