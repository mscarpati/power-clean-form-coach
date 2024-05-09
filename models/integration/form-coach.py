import sys
import os

sys.path.append('/Users/miascarpati/Desktop/Northwestern/Junior/Q3/COMP_SCI_397_Sports/power-clean-form-coach/models/posedetection/pytorch-openpose')
sys.path.append('/Users/miascarpati/Desktop/Northwestern/Junior/Q3/COMP_SCI_397_Sports/power-clean-form-coach/models')

from bartracking.bartracker import BarTracker
from posedetection.posedetector import PoseDetector



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
    
    def run_bar_tracker(self, video_file):
        bar_tracker = BarTracker(video_file, self.absolute_output_dir)
        bar_tracker.track_bar() # need to fix output directory

    def run_pose_detector(self):
        self.pose_detector.process_vid(self.video_file) # need to fix output directory

    def run_both(self):
        """
        Run output of one thru the other - prob do pose detector first.
        """
        self.run_pose_detector()
        res = "outputs/{}-out.mp4".format(os.path.basename(self.video_file).split('.')[0])
        self.run_bar_tracker(res)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 form-coach.py <video_file>')
    filename = "inputs/" + sys.argv[1]
    form_coach = FormCoach(filename)
    choice = form_coach.select()
    if choice == '1':
        form_coach.run_bar_tracker(filename)
    elif choice == '2':
        form_coach.run_pose_detector()
    elif choice == '3':
        form_coach.run_both()
    else:
        sys.exit('Invalid choice. Please enter 1, 2, or 3.')
