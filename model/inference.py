from os.path import dirname, abspath, join
from os import chdir
from sys import executable
from json import dumps
from subprocess import run
from model.utils import process_detections

yolov5_dir = join(dirname(abspath(__file__)), "pretrained/yolov5")
labels_dir = join(dirname(abspath(__file__)), "pretrained/yolov5/runs/detect/exp/labels")
images_dir = join(dirname(abspath(__file__)), "pretrained/images")

def inference() -> str:
	chdir(yolov5_dir)
	cmd = (
		f"\"{executable}\" detect.py --weights ../runs/best.pt "
		f"--img 640 --conf 0.01 --iou 0.4 "
		f"--source ../images --save-txt --save-conf --exist-ok"
	)
	run(cmd, shell=True, check=True)

	records = process_detections(labels_dir, images_dir)
	return dumps(records)
