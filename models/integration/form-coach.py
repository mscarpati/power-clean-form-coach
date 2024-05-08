from bartracking.bartracker import BarTracker
from posedetection.posedetector import PoseDetector

class FormCoach:
    def __init__(self, video_file):
        self.video_file = video_file
        self.bar_tracker = BarTracker(video_file)
        self.pose_detector = PoseDetector()

    def select(self):
        """
        Ask user to select bar tracker, pose detector, or both.
        """
        print("Select which model you would like to use.")
        print("1. Bar Tracker")
        print("2. Pose Detector")
        print("3. Both")
        choice = input("Enter 1, 2, or 3: ")
        return choice
    
    def run_bar_tracker(self):
        self.bar_tracker.track_bar() # need to fix output directory

    def run_pose_detector(self):
        self.pose_detector.process_vid(self.video_file) # need to fix output directory

    def run_both(self):
        """
        Run output of one thru the other - prob do pose detector first.
        """
        pass
