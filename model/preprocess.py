import os
import glob
import argparse
import numpy as np
from PIL import Image

import pydicom

def process_dicom(dcm_path, output_size=(1024, 1024)):
    """
    Process a DICOM file and return a numpy array of the image.
    """
    ds = pydicom.dcmread(dcm_path)
    image = ds.pixel_array.astype(np.float32)
    
    if hasattr(ds, 'RescaleSlope') and hasattr(ds, 'RescaleIntercept'):
        image = image * ds.RescaleSlope + ds.RescaleIntercept
    
    min_val, max_val = np.min(image), np.max(image)
    if max_val > min_val:
      image = (image - min_val) / (max_val - min_val) * 255.0
    else:
      image = np.zeros_like(image)
    image = image.astype(np.uint8)
    
    pil_image = Image.fromarray(image).convert('RGB')
    pil_image = pil_image.resize(output_size, Image.Resampling.LANCZOS)
    return pil_image

def process_image(image_path, output_size=(1024, 1024)):
    """
    Process an image file. If the extension indicates DICOM, use process_dicom;
    otherwise use PIL directly.
    """
    ext = os.path.splitext(image_path)[1].lower()
    if ext in ['.dcm', '.dicom']:
        return process_dicom(image_path, output_size)
    else:
        pil_img = Image.open(image_path)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        pil_img = pil_img.resize(output_size, Image.Resampling.LANCZOS)
        return pil_img

def preprocess_images(input_dir, output_dir, output_size=(1024, 1024)):
    """
    Process all images in the input directory and save the preprocessed images
    to the output directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for image_path in glob.glob(os.path.join(input_dir, "*")):
        try:
            processed_img = process_image(image_path, output_size)
            # Save the processed image as PNG.
            base_name = os.path.basename(image_path)
            base_name = os.path.splitext(base_name)[0] + '.png'
            out_path = os.path.join(output_dir, base_name)
            processed_img.save(out_path)
            print(f"Processed and saved: {out_path}")
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Preprocess chest X-ray images for YOLO input (resize to 1024x1024)"
    )
    parser.add_argument("--input_dir", type=str, required=True,
                        help="Directory containing input images (DCM, JPG, PNG, etc.)")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Directory to save preprocessed images")
    parser.add_argument("--size", type=int, default=1024,
                        help="Output image size (square), default is 1024")
    args = parser.parse_args()

    output_dimensions = (args.size, args.size)
    preprocess_images(args.input_dir, args.output_dir, output_dimensions)

# Use case:
# python preprocess.py --input_dir pretrained/test_dicom --output_dir pretrained/images --size 1024