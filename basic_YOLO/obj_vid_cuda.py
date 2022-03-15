'''
Reference:
https://thinkinfi.com/use-opencv-with-gpu-python/

Download cfg:
> wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg

Download weights:
> wget https://pjreddie.com/media/files/yolov3.weights

Dataset:
> wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names

'''
import cv2
import numpy as np

# windows / pi
#cap = cv2.VideoCapture(0)

# linux
cam_device="/dev/video0"
cap = cv2.VideoCapture(cam_device)

# capture from file
#vid = "path/to/video.mp4"
#cap = cv2.VideoCapture(vid)

# Load Yolo
yolo_weight = "model/yolov3.weights"
yolo_config = "model/yolov3.cfg"
coco_labels = "model/coco.names"
net = cv2.dnn.readNet(yolo_weight, yolo_config)


# The Difference:

# Offload Work onto GPU
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)


classes = []
with open(coco_labels, "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))
 
# Defining desired shape
fWidth = 256
fHeight = 256


while True:
    read_ok, img = cap.read()
 
    height, width, channels = img.shape
 
    # Detecting objects
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
 
    # Showing informations on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
 
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
 
    font = cv2.FONT_HERSHEY_DUPLEX
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence_label = int(confidences[i] * 100)
            color = colors[i]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, f'{label, confidence_label}', (x-25, y + 75), font, 2, color, 2)
 
    cv2.imshow("Image", img)
    # Close video window by pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break