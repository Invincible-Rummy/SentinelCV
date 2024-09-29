# Instantiates Patient objects
import time
from collections import Counter
from statistics import mode

from movement_functions import has_moved, key_joints, movement_threshold

# import pyttsx3


# engine = pyttsx3.init()

class Patient:
    minutes_stored = 6 # 360
    joints_threshold = 20 # seconds
    # possible_positions = ["Supine", "Left Side", "Right Side"]

    # Constructor
    def __init__(self, x1, y1, x2, y2, id, nurse_threshold=300, patient_threshold=285):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.id = id
        self.past_positions = {joint: None for joint in key_joints}
        self.last_moved = {joint: time.time() for joint in key_joints}
        self.frame_list = []
        self.sec_list = []
        self.min_list = []
        self.nurse_threshold = 5 # nurse_threshold
        self.patient_threshold = 4 # patient_threshold
        self.nurse_alert = False
        self.curr_index = 0
        self.patient_alert = False
        self.patient_alert_position = None

    # Update all joints and positions given a dictionary of joints & current positions
    def update_joints(self, positions):
        for joint, position in positions.items():
            if self.past_positions[joint] == None: continue
            if has_moved(self.past_positions[joint], position, movement_threshold[joint]):
                self.last_moved[joint] = time.time()        
        self.past_positions = positions

    def joints_alerts(self):
        alert_joints = self.check_joints()
        for joint in alert_joints:
            print(str(self.id) + ": You haven't moved your " + joint + " in a while!")

    # Check which joints haven't been moved in long enough
    def check_joints(self):
        # alert_joints = []
        for joint, tm in self.last_moved.items():
            if time.time() - tm > self.joints_threshold:
                return True
        return False

    # Function to call during each frame iteration (30 fps)
    def update_frame(self, position):
        self.frame_list.append(position)
        if len(self.frame_list) > 3: #30
            avg = mode(self.frame_list)
            self.frame_list = []
            self.__update_sec(avg)

    # Placeholder function for sending patient alert        
    def send_patient_alert(self):
        pass

    # Placeholder function for sending nurse alert 
    def send_nurse_alert(self):
        pass
            
    # Dismiss the nurse alert
    def dismiss_alert(self):
        nurse_alert = False

    # Update the stored list of past 60 seconds
    def __update_sec(self, position):
        self.sec_list.append(position)
        if len(self.sec_list) > 3: #60
            avg = mode(self.sec_list)
            self.sec_list = []
            self.__update_min(avg)

    # Update the stored list of past 360 minutes
    def __update_min(self, position):
        if len(self.min_list) == 0:
            self.nurse_alert = False
        if self.curr_index < self.minutes_stored:
            self.min_list.append(position)
        else:
            self.min_list[self.curr_index % self.minutes_stored] = position
        self.curr_index += 1

        # Check the frequency of each position
        frequency_list = Counter(self.min_list)
        for pos, frq in frequency_list.items():
            # Send an alert to the patient
            if not self.patient_alert and frq == self.patient_threshold:
                self.send_patient_alert()            
                print("PATIENT ALERT")
                print(str(self.id) + ": Please move off your " + ("back" if pos == "Supine" else pos.lower()) + " to avoid pressure ulcers!")
                self.patient_alert = True   
                self.patient_alert_position = pos
            elif self.patient_alert and pos == self.patient_alert_position and frq != self.patient_threshold:
                self.patient_alert = False

            # Send an alert to the nurse
            if frq >= self.nurse_threshold and not self.nurse_alert:
                self.send_nurse_alert()            
                print("NURSE ALERT")
                self.nurse_alert = True
                self.min_list = []
                self.curr_index = 0
                break
