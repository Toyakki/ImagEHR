# Containing the helper functions to convert YOLO output into prompt
from PIL import Image
from typing import Dict, Optional
import os
import glob
import numpy as np

INPUT_VARIABLE = "MI"

CLASS_MAPPING = {
    0: {"QNAM": "AORTENLG", "QLABEL": "Aortic enlargement"},
    1: {"MITESTCD": "ATELECTASIS", "MITEST": "Atelectasis"},
    2: {"QNAM": "CALCIFIC", "QLABEL": "Calcification"},
    3: {"MITESTCD": "CARDIOMEGALY", "MITEST": "Cardiomegaly"},
    4: {"MITESTCD": "CONSOLIDATION", "MITEST": "Consolidation"},
    5: {"QNAM": "ILD", "QLABEL": "Interstitial lung disease"},
    6: {"QNAM": "INFILTRA", "QLABEL": "Infiltration"},
    7: {"QNAM": "LUNGOPAC", "QLABEL": "Lung opacity"},
    8: {"MITESTCD": "NODULE", "MITEST": "Nodule/Mass"},
    9: {"QNAM": "OTHLESN", "QLABEL": "Other lesion"},
    10: {"RSTESTCD": "PLEUREFF", "RSTEST": "Pleural effusion", "RSCAT": "CHEST X-RAY"},
    11: {"RSTESTCD": "PLEURTHK", "RSTEST": "Pleural thickening", "RSCAT": "CHEST X-RAY"},
    12: {"RSTESTCD": "PNMTHRX", "RSTEST": "Pneumothorax", "RSCAT": "CHEST X-RAY"},
    13: {"QNAM": "PULMFIB", "QLABEL": "Pulmonary fibrosis"},
    14: {"RSTESTCD": "NOFIND", "RSTEST": "No finding", "RSCAT": "CHEST X-RAY"},
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

def convert_to_dict(detection_result, width: int, height: int) -> Optional[Dict[str, str]]:
    """
    Convert detection output into a structured CDISC-compliant dictionary.
    Supports MI, RS, and SUPPQUAL mappings.
    """
    class_id, conf, x_center, y_center, w_norm, h_norm = detection_result

    if conf <= CUT_OFF:
        return None

    voc_bbox = yolo2voc(height, width, np.array([[x_center, y_center, w_norm, h_norm]]))[0]

    xmin, ymin, xmax, ymax = voc_bbox

    dpi = 300
    pixel_spacing_cm = 2.54 / dpi

    width_cm = (xmax - xmin) * pixel_spacing_cm
    height_cm = (ymax - ymin) * pixel_spacing_cm
    miorres = f"{width_cm:.2f} x {height_cm:.2f} cm^2"
    miloc = compute_miloc(xmin, ymin, xmax, ymax, width, height)

    # Get mapping and determine type
    mapping = CLASS_MAPPING.get(int(class_id))
    if not mapping:
        return None  # Unknown class_id

    structured = {}

    # Determine mapping type
    if "MITESTCD" in mapping:
        structured = {
            "MITESTCD": mapping["MITESTCD"],
            "MIORRES": miorres,
            "MILOC": miloc,
            "MIMETHOD": "x-ray",
            "MIEVAL": "Radiologist"
        }
    elif "RSTESTCD" in mapping:
        structured = {
            "RSTESTCD": mapping["RSTESTCD"],
            "RSORRES": "Positive",
            "RSCAT": "CHEST X-RAY",
        }
    elif "QNAM" in mapping:
        structured = {
            "QNAM": mapping["QNAM"],
            "QLABEL": mapping["QLABEL"],
            "QVAL": "Positive",
            "RDOMAIN": "RS",
        }
    else:
        return None

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
        if not os.path.exists(image_file):
            image_file = os.path.join(images_dir, image_id + '.webp')
        
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
            structured_records.append(record)
    return structured_records
