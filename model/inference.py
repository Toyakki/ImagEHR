from utils import yolo2voc, process_detections


import json
from glob import glob
import shutil, os
import subprocess
import matplotlib.pyplot as plt
from tqdm import tqdm  # If not in a notebook, consider using tqdm.tqdm
from PIL import Image  # For reading image dimensions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
yolov5_dir = os.path.join(BASE_DIR, 'pretrained/yolov5')
DEBUG = True
# Adjust this path if necessary, e.g., using os.path.join(yolov5_dir, 'runs/train/exp/weights/best.pt')
weights_dir = os.path.join(yolov5_dir, 'runs/train/exp/weights/best.pt')
images_dir = os.path.join(BASE_DIR, 'data')
labels_dir = os.path.join(yolov5_dir, 'runs/detect/exp/labels')
    
def inference(images_dir, weights_dir):
    # Change working directory to where detect.py is located
    os.chdir(yolov5_dir)
    
    # Construct and execute the detection command
    cmd = (
        f"python detect.py --weights {weights_dir} "
        f"--img 640 --conf 0.01 --iou 0.4 "
        f"--source {images_dir} --save-txt --save-conf --exist-ok"
    )
    subprocess.run(cmd, shell=True, check=True)
    records = process_detections(labels_dir, images_dir)
    with open('detection_results.json', 'w') as f:
        json.dump(records, f)

if __name__ == '__main__':
    inference(images_dir, weights_dir)
    print('Inference complete. Detection results saved to detection_results.json')
