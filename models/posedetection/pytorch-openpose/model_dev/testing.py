## Get optimal angles/values from dataset
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
        self.results = {"src": [], "knee_angle_l": [], "knee_angle_r": [], "hip_angle_l": [], "hip_angle_r": [], "bar_distance": []} # will convert to pandas df and get avg, sd, and store in csv
        self.body_est = Body('../model/body_pose_model.pth')

    def process_image(self, frame, is_bar = True, bar_distances=None, is_knee=False, is_hip=False, is_single=False):
        candidate, subset = self.body_est(frame)
        marked_up = util.draw_bodypose(frame, candidate, subset)
        
        if len(candidate) > 0:
            coordinates = np.delete(candidate, (2, 3), 1)
            print("Length of Coordinates: ", len(coordinates))
            if is_bar:
                bar_distances.append(util.get_bar_distance(coordinates[4], coordinates[7]))
            if is_knee:
                self.results["knee_angle_r"].append(util.get_angle(coordinates[13], coordinates[14], coordinates[15]))
                self.results["knee_angle_l"].append(util.get_angle(coordinates[9], coordinates[10], coordinates[11]))
                #print("Left knee angle: ", util.get_angle(coordinates[9], coordinates[10], coordinates[11]))
                #print("Right knee angle: ", util.get_angle(coordinates[13], coordinates[14], coordinates[15]))
            elif is_hip:
                self.results["hip_angle_l"].append(util.get_angle(coordinates[2], coordinates[9], coordinates[10]))
                self.results["hip_angle_r"].append(util.get_angle(coordinates[2], coordinates[12], coordinates[13]))
                print("Left hip angle: ", util.get_angle(coordinates[1], coordinates[8], coordinates[9]))
                print("Right hip angle: ", util.get_angle(coordinates[1], coordinates[11], coordinates[12]))

        if not is_single:
            return marked_up
        else:
            plt.imshow(marked_up[:, :, [2, 1, 0]])
            plt.show()
    
    def process_vid(self, video, index):
        bar_distance = []
        cap = None
        try:
            cap = cv.VideoCapture(video)
        except:
            sys.exit("Cannot open video file")

        video_out = None
        ok, frame = cap.read()
        h, w, _ = frame.shape
        fps = cap.get(cv.CAP_PROP_FPS)
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        video_out = cv.VideoWriter("res/{}-out.mp4".format(index), fourcc, fps, (w,h), isColor=True)
        
        if ok:
            canvas = self.process_image(frame, bar_distance)
            video_out.write(canvas)
            
            while True:
                ok, frame = cap.read()
                
                if not ok:
                    print('Cannot read video file')
                    break
                
                canvas = self.process_image(frame, bar_distance)

                video_out.write(canvas)

        self.results["bar_distance"].append(np.std(bar_distance))
        cap.release()
        if video_out is not None:
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
            i = 0
            for file in files:
                self.results["src"].append(file)
                print("processing video {}".format(file))
                file_path = os.path.join(path, file)
                self.process_vid(file_path, i)
                i+=1

    def get_results(self):
        # pad self.results with None if not enough data
        max_data_len = 0
        for key in self.results:
            max_data_len = max(max_data_len, len(self.results[key]))
        
        for key in self.results:
            if len(self.results[key]) < max_data_len:
                self.results[key] += [None] * (max_data_len - len(self.results[key]))

        for key in self.results:
            if key != "src":
                avg = np.mean([x for x in self.results[key] if x is not None])
                sd = np.std([x for x in self.results[key] if x is not None])
                self.results[key].append(avg)
                self.results[key].append(sd)
        self.results["src"].append("average")
        self.results["src"].append("std_dev")
        
        df = pd.DataFrame(self.results)
        df.to_csv("res/results.csv")

if __name__ == "__main__":
    test = Testing()
    test.process_dir('training/hip', is_hip=True, img=True)
    #test.process_dir('training/knee', is_knee=True, img=True)
    #test.process_dir('training/video') # still need to test this
    #test.get_results()