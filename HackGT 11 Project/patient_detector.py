# Detects all patients and extracts bounding box info for each patient
from copy import deepcopy

import cv2
import mediapipe as mp
from ultralytics import YOLO

from movement_functions import *
from patient_class import *

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

patients = []

# Model
model = YOLO("yolo-Weights/yolov8n.pt")

# Object classes
classNames = ["person"]

def create_patients_list(img):
    id = 0
    buffer_pixels = 40
    results = model(img, stream=True)
    for r in results:   
        boxes = r.boxes
        counter = 0
        for box in boxes:
            counter += 1
            if int(box.cls[0]) != 0:
                continue

            x1, y1, x2, y2 = box.xyxy[0]
            height, width = img.shape[:2]            
            x1, y1, x2, y2 = max(int(x1) - buffer_pixels, 0), max(int(y1) - buffer_pixels, 0), min(int(x2) + buffer_pixels, width), min(int(y2) + buffer_pixels, height)

            # Ensure valid bounding box coordinates
            if x1 < 0 or y1 < 0 or x2 > img.shape[1] or y2 > img.shape[0]:
                print("Bounding box exceeds frame dimensions")
                continue
            
            id += 1
            patients.append(Patient(x1, y1, x2, y2, id))

def draw_bounds(img):
    for patient in patients:
        # Draw bounding box
        cv2.rectangle(img, (patient.x1, patient.y1), (patient.x2, patient.y2), (255, 0, 255), 3)

        # Put text
        org = [patient.x1, patient.y1]
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        color = (255, 0, 0)
        thickness = 2
        cv2.putText(img, "Patient " + str(patient.id), org, font, fontScale, color, thickness)

def process_video_feed():
    global patients

    # Capture video from camera
    webcam_id = 1
    if webcam_id == 0:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    # Set frame dimensions and fps
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # Display room with bounding boxes and individual patients
    while True:
        success, img = cap.read()
        if not success:
            break

        if not patients:
            create_patients_list(img)

        # Create dictionary to store individual patient video feeds
        patient_feeds = {}

        # Create status dictionaries
        patient_joint_alerts = {}
        patient_positions = {}
        patient_position_alerts = {}

        for patient in patients:
            
            img_rgb = deepcopy(img[patient.y1 : patient.y2, patient.x1 : patient.x2])
            results_joint = pose.process(img_rgb)

            landmarks = results_joint.pose_landmarks
            
            if landmarks:
                # Draw pose landmarks
                mp_draw.draw_landmarks(img_rgb, landmarks, mp_pose.POSE_CONNECTIONS)
                positions = get_zone_positions(landmarks.landmark)

                patient.update_joints(positions)
                
                # Determine patient's posture
                posture = get_posture(positions)

                patient.update_frame(posture)

                # Update patient status dictionaries
                patient_joint_alerts[patient.id] = patient.check_joints()
                patient_positions[patient.id] = posture
                patient_position_alerts[patient.id] = patient.nurse_alert

                # Display detected posture on the video feed
                cv2.putText(img_rgb, f"Posture: {posture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                draw_parts(img_rgb, positions)

                # Encode the fram for streaming individual patient feeds
                ret2, buffer2 = cv2.imencode('.jpg', img_rgb)
                frame2 = buffer2.tobytes()

                # Add individual patient frames to dictionary
                patient_feeds[patient.id] = frame2

        draw_bounds(img)

        # Encode the frame for streaming room feed
        ret1, buffer1 = cv2.imencode('.jpg', img)
        general_feed = buffer1.tobytes()
        
        # Yield the frames to be used in streaming room and individual patient feeds, yield the status dictionaries
        yield (general_feed, patient_feeds, patient_joint_alerts, patient_positions, patient_position_alerts)   

#     if cv2.waitKey(1) == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
