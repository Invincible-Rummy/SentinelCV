import threading
from flask import Flask, Response, jsonify, render_template

from patient_detector import process_video_feed 


app = Flask(__name__)


# Stores video frames for general feed
general_feed_frame = None


# Dictionary to store video frames for patient feeds
patient_feeds = {}


# Dictionaries to store patient status frames
patient_joint_alerts = {}
patient_positions = {}
patient_position_alerts = {}


def update_feeds():
    global general_feed_frame, patient_feeds, patient_joint_alerts, patient_positions, patient_position_alerts
    for general_feed, patient_frames, patient_joint_alerts1, patient_positions1, patient_position_alerts1 in process_video_feed():
        general_feed_frame = general_feed
        patient_feeds = patient_frames
        patient_joint_alerts = patient_joint_alerts1
        patient_positions = patient_positions1
        patient_position_alerts = patient_position_alerts1


thread = threading.Thread(target=update_feeds)
thread.daemon = True
thread.start()


@app.route('/')
def index():
    return render_template('index.html', patient_count=len(patient_feeds))


@app.route('/index')
def home():
    return render_template('index.html')


@app.route('/video_feed_general')
def video_feed_general():
    # Return the response with processed video frames for general video
    def generate():
        global general_feed_frame
        while True:
            if general_feed_frame:
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + general_feed_frame + b'\r\n')
            else:
                yield b''
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed/<int:patient_id>')
def video_feed(patient_id):
    # Return the response with processed video frames for individual patient videos
    def generate():
        while True:
            if patient_id in patient_feeds:
                frame = patient_feeds[patient_id]
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                yield b''
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/get_patient_joint_alert/<int:patient_id>')
def get_patient_joint_alert(patient_id):
    # Gets patient joint alert boolean
    def generate():
        while True:
            if patient_id in patient_joint_alerts:
                # Yield the patient joint alert data as a boolean (converted to JSON-like text)
                yield f"data: {str(patient_joint_alerts[patient_id]).lower()}\n\n"
            else:
                # Yield an empty string if the patient ID does not exist
                yield f"data: false\n\n"
    return Response(generate(), mimetype='text/event-stream')


@app.route('/get_patient_position/<int:patient_id>')
def get_patient_position(patient_id):
    # Gets patient position
    def generate():
        while True:
            if patient_id in patient_positions:
                # Yield the patient position data as JSON
                yield f"data: {patient_positions}\n\n"
            else:
                yield f""
    return Response(generate(), mimetype='text/event-stream')


@app.route('/get_patient_position_alert/<int:patient_id>')
def get_patient_position_alert(patient_id):
    # Function to stream position alert data for the specified patient as a boolean
    def generate():
        while True:
            if patient_id in patient_position_alerts:
                # Yield the patient position alert data as a boolean (converted to JSON-like text)
                yield f"data: {str(patient_position_alerts[patient_id]).lower()}\n\n"
            else:
                # Yield an empty string if the patient ID does not exist
                yield f"data: false\n\n"
    return Response(generate(), mimetype='text/event-stream')


@app.route('/get_patient_count')
def get_patient_count():
    # Gets number of patients in room
    return jsonify({'patient_count': len(patient_feeds)})

@app.route('/patients')
def patients():
    return render_template('patients.html')

if __name__ == '__main__':
    app.run(debug=True)