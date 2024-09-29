# Defines important functions
import math

import cv2
import mediapipe as mp

movement_threshold = {'left_shoulder': .003, 
                      'right_shoulder': .003, 
                      'left_hip': .01, 
                      'right_hip': .01, 
                      'sacrum': .01, 
                      'left_elbow': .01, 
                      'right_elbow': .01,
                      'left_heel': .011, 
                      'right_heel': .011, 
                      'nose': .01
                      }# 0.3

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils
key_joints = ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip', 'sacrum', 'left_elbow', 'right_elbow', 'left_heel', 'right_heel', 
              'nose']

def get_zone_positions(landmarks):
    positions = {
        'left_shoulder': (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y),
        'right_shoulder': (landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y),
        'left_hip': (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y),
        'right_hip': (landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y),
        'sacrum': ((landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x + landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x) / 2,
                   (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y + landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y) / 2),
        'left_elbow': (landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y),
        'right_elbow': (landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y),
        'left_heel': (landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HEEL.value].y),
        'right_heel': (landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y),
        'nose': (landmarks[mp_pose.PoseLandmark.NOSE.value].x, landmarks[mp_pose.PoseLandmark.NOSE.value].y),
    }
    return positions

def draw_parts(img, zones):
    for part, position in zones.items():
        if position == None: 
            continue
        # Convert normalized coordinates to pixel coordinates
        h, w, _ = img.shape
        x, y = int(position[0] * w), int(position[1] * h)
        # Draw a rectangle around the key part
        cv2.rectangle(img, (x - 20, y - 20), (x + 20, y + 20), (0, 255, 0), 2)
        # Put movement status text near the box
        cv2.putText(img, part, (x - 40, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)

def has_moved(previous, current, threshold=0.05):
    # Calculate movement distance for multi-point zones (e.g., sacrum, shoulders)
    movement_distance = sum([(current[i] - previous[i]) ** 2 for i in range(len(current))]) ** 0.5
    return movement_distance > threshold

def get_angle(x1, y1, x2, y2):
    # Calculate the angle of the line connecting two points with respect to the horizontal axis
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def check_movement(current_position, previous_position, threshold):
    if previous_position is None:
        return "moving"  # Initial state assumes movement
    # Calculate Euclidean distance
    distance = math.sqrt((current_position[0] - previous_position[0]) ** 2 + (current_position[1] - previous_position[1]) ** 2)
    return "moving" if distance > threshold else "still"

def get_posture(positions):
    # Get the x and y coordinates of key landmarks
    left_shoulder = positions['left_shoulder']
    right_shoulder = positions['right_shoulder']
    nose = positions['nose']

    # Calculate the horizontal and vertical distances between shoulders and hips
    shoulder_width = abs(positions['left_shoulder'][0] - positions['right_shoulder'][0])
    hip_width = abs(positions['left_hip'][0] - positions['right_hip'][0])
    
    # Determine head orientation based on nose position
    nose_x_diff = nose[0] - ((left_shoulder[0] + right_shoulder[0]) / 2)

    # Determine posture based on distances and relative vertical positions
    if shoulder_width < 0.20 and hip_width < 0.16:  # Shoulders and hips are closer together (lying on side)
        # Check if lying on left side or right side based on nose position
        if nose_x_diff < 0:  # Nose is to the right of the midline
            return "Right Side"
        elif nose_x_diff > 0:  # Nose is to the left of the midline
            return "Left Side"
    else:
        return "Supine"
