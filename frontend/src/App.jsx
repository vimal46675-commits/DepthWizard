import { useState } from "react";
import "./App.css";
import TerrainViewer from "./components/TerrainViewer";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [error, setError] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [showTerrain, setShowTerrain] = useState(false);
  const [showImageLightbox, setShowImageLightbox] = useState(false);
  const [resultsData, setResultsData] = useState(null);
  const [processingStep, setProcessingStep] = useState(1);

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (!file) return;

    setError("");
    setShowResults(false);
    setResultsData(null);

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/tiff",
    ];

    if (!allowedTypes.includes(file.type)) {
      setSelectedFile(null);
      setPreviewUrl("");
      setError(
        "Unsupported file format. Please upload JPG, PNG or GeoTIFF."
      );
      return;
    }

    const maxSize = 100 * 1024 * 1024;

    if (file.size > maxSize) {
      setSelectedFile(null);
      setPreviewUrl("");
      setError(
        "File is too large. Maximum file size is 100 MB."
      );
      return;
    }

    setSelectedFile(file);

    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleGenerateDSM = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setError("");
    setProcessingStep(1);

    try {
      setProcessingStep(2);
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://localhost:8000/api/process", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server error (${response.status})`);
      }

      setProcessingStep(3);
      const data = await response.json();

      setProcessingStep(4);
      setResultsData(data);
      setShowResults(true);
    } catch (err) {
      console.error("Processing error:", err);
      setError(`Processing failed: ${err.message}. Please check that the DepthWizard backend is running.`);
    } finally {
      setIsProcessing(false);
    }
  };

  if (showTerrain) {
    return (
      <TerrainViewer
        onBack={() => setShowTerrain(false)}
        elevationGrid={resultsData?.elevation_grid}
        stats={resultsData?.stats}
      />
    );
  }

  return (
    <div className="app">

      <header className="navbar">
        <div className="logo">
          DepthWizard
        </div>

        <div className="nav-text">
          AI-Powered Terrain Analysis
        </div>
      </header>

      <main className="hero">
        <div className="hero-grid" aria-hidden="true"></div>
        <div className="hero-contours hero-contours-left" aria-hidden="true"></div>
        <div className="hero-contours hero-contours-right" aria-hidden="true"></div>
        <div className="terrain-wireframe" aria-hidden="true">
          <div className="wireframe-surface"></div>
        </div>
        <div className="floating-terrain-card floating-terrain-card-left" aria-hidden="true">
          <span style={{ fontSize: "2rem", display: "block", marginBottom: "4px" }}>🛰️</span>
          <span>REMOTE DATA</span>
        </div>

        <div className="floating-terrain-card floating-terrain-card-right" aria-hidden="true">
          <span style={{ fontSize: "2rem", display: "block", marginBottom: "4px" }}>⛰️</span>
          <span>3D TERRAIN</span>
        </div>
        <div className="hero-content">

          <p className="tag">
            REMOTE SENSING • 3D TERRAIN
          </p>

          <h1>
  Turn a Single Image into <span className="hero-blue">3D</span>
  <br />
  <span className="hero-blue">Terrain</span>
</h1>

          <p className="description">
            Upload a satellite or aerial image and generate
            depth, elevation, DSM and an interactive 3D
            terrain experience.
          </p>

          <div className="upload-box">
            <div className="upload-icon">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M12 16V4" />
                <path d="m7 9 5-5 5 5" />
                <path d="M5 20h14" />
              </svg>
            </div>

            <h2>
              Upload your image
            </h2>

            <p>
              JPG, PNG or GeoTIFF
            </p>

            <div className="upload-actions">
            <label
              htmlFor="image-upload"
              className="upload-button"
            >
              <span className="button-icon">
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M4 7h5l1.5 2H20v10H4z" />
                  <path d="M4 7V5h5l1.5 2" />
                </svg>
              </span>
              Choose Image

              <input
                id="image-upload"
                type="file"
                accept=".jpg,.jpeg,.png,.tif,.tiff"
                hidden
                onChange={handleFileChange}
              />
            </label>

            <button
  className={`generate-button ${selectedFile ? "ready" : ""}`}
  disabled={!selectedFile || isProcessing}
  onClick={handleGenerateDSM}
>
  <span className="generate-button-icon">✦</span>
  {isProcessing ? "Processing AI..." : "Generate DSM"}
</button>
            </div>

            {error && (
              <p className="upload-error">
                {error}
              </p>
            )}

            {selectedFile && (
              <div className="preview">

                <h3>
                  Selected Image
                </h3>

                {previewUrl &&
                  selectedFile.type !== "image/tiff" && (
                    <img
                      src={previewUrl}
                      alt="Selected"
                    />
                  )}

                {selectedFile.type === "image/tiff" && (
                  <div className="tiff-preview">

                    <div className="tiff-icon">
                      🗺️
                    </div>

                    <p>
                      GeoTIFF selected
                    </p>

                    <small>
                      Preview will be generated during processing.
                    </small>

                  </div>
                )}

                <div className="file-info">

                  <p>
                    <strong>File:</strong>{" "}
                    {selectedFile.name}
                  </p>

                  <p>
                    <strong>Size:</strong>{" "}
                    {(
                      selectedFile.size /
                      (1024 * 1024)
                    ).toFixed(2)}{" "}
                    MB
                  </p>

                  <p>
                    <strong>Format:</strong>{" "}
                    {selectedFile.type === "image/tiff"
                      ? "GeoTIFF"
                      : selectedFile.type}
                  </p>

                </div>

              </div>
            )}

          </div>

          {isProcessing && (
            <div className="processing-screen">

              <h2>
                Generating Your DSM with Depth Anything V2
              </h2>

              <p>
                Please wait while DepthWizard runs neural depth estimation & metric calibration.
              </p>

              <div className="processing-steps">

                <div className={processingStep >= 1 ? "completed" : ""}>
                  ✓ Image Uploaded
                </div>

                <div className={processingStep === 2 ? "active" : processingStep > 2 ? "completed" : ""}>
                  {processingStep > 2 ? "✓" : "⏳"} Depth Estimation (ViT-S)
                </div>

                <div className={processingStep === 3 ? "active" : processingStep > 3 ? "completed" : ""}>
                  {processingStep > 3 ? "✓" : "⏳"} Scale Calibration & Hillshade
                </div>

                <div className={processingStep >= 4 ? "completed" : ""}>
                  {processingStep >= 4 ? "✓" : "○"} 3D Surface Reconstruction
                </div>

              </div>

            </div>
          )}

          {showResults && (
            <div className="results-section">

              <div className="results-header">
                <div>
                  <h2>
                    DSM Analysis Results
                  </h2>

                  <p>
                    {selectedFile?.name}
                  </p>
                </div>

                <span className="results-status" style={{ background: "rgba(16, 185, 129, 0.2)", color: "#10b981", borderColor: "#10b981" }}>
                  AI INFERENCE COMPLETED
                </span>
              </div>

              <div className="results-grid">

                <div className="result-card">

                  <h3>
                    Original Image
                  </h3>

                  {previewUrl &&
                  selectedFile?.type !== "image/tiff" ? (
                    <div
                      className="original-image-wrapper"
                      onClick={() => setShowImageLightbox(true)}
                    >
                      <img
                        src={previewUrl}
                        alt="Original"
                      />

                      <div className="zoom-hint">
                        Click to enlarge
                      </div>
                    </div>
                  ) : (
                    <div className="result-placeholder">
                      GeoTIFF
                    </div>
                  )}

                </div>

                <div className="result-card">

                  <h3>
                    Depth Map
                  </h3>

                  {resultsData?.depth_map ? (
                    <div className="original-image-wrapper">
                      <img
                        src={resultsData.depth_map}
                        alt="Depth Map"
                      />
                    </div>
                  ) : (
                    <div className="result-placeholder depth-placeholder">
                      <div className="placeholder-content">
                        <div className="placeholder-icon">◌</div>
                        <span>Depth Map</span>
                        <small>Loading...</small>
                      </div>
                    </div>
                  )}

                </div>

                <div className="result-card">

                  <h3>
                    Calibrated DSM
                  </h3>

                  {resultsData?.dsm_map ? (
                    <div className="original-image-wrapper">
                      <img
                        src={resultsData.dsm_map}
                        alt="Digital Surface Model"
                      />
                    </div>
                  ) : (
                    <div className="result-placeholder dsm-placeholder">
                      <div className="placeholder-content">
                        <div className="placeholder-icon">◌</div>
                        <span>Digital Surface Model</span>
                        <small>Loading...</small>
                      </div>
                    </div>
                  )}

                </div>

                <div className="result-card">

                  <h3>
                    Hillshade
                  </h3>

                  {resultsData?.hillshade_map ? (
                    <div className="original-image-wrapper">
                      <img
                        src={resultsData.hillshade_map}
                        alt="Hillshade"
                      />
                    </div>
                  ) : (
                    <div className="result-placeholder hillshade-placeholder">
                      <div className="placeholder-content">
                        <div className="placeholder-icon">◌</div>
                        <span>Hillshade</span>
                        <small>Loading...</small>
                      </div>
                    </div>
                  )}

                </div>

              </div>

              <div className="terrain-stats">

                <div className="stat-card">

                  <div className="stat-icon">
                    ▲
                  </div>

                  <span>
                    Min Elevation
                  </span>

                  <strong>
                    {resultsData?.stats?.min_elevation ?? "106.2"} m
                  </strong>

                </div>

                <div className="stat-card">

                  <div className="stat-icon">
                    ◆
                  </div>

                  <span>
                    Max Elevation
                  </span>

                  <strong>
                    {resultsData?.stats?.max_elevation ?? "107.3"} m
                  </strong>

                </div>

                <div className="stat-card">

                  <div className="stat-icon">
                    ↕
                  </div>

                  <span>
                    Height Range
                  </span>

                  <strong>
                    {resultsData?.stats?.height_range ?? "1.1"} m
                  </strong>

                </div>

                <div className="stat-card">

                  <div className="stat-icon">
                    ▦
                  </div>

                  <span>
                    Mean Elevation
                  </span>

                  <strong>
                    {resultsData?.stats?.mean_elevation ?? "106.4"} m
                  </strong>

                </div>

              </div>

              <button
                className="explore-button"
                onClick={() => setShowTerrain(true)}
              >
                Explore in 3D →
              </button>

            </div>
          )}

        </div>
      </main>

      {showImageLightbox && (
        <div
          className="image-lightbox"
          onClick={() => setShowImageLightbox(false)}
        >

          <button
            className="lightbox-close"
            onClick={() => setShowImageLightbox(false)}
          >
            ×
          </button>

          <img
            src={previewUrl}
            alt="Original enlarged"
            onClick={(event) => event.stopPropagation()}
          />

        </div>
      )}

    </div>
  );
}

export default App;