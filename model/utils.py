# Containing the helper functions to convert YOLO output into prompt
import os
import glob
import numpy as np
import json

from PIL import Image
from typing import Dict, Optional

CLASS_MAPPING = {
    0: {"MITESTCD": "AORTIC_ENLARGEMENT", "MITEST": "Aortic enlargement"},
    1: {"MITESTCD": "ATELECTASIS", "MITEST": "Atelectasis"},
    2: {"MITESTCD": "CALCIFICATION", "MITEST": "Calcification"},
    3: {"MITESTCD": "CARDIOMEGALY", "MITEST": "Cardiomegaly"},
    4: {"MITESTCD": "CONSOLIDATION", "MITEST": "Consolidation"},
    5: {"MITESTCD": "ILD", "MITEST": "ILD"},
    6: {"MITESTCD": "INFILTRATION", "MITEST": "Infiltration"},
    7: {"MITESTCD": "LUNG_OPACITY", "MITEST": "Lung opacity"},
    8: {"MITESTCD": "NODULE", "MITEST": "Nodule/Mass"},
    9: {"MITESTCD": "OTHER_LESION", "MITEST": "Other lesion"},
    10: {"MITESTCD": "PLEURAL_EFFUSION", "MITEST": "Pleural effusion"},
    11: {"MITESTCD": "PLEURAL_THICKENING", "MITEST": "Pleural thickening"},
    12: {"MITESTCD": "PNEUMOTHORAX", "MITEST": "Pneumothorax"},
    13: {"MITESTCD": "PULMONARY_FIBROSIS", "MITEST": "Pulmonary fibrosis"},
    14: {"MITESTCD": "NO_FINDING", "MITEST": "No finding"}
}

CUT_OFF = 0.6    # Confidence cutoff for considering a detection

def yolo2voc(image_height, image_width, bboxes) -> np.ndarray:
    """
    Convert YOLO format (normalized [x_center, y_center, width, height]) 
    to VOC format ([x1, y1, x2, y2] in absolute pixel values).
    """
    bboxes = bboxes.copy().astype(float)
    
    # Convert normalized values to absolute values
    bboxes[..., [0, 2]] = bboxes[..., [0, 2]] * image_width
    bboxes[..., [1, 3]] = bboxes[..., [1, 3]] * image_height
    
    # Convert center coordinates to top-left coordinates
    bboxes[..., [0, 1]] = bboxes[..., [0, 1]] - bboxes[..., [2, 3]] / 2
    bboxes[..., [2, 3]] = bboxes[..., [0, 1]] + bboxes[..., [2, 3]]
    
    return bboxes

def compute_miloc(xmin, ymin, xmax, ymax, image_width, image_height) -> str:
    center_x = (xmin + xmax) / 2
    center_y = (ymin + ymax) / 2
    side = "Left" if center_x < image_width / 2 else "Right"
    if center_y < image_height / 3:
        vertical = "upper"
    elif center_y > 2 * image_height / 3:
        vertical = "lower"
    else:
        vertical = "middle"
    return f"{vertical} {side} lobe"

def convert_to_dict(detection_result, width, height) -> Optional[Dict[str, str]]:
    """
    Convert the detection output into a structured dictionary.    
    """
    class_id, conf, x_center, y_center, w_norm, h_norm = detection_result
    voc_bbox = yolo2voc(height, width, np.array([[x_center, y_center, w_norm, h_norm]]))[0]
    xmin, ymin, xmax, ymax = voc_bbox
    
    widght_px = xmax - xmin
    miorres = f"{widght_px:.1f} px"
    if conf > CUT_OFF:
        miloc = compute_miloc(xmin, ymin, xmax, ymax, width, height)
        mapping = CLASS_MAPPING.get(int(class_id), {"MITESTCD": "UNKNOWN", "MITEST": "Unknown"})
        structured = {
            "MITESTCD": mapping["MITESTCD"],
            "MITEST": mapping["MITEST"],
            "MIORRES": miorres,
            "MILOC": miloc,
            "MIMETHOD": "X-ray",
            "MIEVAL": "Radiologist"
        }
    else:
        structured = None
    return structured

def process_detections(labels_dir, images_dir):
    """
    Process all YOLO output text files in the labels dictoinary and convert
    detection into structured records.
    """
    structured_records = []
    label_files = glob.glob(os.path.join(labels_dir, '*.txt'))
    
    for label_file in label_files:
        image_id = os.path.basename(label_file).split('.')[0]
        image_file = os.path.join(images_dir, image_id + '.png')
        if not os.path.exists(image_file):
            image_file = os.path.join(images_dir, image_id + '.jpg')
        
        with Image.open(image_file) as img:
            width, height = img.size
        
        with open(label_file, 'r') as f:
            content = f.read().strip().replace('\n', ' ')
        
        if not content:
            detection = [14, 1, 0, 0, 1, 1]
            record = convert_to_dict(detection, width, height)
        else:
            values = list(map(float, content.split()))
            for i in range(0, len(values), 6):
                detection = values[i:i+6]
                record = convert_to_dict(detection, width, height)
        
        if record:
            record["IMAGEID"] = image_id
            structured_records.append(record)
    return structured_records
