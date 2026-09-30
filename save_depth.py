import os
import argparse

import cv2
import numpy as np
import torch

from depth_anything_v2.dpt import DepthAnythingV2


# ============================================================
# DEPTHWIZARD - MEMBER 1
# Single-Image Relative Depth Extraction
# ============================================================


# ------------------------------------------------------------
# Model configuration
# ------------------------------------------------------------

ENCODER = "vits"
INPUT_SIZE = 518

MODEL_CONFIGS = {
    "vits": {
        "encoder": "vits",
        "features": 64,
        "out_channels": [48, 96, 192, 384],
    }
}

CHECKPOINT = "checkpoints/depth_anything_v2_vits.pth"


# ------------------------------------------------------------
# Device selection
# ------------------------------------------------------------

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ------------------------------------------------------------
# Load Depth Anything V2
# ------------------------------------------------------------

def load_model():

    print("----------------------------------------")
    print("Loading Depth Anything V2...")
    print("----------------------------------------")

    print("Using device:", DEVICE)

    if DEVICE == "cuda":
        print("GPU:", torch.cuda.get_device_name(0))

    model = DepthAnythingV2(
        **MODEL_CONFIGS[ENCODER]
    )

    model.load_state_dict(
        torch.load(
            CHECKPOINT,
            map_location="cpu"
        )
    )

    model = model.to(DEVICE).eval()

    print("Model loaded successfully!")
    print()

    return model


# ------------------------------------------------------------
# Load input image
# ------------------------------------------------------------

def load_image(image_path):

    print("----------------------------------------")
    print("Loading image...")
    print("----------------------------------------")

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    print("Image:", image_path)
    print("Image size:", image.shape)
    print()

    return image


# ------------------------------------------------------------
# Generate depth
# ------------------------------------------------------------

def generate_depth(model, image):

    print("----------------------------------------")
    print("Generating relative depth map...")
    print("----------------------------------------")

    depth = model.infer_image(
        image,
        INPUT_SIZE
    )

    print("Depth generated successfully!")
    print("Depth shape:", depth.shape)
    print("Minimum depth:", float(depth.min()))
    print("Maximum depth:", float(depth.max()))
    print("Mean depth:", float(depth.mean()))
    print()

    return depth


# ------------------------------------------------------------
# Save numerical depth
# ------------------------------------------------------------

def save_raw_depth(depth, output_path):

    np.save(
        output_path,
        depth.astype(np.float32)
    )

    print("Raw depth saved:")
    print(output_path)
    print()


# ------------------------------------------------------------
# Save visualization
# ------------------------------------------------------------

def save_visualization(depth, output_path):

    # Normalize relative depth to 0-255
    depth_normalized = cv2.normalize(
        depth,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )

    depth_normalized = depth_normalized.astype(
        np.uint8
    )

    cv2.imwrite(
        output_path,
        depth_normalized
    )

    print("Depth visualization saved:")
    print(output_path)
    print()


# ------------------------------------------------------------
# Main program
# ------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="DepthWizard - Monocular Depth Extraction"
    )

    parser.add_argument(
        "image",
        help="Path to input JPG, JPEG, PNG, TIF or TIFF image"
    )

    args = parser.parse_args()

    image_path = args.image

    # Check supported extensions
    supported_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".tif",
        ".tiff"
    )

    extension = os.path.splitext(
        image_path
    )[1].lower()

    if extension not in supported_extensions:
        raise ValueError(
            "Unsupported image format. "
            "Use JPG, JPEG, PNG, TIF or TIFF."
        )

    # Create output directories
    raw_output_dir = os.path.join(
        "results",
        "depth_maps"
    )

    visualization_output_dir = os.path.join(
        "results",
        "visualizations"
    )

    os.makedirs(
        raw_output_dir,
        exist_ok=True
    )

    os.makedirs(
        visualization_output_dir,
        exist_ok=True
    )

    # Get filename without extension
    filename = os.path.splitext(
        os.path.basename(image_path)
    )[0]

    # Output filenames
    raw_depth_path = os.path.join(
        raw_output_dir,
        filename + "_depth.npy"
    )

    visualization_path = os.path.join(
        visualization_output_dir,
        filename + "_depth.png"
    )

    # Load model
    model = load_model()

    # Load image
    image = load_image(image_path)

    # Generate depth
    depth = generate_depth(
        model,
        image
    )

    # Save raw numerical depth
    save_raw_depth(
        depth,
        raw_depth_path
    )

    # Save visualization
    save_visualization(
        depth,
        visualization_path
    )

    # Final information
    print("----------------------------------------")
    print("DEPTHWIZARD COMPLETED SUCCESSFULLY")
    print("----------------------------------------")

    print("Input:")
    print(image_path)

    print()

    print("Raw depth:")
    print(raw_depth_path)

    print()

    print("Visualization:")
    print(visualization_path)

    print()

    print("Device used:", DEVICE)

    if DEVICE == "cuda":
        print(
            "GPU used:",
            torch.cuda.get_device_name(0)
        )

    print("----------------------------------------")


if __name__ == "__main__":
    main()