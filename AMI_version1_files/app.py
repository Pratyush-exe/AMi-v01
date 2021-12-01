from cv2 import cv2
import torch

model = torch.hub.load(r'C:\Users\KIIT\Downloads\yolov5-master\yolov5-master', 'custom', path='best (1).pt',
                       force_reload=True, source='local')
camera = cv2.VideoCapture(0)


def getColor(name):
    if name == "RBC":
        return 255, 0, 0
    elif name == "WBC":
        return 0, 0, 255
    else:
        return 0, 255, 255


while True:
    _, img = camera.read()
    height, width, channels = img.shape

    class_ids = []
    id = 0
    confidences = []
    labels = []
    boxes = []
    results = model([img])
    res = results.pandas().xyxy[0]
    for index, row in res.iterrows():
        if row['confidence'] >= 0.6:
            class_ids.append(id)
            id += 1
            confidences.append(row['confidence'])
            boxes.append([row['xmin'], row['xmax'], row['ymin'], row['ymax']])
            labels.append(row['name'])

    font = cv2.FONT_HERSHEY_PLAIN
    for i in range(len(class_ids)):
        xmin, xmax, ymin, ymax = boxes[i]
        color = getColor(labels[i])
        cv2.rectangle(img, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 1)
        cv2.putText(img, labels[i] + " " + str(round(confidences[i], 2)), (int(xmin), int(ymin) - 3), font, 1,
                    color, 2)
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == 27:
        break

camera.release()
cv2.destroyAllWindows()
