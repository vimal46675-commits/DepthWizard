import os
import io
import json
import base64
import numpy as np
import cv2
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from depth_anything_v2.dpt import DepthAnythingV2

app = FastAPI(title="DepthWizard API", version="1.0.0")

# Enable CORS for frontend Vite dev server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_CONFIGS = {
    "vits": {"encoder": "vits", "features": 64, "out_channels": [48, 96, 192, 384]},
    "vitb": {"encoder": "vitb", "features": 128, "out_channels": [96, 192, 384, 768]},
    "vitl": {"encoder": "vitl", "features": 256, "out_channels": [256, 512, 1024, 1024]}
}

# Calibration defaults (from calibration_parameters.json)
DEFAULT_SCALE = 0.205471
DEFAULT_OFFSET = 106.224873

calib_params_path = "calibration_parameters.json"
if os.path.exists(calib_params_path):
    try:
        with open(calib_params_path, "r") as f:
            calib_data = json.load(f)
            DEFAULT_SCALE = float(calib_data.get("scale", DEFAULT_SCALE))
            DEFAULT_OFFSET = float(calib_data.get("offset", DEFAULT_OFFSET))
    except Exception as e:
        print(f"Warning loading calibration_parameters.json: {e}")

print("Initializing DepthWizard AI model...")
model = None

def get_model():
    global model
    if model is None:
        ckpt_path = "checkpoints/depth_anything_v2_vits.pth"
        if not os.path.exists(ckpt_path):
            raise FileNotFoundError(f"Checkpoint not found at {ckpt_path}")
        print(f"Loading DepthAnythingV2 (vits) on {DEVICE}...")
        m = DepthAnythingV2(**MODEL_CONFIGS["vits"])
        m.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
        m = m.to(DEVICE).eval()
        model = m
        print("Model loaded successfully!")
    return model

# Pre-load model on startup
try:
    get_model()
except Exception as e:
    print(f"Model pre-loading deferred or encountered notice: {e}")

def array_to_base64_png(img_uint8: np.ndarray) -> str:
    """Encodes a uint8 RGB or grayscale numpy array to base64 PNG data URL."""
    is_success, buffer = cv2.imencode(".png", img_uint8)
    if not is_success:
        raise ValueError("Could not encode image to PNG")
    b64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"

def compute_hillshade(elevation: np.ndarray, azimuth_deg: float = 315.0, altitude_deg: float = 45.0) -> np.ndarray:
    """Computes an analytical hillshade from an elevation grid."""
    azimuth_rad = np.radians(azimuth_deg)
    altitude_rad = np.radians(altitude_deg)
    
    # Gradients
    dy, dx = np.gradient(elevation)
    
    # Slope and Aspect
    slope = np.pi / 2.0 - np.arctan(np.sqrt(dx * dx + dy * dy))
    aspect = np.arctan2(-dx, dy)
    
    # Shading calculation
    shaded = (
        np.sin(altitude_rad) * np.sin(slope)
        + np.cos(altitude_rad) * np.cos(slope) * np.cos(azimuth_rad - aspect)
    )
    
    shaded = (shaded - shaded.min()) / (shaded.max() - shaded.min() + 1e-8) * 255.0
    return np.clip(shaded, 0, 255).astype(np.uint8)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "DepthWizard AI Engine",
        "device": DEVICE,
        "model_loaded": model is not None,
        "calibration": {
            "scale": DEFAULT_SCALE,
            "offset": DEFAULT_OFFSET
        }
    }

