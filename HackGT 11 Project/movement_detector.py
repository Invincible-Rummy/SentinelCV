# Detects patient movement and changes in posture
import math
import time

import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

# Initialize OpenCV VideoCapture (0 for webcam, or use a video file path)
webcam_id = 0
if webcam_id == 0:
    cap = cv2.VideoCapture(0)
else:
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Set frame dimensions and fps
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 10)

# Variables to track time and positions for different zones
zones = {
    'sacrum': None,
    'left_shoulder': None,
    'right_shoulder': None,
    'left_hip': None,
    'right_hip': None,
    'left_elbow': None,
    'right_elbow': None,
    'nose': None,
    'left_heel': None,
    'right_heel': None,
}

previous_positions = {
    'left_shoulder': None,
    'right_shoulder': None,
    'left_hip': None,
    'right_hip': None,
    'sacrum': None, 
    'left_elbow': None,
    'right_elbow': None,
    'nose': None,
    'left_heel': None,
    'right_heel': None,
}

movement_threshold = 30
last_change_times = {zone: time.time() for zone in zones}
reposition_alert_interval = 20  # 2 hours in seconds

def get_zone_positions(landmarks):
    positions = {
        'left_shoulder': (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y),
        'right_shoulder': (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y),
        'left_hip': (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y),
        'right_hip': (landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y),
        'sacrum': ((landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x + landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x) / 2,
                       (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y + landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y) / 2),
        'left_elbow': (landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y),
        'right_elbow': (landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y),
        'nose': (landmarks[mp_pose.PoseLandmark.NOSE.value].x, landmarks[mp_pose.PoseLandmark.NOSE.value].y),
        'left_heel': (landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y),
        'right_heel': (landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x,
                   landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y),
    }
    return positions

def check_movement(current_position, previous_position, threshold=movement_threshold):
    if previous_position is None:
        return "moving"  # Initial state assumes movement
    # Calculate Euclidean distance
    distance = math.sqrt((current_position[0] - previous_position[0]) ** 2 + (current_position[1] - previous_position[1]) ** 2)
    return "moving" if distance > threshold else "still"

def get_angle(x1, y1, x2, y2):
    """Calculate the angle of the line connecting two points with respect to the horizontal axis."""
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def get_posture(landmarks):
    # Get the x and y coordinates of key landmarks
    left_shoulder = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y)
    right_shoulder = (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y)
    left_hip = (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y)
    right_hip = (landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                 landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y)
    nose = (landmarks[mp_pose.PoseLandmark.NOSE.value].x,
            landmarks[mp_pose.PoseLandmark.NOSE.value].y)

    # Calculate the horizontal and vertical distances between shoulders and hips
    shoulder_width = abs(left_shoulder[0] - right_shoulder[0])
    hip_width = abs(left_hip[0] - right_hip[0])
    # shoulder_height_diff = left_shoulder[1] - right_shoulder[1]
    # hip_height_diff = left_hip[1] - right_hip[1]
    
    # Determine head orientation based on nose position
    nose_x_diff = nose[0] - ((left_shoulder[0] + right_shoulder[0]) / 2)

    # Determine posture based on distances and relative vertical positions
    if shoulder_width < 0.15 and hip_width < 0.15:  # Shoulders and hips are closer together (lying on side)
        # Check if lying on left side or right side based on nose position
        if nose_x_diff < 0:  # Nose is to the right of the midline
            return "Right Side"
        elif nose_x_diff > 0:  # Nose is to the left of the midline
            return "Left Side"
    else:
        return "Straight"

def has_moved(previous, current, threshold=0.05):
    # Calculate movement distance for multi-point zones (e.g., sacrum, shoulders)
    movement_distance = sum([(current[i] - previous[i]) ** 2 for i in range(len(current))]) ** 0.5
    return movement_distance > threshold

while True:
    success, img = cap.read()
    if not success:
        break

    # Convert the BGR image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if results.pose_landmarks:
        
        # Determine patient's posture
        posture = get_posture(results.pose_landmarks.landmark)

        # Display detected posture on the video feed
        cv2.putText(img, f"Posture: {posture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # Draw pose landmarks
        mp_draw.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Get current zone positions
        current_positions = get_zone_positions(results.pose_landmarks.landmark)
        movement_statuses = {}
        key_parts = get_zone_positions(landmarks=results.pose_landmarks.landmark)

        for part, current_position in key_parts.items():
            movement_statuses[part] = check_movement(current_position, previous_positions[part])
            previous_positions[part] = current_position  # Update the previous position

        # Draw boxes and labels for each key part
        for part, position in key_parts.items():
            # Convert normalized coordinates to pixel coordinates
            h, w, _ = img.shape
            x, y = int(position[0] * w), int(position[1] * h)
            # Draw a rectangle around the key part
            cv2.rectangle(img, (x - 20, y - 20), (x + 20, y + 20), (0, 255, 0), 2)
            # Put movement status text near the box
            cv2.putText(img, f"{part}: {movement_statuses[part]}", (x - 40, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)

        # Check movements for each zone
        for zone, last_position in zones.items():
            if last_position:
                # Determine if the zone has moved sufficiently
                if has_moved(last_position, current_positions[zone]):
                    print(zone, "moved right now!")
                    last_change_times[zone] = time.time()  # Reset timer for this zone
                    print(f"{zone.capitalize()} moved; timer reset.")
            
            # Update last known position for the zone
            zones[zone] = current_positions[zone]

        # Check if all zones have been inactive beyond the alert interval
        if all(time.time() - last_change_times[zone] > reposition_alert_interval for zone in zones):
            print("Reposition alert: It's time to change the patient's position!")

    # Display the image
    cv2.imshow("Patient Monitoring - Multi-Zone", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
