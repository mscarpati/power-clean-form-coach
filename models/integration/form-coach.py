from flask import Flask, request, jsonify, send_from_directory, url_for
from flask_cors import CORS

import sys
import os

sys.path.append('/Users/miascarpati/Desktop/Northwestern/Junior/Q3/COMP_SCI_397_Sports/power-clean-form-coach/models/posedetection/pytorch-openpose')
sys.path.append('/Users/miascarpati/Desktop/Northwestern/Junior/Q3/COMP_SCI_397_Sports/power-clean-form-coach/models')

from bartracking.bartracker import BarTracker
from posedetection.posedetector import PoseDetector

app = Flask(__name__, static_folder='/outputs')
CORS(app, supports_credentials=True)

class FormCoach:
    def __init__(self, video_file):
        self.absolute_output_dir = '/Users/miascarpati/Desktop/Northwestern/Junior/Q3/COMP_SCI_397_Sports/power-clean-form-coach/models/integration/outputs/'
        self.video_file = video_file
        self.pose_detector = PoseDetector(output_dir = self.absolute_output_dir, model_dir = "../posedetection/pytorch-openpose/model/body_pose_model.pth")

    def select(self):
        """
        Ask user to select bar tracker, pose detector, or both.
        """
        print("Welcome to Form Coach!")
        print("Please ensure that the video file is in the inputs directory. For best results, the video should be taken at a 3/4 angle from the front.")
        print("Select which model you would like to use.")
        print("1. Bar Tracker")
        print("2. Pose Detector")
        print("3. Both")
        print("If you need to make changes, press any other key to exit.")
        choice = input("Enter 1, 2, or 3: ")
        return choice
    
    def run_bar_tracker(self, video_file, frontendCall = False, cx = None, cy = None, radius = None, sw = None, sh = None):
        bar_tracker = BarTracker(video_file, self.absolute_output_dir)
        bar_tracker.track_bar(frontendCall=frontendCall, cx=cx, cy=cy, radius=radius, sw=sw, sh=sh) # need to fix output directory

    def run_pose_detector(self):
        print("Running pose detector...")
        self.pose_detector.process_vid(self.video_file) # need to fix output directory

    def run_both(self, cx, cy, radius):
        """
        Run output of one thru the other - prob do pose detector first.
        """
        self.run_pose_detector()
        res = "outputs/{}-out.mp4".format(os.path.basename(self.video_file).split('.')[0])
        self.run_bar_tracker(res, frontendCall = True, cx=cx, cy=cy, radius=radius)

form_coach = None
both = False
video_path = None

@app.route('/upload', methods=['POST'])
def upload_file():
    # Global variables for access in coord function
    # Maybe refactor?
    global form_coach
    global both
    global video_path

    video = request.files['file']
    barTracker = request.form.get('barTracker')
    # print(barTracker)
    poseDetector = request.form.get('formAnalysis')
    print(poseDetector)
    video_path = os.path.join('inputs', video.filename)
    video.save(video_path)
    form_coach = FormCoach(video_path)
    if barTracker == 'true' and poseDetector == 'true':
        both = True
        #form_coach.run_both()
        pass
    elif barTracker == 'true':
        pass
        #form_coach.run_bar_tracker(video_path, frontendCall = True)
    elif poseDetector == 'true':
        form_coach.run_pose_detector()

    return jsonify({'message': 'Video processed'})

@app.route('/bartracker', methods=['POST'])
def send_coords():
    cx = request.form.get('cx')
    cy = request.form.get('cy')
    radius = request.form.get('radius')
    sw = request.form.get('screenWidth')
    sh = request.form.get('screenHeight')
    if both:
        form_coach.run_both(cx=float(cx), cy=float(cy), radius=float(radius))
    else: form_coach.run_bar_tracker(video_path, frontendCall=True, cx=float(cx), cy=float(cy), radius=float(radius), sw=float(sw), sh=float(sh))
    return jsonify({'message': 'coordinates uploaded successfully!'})

@app.route('/inputs/<filename>')
def get_input(filename):
    return send_from_directory('/Users/miascarpati/Desktop/Northwestern/Junior/Q3/COMP_SCI_397_Sports/power-clean-form-coach/models/integration/inputs', filename)

@app.route('/results/<filename>')
def get_results(filename):
    #url = url_for('static', filename=filename)
    #print(url)
    #return url
    return send_from_directory('/Users/miascarpati/Desktop/Northwestern/Junior/Q3/COMP_SCI_397_Sports/power-clean-form-coach/models/integration/outputs', filename)

# need seperate function for getting circle coords
# also need to figure out running both call since front end requires video url

# to do: add another function that analyzes results? or can just add description on website

if __name__ == '__main__':
    app.run(debug=True, port=5001)

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         sys.exit('Usage: python3 form-coach.py <video_file>')
#     filename = "inputs/" + sys.argv[1]
#     form_coach = FormCoach(filename)
#     choice = form_coach.select()
#     if choice == '1':
#         form_coach.run_bar_tracker(filename)
#     elif choice == '2':
#         form_coach.run_pose_detector()
#     elif choice == '3':
#         form_coach.run_both()
#     else:
#         sys.exit('Invalid choice. Please enter 1, 2, or 3.')
