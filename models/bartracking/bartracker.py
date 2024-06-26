import numpy as np
import cv2 as cv
import sys
import os
# import tensorflow as tf
from collections import deque
from imutils.video import FPS

class BarTracker:
    def __init__(self, filename, output_dir = "output_vids/"):
        self.filename = filename
        self.model = 'ssdlite_mobilenet_v2_coco/frozen_inference_graph.pb'
        self.tracker = cv.TrackerKCF_create() # switch type of tracker potentially?
        self.vid = None
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.radius = 0
        self.output_dir = output_dir
        
        # Fix file path to be absolute of whatever the user inputs
        file_path = '/Users/miascarpati/Desktop/Northwestern/Junior/Q3/COMP_SCI_397_Sports/power-clean-form-coach/models/bar-tracking/input_vids/' + filename
        try:
            self.vid = cv.VideoCapture(filename)
        except:
            sys.exit('Cannot open video file. Please rerun program and make sure your video is an mp4 and is located in the correct directory.')

    def circle_to_bbox(self, center, radius):
        """
        Converts circle coordinates to bounding box coordinates.
        """

        x_min = center[0] - radius
        y_min = center[1] - radius
        x_max = center[0] + radius
        y_max = center[1] + radius
        return x_min, y_min, x_max, y_max
    
    def draw_circle(self, event, x, y, flags, param):
        """
        Draws a circle on the image.
        """
        if event == cv.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y
        elif event == cv.EVENT_MOUSEMOVE:
            if self.drawing == True:
                self.radius = int(np.sqrt((x - self.ix)**2 + (y - self.iy)**2))
        elif event == cv.EVENT_LBUTTONUP:
            self.drawing = False
            self.radius = int(np.sqrt((x - self.ix)**2 + (y - self.iy)**2))
            cv.circle(self.image, (self.ix, self.iy), self.radius, (0, 255, 0), 2)
    
    def detect_circles(self, image):
        self.image = image
        print("Draw a circle around the end of the barbell by clicking at the center and dragging to the edge. Press Enter when finished. Press Esc to exit. Draw as many times as needed.")
        cv.namedWindow('Select Object')
        cv.setMouseCallback('Select Object', self.draw_circle)
        while(1):
            cv.imshow('Select Object', self.image)
            k = cv.waitKey(1) & 0xFF
            if k == 13:
                cv.destroyAllWindows()
                return self.circle_to_bbox((self.ix, self.iy), self.radius)
            if k == 27:
                cv.destroyAllWindows()
                sys.exit('User exited program.')

    def track_bar(self, frontendCall = False, cx=None, cy=None, radius=None, sw=None, sh=None):
        """
        Tracks the bar in the video by forming bounding box around plates.
        """
        ok, frame = self.vid.read()
        if not ok:
            print('Cannot read video file')
            return
        
        # Set up output
        h, w, _ = frame.shape
        fps = self.vid.get(cv.CAP_PROP_FPS)
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        output = self.output_dir + os.path.basename(self.filename).split(".")[0] + '-out.mp4'
        video_out = cv.VideoWriter(output, fourcc, fps, (w,h), isColor=True)

        x_min, y_min, x_max, y_max = 0, 0, 0, 0

        # Generate bounding box coords based on frontend call or not (frontend will pass circle coords directly)
        if frontendCall:
            scale_x = w/640
            scale_y = h/580
            print("cx, scale_x", cx, scale_x)
            print("type of cx", type(cx))
            self.ix = cx * scale_x
            self.iy = cy * scale_y
            self.radius = radius
            x_min, y_min, x_max, y_max = self.circle_to_bbox((self.ix, self.iy), radius)
        
        else:
            x_min, y_min, x_max, y_max = self.detect_circles(frame)
            
        bounding_box = (int(x_min), int(y_min), int(x_max-x_min), int(y_max-y_min))
        print('bounding box:', bounding_box)

        self.tracker.init(frame, bounding_box)
        fps = FPS().start()
        num_frames = int(self.vid.get(cv.CAP_PROP_FRAME_COUNT))
        points = deque(maxlen=num_frames)

        for i in range(num_frames):
            ok, frame = self.vid.read()
            if not ok: break
            
            ok, bounding_box = self.tracker.update(frame)
            
            if ok:
                p1 = (int(bounding_box[0]), int(bounding_box[1]))
                p2 = (int(bounding_box[0] + bounding_box[2]), int(bounding_box[1] + bounding_box[3]))
                # Bounding box around plate
                cv.rectangle(frame, p1, p2, (0,0,255), 2, 1)
                center = (int((p1[0]+p2[0])/2), int((p1[1]+p2[1])/2))
                cv.circle(frame, center, 2, (0,0,255), -1)
                points.appendleft(center)
                for i in range(1, len(points)):
                    if points[i-1] is None or points[i] is None:
                        continue
                    cv.line(frame, points[i-1], points[i], (0,0,255), 2)
            else:
                cv.putText(frame, "Tracking failure detected", (100,80), cv.FONT_HERSHEY_SIMPLEX, 0.75,(255,0,0),2)
            
            # fps.update()
            # fps.stop()
            if frontendCall == False: cv.imshow('Tracking', frame)
            
            video_out.write(frame)

        self.vid.release()
        cv.destroyAllWindows()
        print("Bar tracking complete.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python3 bartracker.py <video_file>')
    filename = sys.argv[1]
    bar_tracker = BarTracker(filename)
    bar_tracker.track_bar()
    