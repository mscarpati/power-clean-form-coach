import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('/Users/miascarpati/Desktop/Northwestern/Junior/Q3/COMP_SCI_397_Sports/power-clean-form-coach/models/posedetection/pytorch-openpose')
import src
from src import util
from src.body import Body

OPTIMAL_KNEE_ANGLE = 95
KNEE_SD = 25
OPTIMAL_HIP_ANGLE_A = 168
HIP_SD = 8.5

####### HOW LIFTS ARE EVALUATED #######
## Lifter's angles/values are compared to optimal angles/values above
## Error margin will be defined as roughly 110% of the stdev of optimal
## Area of error will be circled/highlighted on a color scheme in accordance with how unoptimal it is (red-orange-yellow)
## Error messages will be displayed based on the error margin (put in separate file probably can be .txt)

class PoseDetector():
    def __init__(self):
        self.body_est = Body('../model/body_pose_model.pth')
        self.video = None

        self.knee_angle_L = float('inf')
        self.knee_coord_L = None
        self.hip_angle_L = 0
        self.hip_coord_L = []
        self.knee_angle_R = float('inf')
        self.knee_coord_R = None
        self.hip_angle_R = 0
        self.hip_coord_R = []
        self.frame_buffer = []

    def calculate_knee(self, candidate, height):
        """
        Calculates knee angle if bar is in the appropriate location. Returns boolean.
        Detected when bar is line with shoulder (hand key points are roughly near shoulder).
        Must also detect if the lifter is in the process of squatting. Can do by ensuring knee angle is not increasing.
        Only works on front 3/4 angle video.
        """
        threshold = (1/50)*height
        if len(candidate) > 0:
            coordinates = np.delete(candidate, (2, 3), 1)
            if len(coordinates) > 15:
                # Bar should be by shoulders - y coordinates should be within 1/16 of frame height of each other
                if ((abs(coordinates[4][1] - coordinates[2][1]) <= threshold or 
                    abs(coordinates[7][1] - coordinates[5][1]) <= threshold or
                    abs(coordinates[3][1] - coordinates[2][1]) <= threshold or
                    abs(coordinates[6][1] - coordinates[5][1]) <= threshold)):
                    
                    if ((self.knee_coord_L is not None and self.knee_coord_R is not None) and 
                        (abs(self.knee_coord_L[1] - coordinates[10][1]) <= threshold or abs(self.knee_coord_R[1] - coordinates[13][1] <= threshold)) or 
                        (self.knee_coord_L is None or self.knee_coord_R is None)):
                    # Make sure knee angle is not increasing
                        left = util.get_angle(coordinates[9], coordinates[10], coordinates[11])
                        right = util.get_angle(coordinates[12], coordinates[13], coordinates[14])

                        if ((left < self.knee_angle_L or right < self.knee_angle_R) and 
                            (left >= 70 and right >= 70)):
                            #print("calculating knee angle")
                            self.knee_angle_L = left
                            #print("Left knee angle: ", left)
                            self.knee_coord_L = coordinates[10] # corresponds to 9
                            self.knee_angle_R = right
                            #print("Right knee angle: ", right)
                            self.knee_coord_R = coordinates[13] # corresponds to 13
                            return True
                    
        return False


    def calculate_hip(self, candidate, height):
        """
        Calculates hip angle if bar is at appropriate location.
        Runs when bar is slightly below hips.
        """
        threshold = (1/100)*height
        if len(candidate) > 0:
            coordinates = np.delete(candidate, (2, 3), 1)
            # Check if bar is around hips - y coordinates should be within 1/16 of frame height of each other
            if ((abs(coordinates[4][1] - coordinates[8][1]) <= threshold 
                or abs(coordinates[7][1] - coordinates[11][1]) <= threshold) and 
                (self.knee_angle_L == float('inf') or self.knee_angle_R == float('inf'))):
                #print("left hand: ", coordinates[4])
                #print("calculating hip angle")
                # self.hip_angle_L = util.get_angle(coordinates[2], coordinates[9], coordinates[10])
                # self.hip_coord_L = coordinates[9]
                # self.hip_angle_R = util.get_angle(coordinates[2], coordinates[12], coordinates[13])
                # self.hip_coord_R = coordinates[12]
                self.hip_angle_L = util.get_angle(coordinates[1], coordinates[8], coordinates[9])
                self.hip_coord_L = coordinates[8]
                self.hip_angle_R = util.get_angle(coordinates[1], coordinates[11], coordinates[12])
                self.hip_coord_R = coordinates[11]
                return True
            
        return False
            
    def draw(self, frame):
        """
        Compares user knee and hip angles to optimal angles. Draws on resulting video accordingly.
        Yellow = deviates by 1*SD - 2*SD
        Orange = deviates by 2*SD - 3*SD
        Red = deviates by >3SD
        """
        knee = ''
        hip = ''

        knee_dev = min(abs(OPTIMAL_KNEE_ANGLE - self.knee_angle_L), abs(OPTIMAL_KNEE_ANGLE - self.knee_angle_R))
        if knee_dev == abs(OPTIMAL_KNEE_ANGLE - self.knee_angle_L): knee = 'left'
        else: knee = 'right'

        hip_dev = min(abs(OPTIMAL_HIP_ANGLE_A - self.hip_angle_L), abs(OPTIMAL_HIP_ANGLE_A - self.hip_angle_R))
        if hip_dev == abs(OPTIMAL_HIP_ANGLE_A - self.hip_angle_L): hip = 'left'
        else: hip = 'right'
        
        knee_color, hip_color = None, None
        
        if knee_dev <= 2*KNEE_SD and knee_dev > KNEE_SD: 
            knee_color = (0, 255, 255) # open cv uses BGR
        elif knee_dev <= 3*KNEE_SD:
            knee_color = (0, 140, 255)
        else:
            knee_color = (0, 0, 255)

        if hip_dev <= 2*HIP_SD and hip_dev > HIP_SD:
            hip_color = (0, 255, 255)
        elif hip_dev <= 3*HIP_SD:
            hip_color = (0, 140, 255)
        else:
            hip_color = (0, 0, 255)

        if knee_color is not None:
            # draw circle around knee - center point should be the knee coordinate
            if knee == 'left':
                cv.circle(frame, (int(self.knee_coord_L[0]), int(self.knee_coord_L[1])), 30, knee_color, 2)
            else:
                cv.circle(frame, (int(self.knee_coord_R[0]), int(self.knee_coord_R[1])), 30, knee_color, 2)

        if hip_color is not None:
            # draw circle around hip - center point should be the hip coordinate
            if hip == 'left':
                cv.circle(frame, (int(self.hip_coord_L[0]), int(self.hip_coord_L[1])), 30, hip_color, 2)
            else:
                cv.circle(frame, (int(self.hip_coord_R[0]), int(self.hip_coord_R[1])), 30, hip_color, 2)

        return frame


    def process_image(self, frame, is_single=False):
        h, w, _ = frame.shape
        candidate, subset = self.body_est(frame)
        marked_up = util.draw_bodypose(frame, candidate, subset)
        
        knee = self.calculate_knee(candidate, h)
        hip = self.calculate_hip(candidate, h)

        # check work - show image if detect hip or detect knee
        if knee or hip or is_single:
            #plt.imshow(marked_up[:, :, [2, 1, 0]])
            #plt.show()
            if is_single: cv.imwrite("res/out.png", marked_up)

        if not is_single:
            return marked_up
        else:
            plt.imshow(marked_up[:, :, [2, 1, 0]])
            plt.show()
                
    def process_vid(self, video):
        self.video = video
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
        video_out = cv.VideoWriter("res/{}-out.mp4".format(video), fourcc, fps, (w,h), isColor=True)
        
        if ok:
            canvas = self.process_image(frame)
            self.frame_buffer.append(canvas)
            video_out.write(canvas)
            
            while True:
                ok, frame = cap.read()
                
                if not ok:
                    break
                
                canvas = self.process_image(frame, bar_distance)
                self.frame_buffer.append(canvas)

        for frame in self.frame_buffer:
            updated = self.draw(frame)
            video_out.write(updated)

        cap.release()
        if video_out is not None:
            video_out.release()
        cv.destroyAllWindows()
        print("Video processed")
        print("Knee Angle L: ", self.knee_angle_L)
        print("Knee Angle R: ", self.knee_angle_R)
        print("Hip Angle L: ", self.hip_angle_L)
        print("Hip Angle R: ", self.hip_angle_R)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 posedetector.py <video_file>')
    filename = sys.argv[1]
    eval = PoseDetector()
    eval.process_vid(filename)