import numpy as np
import cv2 as cv
import sys
import tensorflow as tf
from collections import deque
from imutils.video import FPS

class BarTracker:
    def __init__(self, filename: str):
        self.model = 'ssdlite_mobilenet_v2_coco/frozen_inference_graph.pb'
        self.tracker = cv.TrackerKCF_create() # switch type of tracker potentially?
        self.vid = cv.VideoCapture(filename)

    def generate_bounding_box(self, image: str):
        """
        Generates a bounding box around the detected object in the image.
        Application: Bounding box will be used to track the object in the video.
        Video frames will be processed and passed into this function as images.
        """
        with tf.io.gfile.GFile(self.model, 'rb') as f: # change to the path of the model
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())
        
        with tf.compat.v1.Session() as sess:
            # Restore session
            sess.graph.as_default()
            tf.import_graph_def(graph_def, name='')

            # Read and preprocess an image.
            # img = cv.imread(image)
            # rows = img.shape[0]
            # cols = img.shape[1]
            # inp = cv.resize(img, (300, 300))
            # inp = inp[:, :, [2, 1, 0]]  # BGR2RGB
            image_dim = np.expand_dims(image, axis=0)

            # Run the model
            out = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                            sess.graph.get_tensor_by_name('detection_scores:0'),
                            sess.graph.get_tensor_by_name('detection_boxes:0'),
                            sess.graph.get_tensor_by_name('detection_classes:0')],
                        feed_dict={'image_tensor:0': image_dim})

            # Get bounding box coordinates
            y_min, x_min, y_max, x_max = np.squeeze(out[2])[0]
            img_height, img_width, _ = image.shape
            y_min = int(y_min * img_height)
            x_min = int(x_min * img_width)
            y_max = int(y_max * img_height)
            x_max = int(x_max * img_width)

            return x_min, y_min, x_max, y_max

            # num_detections = int(out[0][0])
            # for i in range(num_detections):
            #     classId = int(out[3][0][i])
            #     score = float(out[1][0][i])
            #     bbox = [float(v) for v in out[2][0][i]]
            #     if score > 0.3:
            #         x = bbox[1] * cols
            #         y = bbox[0] * rows
            #         right = bbox[3] * cols
            #         bottom = bbox[2] * rows
            #         cv.rectangle(img, (int(x), int(y)), (int(right), int(bottom)), (125, 255, 51), thickness=2)

    def track_bar(self):
        """
        Tracks the bar in the video by forming bounding box around plates.
        """
        ok, frame = self.vid.read()
        if not ok:
            print('Cannot read video file')
            return
        
        # Set up output
        h, w, layers = frame.shape
        fps = self.vid.get(cv.CAP_PROP_FPS)
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        video_out = cv.VideoWriter("output_vids/out.mp4", fourcc, fps, (w,h), isColor=True)

        # Get bounding box for the first frame
        x_min, y_min, x_max, y_max = self.generate_bounding_box(frame)
        bounding_box = (x_min, y_min, x_max-x_min, y_max-y_min)

        self.tracker.init(frame, bounding_box)
        fps = FPS().start()
        points = deque(maxlen=int(self.vid.get(cv.CAP_PROP_FRAME_COUNT)))

        while ok:
            ok, frame = self.vid.read()
            if not ok:
                break
            ok, bounding_box = self.tracker.update(frame)
            if ok:
                p1 = (int(bounding_box[0]), int(bounding_box[1]))
                p2 = (int(bounding_box[0] + bounding_box[2]), int(bounding_box[1] + bounding_box[3]))
                cv.rectangle(frame, p1, p2, (0,255,0), 2, 1)
                # Draw centroid
                center = (int((p1[0]+p2[0])/2), int((p1[1]+p2[1])/2))
                cv.circle(frame, center, 2, (0,255,0), -1)
                points.appendleft(center)
                for i in range(1, len(points)):
                    if points[i-1] is None or points[i] is None:
                        continue
                    cv.line(frame, points[i-1], points[i], (0,255,0), 2)
            else:
                cv.putText(frame, "Tracking failure detected", (100,80), cv.FONT_HERSHEY_SIMPLEX, 0.75,(0,255,0),2)
            
            fps.update()
            fps.stop()
            cv.imshow('Tracking', frame)
            video_out.write(frame)
            key = cv.waitKey(1) & 0xFF

        self.vid.release()
        cv.destroyAllWindows()

if __name__ == '__main__':
    filename = sys.argv[1]
    bar_tracker = BarTracker(filename)
    bar_tracker.track_bar()
    