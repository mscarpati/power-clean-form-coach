## Get optimal angles/values from dataset
## Was within the models/pose-detection/pytorch-openpose directory
import sys
import os
from os import walk
import pandas as pd
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

sys.path.append('/Users/miascarpati/Desktop/Northwestern/Junior/Q3/COMP_SCI_397_Sports/power-clean-form-coach/models/pose-detection/pytorch-openpose')
from src import util
from src.body import Body

class Testing:
    def __init__(self):
        self.results = {"knee_angle_l": [], "knee_angle_r": [], "hip_angle_l": [], "hip_angle_r": [], "bar_distance": []} # will convert to pandas df and get avg, sd, and store in csv
        self.body_est = Body('../model/body_pose_model.pth')

    def process_image(self, frame, is_bar = True, bar_distances=None, is_knee=False, is_hip=False, is_single=False):
        candidate, subset = self.body_est(frame)
        marked_up = util.draw_bodypose(frame, candidate, subset)
        
        if len(candidate) > 0:
            coordinates = np.delete(candidate, (2, 3), 1)
            if is_bar:
                bar_distances.append(util.get_bar_distance(coordinates[4], coordinates[7]))
            if is_knee:
                self.results["knee_angle_r"].append(util.get_angle(coordinates[11], coordinates[12], coordinates[13]))
                self.results["knee_angle_l"].append(util.get_angle(coordinates[8], coordinates[9], coordinates[10]))
            elif is_hip:
                self.results["hip_angle_l"].append(util.get_angle(coordinates[1], coordinates[8], coordinates[9]))
                self.results["hip_angle_r"].append(util.get_angle(coordinates[1], coordinates[11], coordinates[12]))

        if not is_single:
            return marked_up
        else:
            plt.imshow(marked_up[:, :, [2, 1, 0]])
            plt.show()
    
    def process_vid(self, video):
        bar_distance = []
        cap = None
        try:
            cap = cv.VideoCapture(video)
        except:
            sys.exit("Cannot open video file")

        index = 0
        while True:
            ok, frame = cap.read()
            
            if not ok:
                print('Cannot read video file')
                break
            
            h, w, _ = frame.shape
            fps = cap.get(cv.CAP_PROP_FPS)
            fourcc = cv.VideoWriter_fourcc(*'mp4v')
            video_out = cv.VideoWriter("res/{}-out.mp4".format(index), fourcc, fps, (w,h), isColor=True)
            canvas = self.process_image(frame, bar_distance)

            video_out.write(canvas)
            index += 1

        self.results["bar_distance"].append(np.mean(bar_distance))
        cap.release()
        video_out.release()
        cv.destroyAllWindows()

    def process_dir(self, path, is_knee=False, is_hip=False, img=False):
        _, _, files = next(walk(path))
        if img:
            for file in files:
                file_path = os.path.join(path, file)
                frame = cv.imread(file_path)
                if frame is None:
                    print("Failed to read image")
                    continue
                self.process_image(frame, is_bar=False, is_knee=is_knee, is_hip=is_hip, is_single=True)
        else:
            for file in files:
                self.process_vid(file)

    def get_results(self):
        # pad self.results with None if not enough data
        max_data_len = 0
        for key in self.results:
            max_data_len = max(max_data_len, len(self.results[key]))
        
        for key in self.results:
            if len(self.results[key]) < max_data_len:
                self.results[key] += [None] * (max_data_len - len(self.results[key]))

        for key in self.results:
            avg = np.mean([x for x in self.results[key] if x is not None])
            sd = np.std([x for x in self.results[key] if x is not None])
            self.results[key].append(avg)
            self.results[key].append(sd)
        
        df = pd.DataFrame(self.results)
        df.to_csv("res/results.csv")

if __name__ == "__main__":
    test = Testing()
    #test.process_dir('training/hip', is_hip=True, img=True)
    test.process_dir('training/knee', is_knee=True, img=True)
    #test.process_dir('training/video') # still need to test this
    test.get_results()