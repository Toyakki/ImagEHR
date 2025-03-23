from os.path import dirname, abspath, join, exists
from os import chdir
from sys import executable
from json import dumps
from subprocess import run
from model.utils import process_detections
from os import makedirs
from os.path import join, dirname, abspath, exists

if not exists(join(dirname(abspath(__file__)), "pretrained/runs/best.pt")):
	print("Missing file /model/pretrained/runs/best.pt; downloading from GH releases")
	import urllib.request

	dest_dir = join(dirname(abspath(__file__)), "pretrained/runs")
	if not exists(dest_dir):
		makedirs(dest_dir)

	url = "https://github.com/Toyakki/ImagEHR/releases/download/1.1.1/best.pt"
	dest_file = join(dest_dir, "best.pt")
	urllib.request.urlretrieve(url, dest_file)
	print("Download complete.")

yolov5_dir = join(dirname(abspath(__file__)), "pretrained/yolov5")
labels_dir = join(dirname(abspath(__file__)), "pretrained/yolov5/runs/detect/exp/labels")
images_dir = join(dirname(abspath(__file__)), "pretrained/images")

def inference() -> str:
	"""
	Create folder /model/pretrained/images if not exists.
	Delete any existing images in /model/pretrained/images if present.
	Put your images (.png, .jpg, .webp) in /model/pretrained/images.
	Then run inference(). Exceptions may be raised, so catch them.
	If successful, you will get a JSON string returned containing results.
	"""
	chdir(yolov5_dir)
	cmd = (
		f"\"{executable}\" detect.py --weights ../runs/best.pt "
		f"--img 640 --conf 0.01 --iou 0.4 "
		f"--source ../images --save-txt --save-conf --exist-ok"
	)
	run(cmd, shell=True, check=True)

	records = process_detections(labels_dir, images_dir)
	return dumps(records, indent=2)