@app.post("/api/process")
async def process_image(file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        filename = file.filename or "uploaded_image"
        ext = os.path.splitext(filename)[1].lower()

        # Handle image loading
        img_bgr = None
        if ext in [".tif", ".tiff"]:
            try:
                import rasterio
                with rasterio.MemoryFile(content) as memfile:
                    with memfile.open() as dataset:
                        bands = dataset.read()
                        if bands.shape[0] >= 3:
                            # 3 or more bands, assume RGB
                            rgb = np.dstack((bands[0], bands[1], bands[2])).astype(np.float32)
                            # Normalize
                            low, high = np.percentile(rgb, 2), np.percentile(rgb, 98)
                            rgb = np.clip((rgb - low) / (high - low + 1e-8), 0, 1) * 255
                            img_bgr = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2BGR)
                        else:
                            # 1 band
                            gray = bands[0].astype(np.float32)
                            low, high = np.percentile(gray, 2), np.percentile(gray, 98)
                            gray = np.clip((gray - low) / (high - low + 1e-8), 0, 1) * 255
                            img_bgr = cv2.cvtColor(gray.astype(np.uint8), cv2.COLOR_GRAY2BGR)
            except Exception as e:
                print(f"Rasterio decode failed, falling back to PIL: {e}")

        if img_bgr is None:
            # Standard image load
            nparr = np.frombuffer(content, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_bgr is None:
            # Try PIL fallback
            try:
                pil_img = Image.open(io.BytesIO(content)).convert("RGB")
                img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to decode image: {e}")

        # Run model inference
        active_model = get_model()
        depth = active_model.infer_image(img_bgr) # 2D numpy array HxW
        
        # 1. Normalized Relative Depth Map Visualization
        depth_min, depth_max = float(depth.min()), float(depth.max())
        norm_depth = (depth - depth_min) / (depth_max - depth_min + 1e-8)
        
        # Colormap for depth (Spectral_r)
        cmap_depth = matplotlib.colormaps.get_cmap("Spectral_r")
        depth_colored = (cmap_depth(norm_depth)[:, :, :3] * 255).astype(np.uint8)
        depth_bgr = cv2.cvtColor(depth_colored, cv2.COLOR_RGB2BGR)
        depth_b64 = array_to_base64_png(depth_bgr)

        # 2. Calibrated DSM Elevation Map
        # Elevation = Scale * RelativeDepth + Offset
        elevation = DEFAULT_SCALE * depth + DEFAULT_OFFSET
        elev_min, elev_max = float(elevation.min()), float(elevation.max())
        elev_mean = float(elevation.mean())
        height_range = float(elev_max - elev_min)

        norm_elev = (elevation - elev_min) / (height_range + 1e-8)
        cmap_terrain = matplotlib.colormaps.get_cmap("terrain")
        dsm_colored = (cmap_terrain(norm_elev)[:, :, :3] * 255).astype(np.uint8)
        dsm_bgr = cv2.cvtColor(dsm_colored, cv2.COLOR_RGB2BGR)
        dsm_b64 = array_to_base64_png(dsm_bgr)

        # 3. Hillshade Map
        hillshade = compute_hillshade(elevation)
        hillshade_bgr = cv2.cvtColor(hillshade, cv2.COLOR_GRAY2BGR)
        hillshade_b64 = array_to_base64_png(hillshade_bgr)

        # 4. 3D Elevation Grid for TerrainViewer (downsample to 64x64 for smooth web 3D rendering)
        grid_size = 64
        resized_elevation = cv2.resize(elevation, (grid_size, grid_size), interpolation=cv2.INTER_AREA)
        # Normalize relative to mean for 3D displacement
        grid_elevation_list = resized_elevation.tolist()

        return JSONResponse({
            "success": True,
            "filename": filename,
            "dimensions": {"width": img_bgr.shape[1], "height": img_bgr.shape[0]},
            "depth_map": depth_b64,
            "dsm_map": dsm_b64,
            "hillshade_map": hillshade_b64,
            "stats": {
                "min_elevation": round(elev_min, 1),
                "max_elevation": round(elev_max, 1),
                "height_range": round(height_range, 1),
                "mean_elevation": round(elev_mean, 1),
                "resolution": "1.0 m"
            },
            "elevation_grid": grid_elevation_list
        })

    except Exception as e:
        print(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
