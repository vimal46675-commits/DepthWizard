import { useRef, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

function TerrainMesh({
  wireframe,
  heightScale,
  activeTool,
  onTerrainClick
}) {
  const size = 12;
  const segments = 40;
  const vertices = [];
  const colors = [];
  const indices = [];

  for (let z = 0; z <= segments; z++) {
    for (let x = 0; x <= segments; x++) {
      const px = (x / segments - 0.5) * size;
      const pz = (z / segments - 0.5) * size;

      const height =
        Math.sin(px * 0.8) * 0.8 +
        Math.cos(pz * 0.7) * 0.6 +
        Math.sin((px + pz) * 0.5) * 0.5;

      vertices.push(px, height, pz);

      const normalizedHeight = Math.max(
        0,
        Math.min(1, (height + 2) / 4)
      );

      let r;
      let g;
      let b;

      if (normalizedHeight < 0.5) {
        const t = normalizedHeight / 0.5;

        r = 0.05 + t * 0.15;
        g = 0.35 + t * 0.45;
        b = 0.2 - t * 0.15;
      } else {
        const t = (normalizedHeight - 0.5) / 0.5;

        r = 0.2 + t * 0.8;
        g = 0.8 - t * 0.35;
        b = 0.05 + t * 0.15;
      }

      colors.push(r, g, b);
    }
  }

  for (let z = 0; z < segments; z++) {
    for (let x = 0; x < segments; x++) {
      const a = z * (segments + 1) + x;
      const b = a + 1;
      const c = a + segments + 1;
      const d = c + 1;

      indices.push(a, c, b);
      indices.push(b, c, d);
    }
  }

  return (
    <mesh
      scale={[1, heightScale, 1]}
      onClick={(event) => {
        if (!activeTool) return;

        event.stopPropagation();
        onTerrainClick(event.point);
      }}
    >
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={vertices.length / 3}
          array={new Float32Array(vertices)}
          itemSize={3}
        />

        <bufferAttribute
          attach="attributes-color"
          count={colors.length / 3}
          array={new Float32Array(colors)}
          itemSize={3}
        />

        <bufferAttribute
          attach="index"
          count={indices.length}
          array={new Uint32Array(indices)}
          itemSize={1}
        />
      </bufferGeometry>

      <meshStandardMaterial
        vertexColors
        wireframe={wireframe}
        roughness={0.8}
        metalness={0.05}
      />
    </mesh>
  );
}

function MeasurementLine({ points }) {
  if (points.length !== 2) return null;

  const geometry = new Float32Array([
    points[0][0],
    points[0][1],
    points[0][2],
    points[1][0],
    points[1][1],
    points[1][2]
  ]);

  return (
    <line>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={2}
          array={geometry}
          itemSize={3}
        />
      </bufferGeometry>

      <lineBasicMaterial color="#ef4444" linewidth={3} />
    </line>
  );
}

function TerrainScene({
  controlsRef,
  wireframe,
  heightScale,
  activeTool,
  onTerrainClick,
  selectedPoints
}) {
  return (
    <>
      <ambientLight intensity={1.5} />

      <directionalLight
        position={[5, 10, 5]}
        intensity={3}
      />

      <directionalLight
        position={[-5, 5, -5]}
        intensity={1.5}
      />

      <TerrainMesh
        wireframe={wireframe}
        heightScale={heightScale}
        activeTool={activeTool}
        onTerrainClick={onTerrainClick}
      />

      {selectedPoints.map((point, index) => (
        <mesh
          key={index}
          position={point}
        >
          <sphereGeometry args={[0.15, 20, 20]} />
          <meshStandardMaterial color="#ef4444" />
        </mesh>
      ))}

      <MeasurementLine points={selectedPoints} />

      <gridHelper
        args={[16, 16]}
        position={[0, -1.5, 0]}
      />

      <OrbitControls
        ref={controlsRef}
        makeDefault
        enableRotate
        enableZoom
        enablePan
        zoomSpeed={1}
        rotateSpeed={0.8}
        panSpeed={0.8}
        minDistance={4}
        maxDistance={30}
      />
    </>
  );
}

function TerrainViewer({ onBack }) {
  const controlsRef = useRef();

  const [wireframe, setWireframe] = useState(false);
  const [heightScale, setHeightScale] = useState(1);
  const [activeTool, setActiveTool] = useState("");
  const [selectedPoints, setSelectedPoints] = useState([]);

  const resetView = () => {
    if (!controlsRef.current) return;

    controlsRef.current.object.position.set(8, 7, 8);
    controlsRef.current.target.set(0, 0, 0);
    controlsRef.current.update();
  };

  const zoomIn = () => {
    if (!controlsRef.current) return;

    controlsRef.current.dollyOut(1.2);
    controlsRef.current.update();
  };

  const zoomOut = () => {
    if (!controlsRef.current) return;

    controlsRef.current.dollyIn(1.2);
    controlsRef.current.update();
  };

  const selectTool = (tool) => {
    setActiveTool((currentTool) =>
      currentTool === tool ? "" : tool
    );

    setSelectedPoints([]);
  };

  const handleTerrainClick = (point) => {
    if (!activeTool) return;

    const newPoint = [
      point.x,
      point.y * heightScale,
      point.z
    ];

    setSelectedPoints((currentPoints) => {
      if (currentPoints.length >= 2) {
        return [newPoint];
      }

      return [...currentPoints, newPoint];
    });
  };

  const heightDifference =
  selectedPoints.length === 2
    ? Math.abs(
        Number(selectedPoints[1][1].toFixed(2)) -
        Number(selectedPoints[0][1].toFixed(2))
      )
    : 0;

  const horizontalDistance =
    selectedPoints.length === 2
      ? Math.sqrt(
          Math.pow(
            selectedPoints[1][0] -
            selectedPoints[0][0],
            2
          ) +
          Math.pow(
            selectedPoints[1][2] -
            selectedPoints[0][2],
            2
          )
        )
      : 0;

  const slopeAngle =
    selectedPoints.length === 2
      ? Math.atan2(
          heightDifference,
          horizontalDistance
        ) * (180 / Math.PI)
      : 0;

  const activeToolLabel =
    activeTool === "height"
      ? "Measure Height"
      : activeTool === "slope"
      ? "Measure Slope"
      : activeTool === "point"
      ? "Point Information"
      : "None";

  return (
    <div className="terrain-page">

      <div className="terrain-header">

        <button
          className="back-button"
          onClick={onBack}
        >
          ← Back
        </button>

        <div>
          <h2>DepthWizard 3D Terrain</h2>
          <p>Interactive terrain analysis</p>
        </div>

      </div>

      <div className="terrain-content">

        <div className="terrain-viewer">

          <Canvas
            camera={{
              position: [8, 7, 8],
              fov: 50
            }}
          >
            <TerrainScene
              controlsRef={controlsRef}
              wireframe={wireframe}
              heightScale={heightScale}
              activeTool={activeTool}
              onTerrainClick={handleTerrainClick}
              selectedPoints={selectedPoints}
            />
          </Canvas>

          <div className="terrain-status-badge">
            <span className="status-dot"></span>

            <div>
              <strong>3D TERRAIN</strong>
              <small>Demo DSM</small>
            </div>
          </div>

          <div className="elevation-legend">

            <strong>Elevation</strong>

            <div className="legend-gradient"></div>

            <div className="legend-labels">
              <span>Low</span>
              <span>Medium</span>
              <span>High</span>
            </div>

          </div>

          {activeTool && (
            <div className="measurement-status">

              {activeTool === "height" && (
                <>
                  <strong>📏 Height Measurement</strong>

                  <span>
                    {selectedPoints.length === 0 &&
                      "Click the first terrain point"}

                    {selectedPoints.length === 1 &&
                      "Click the second terrain point"}

                    {selectedPoints.length === 2 &&
                      "Measurement complete"}
                  </span>
                </>
              )}

              {activeTool === "slope" && (
                <>
                  <strong>📐 Slope Measurement</strong>

                  <span>
                    {selectedPoints.length === 0 &&
                      "Click the first terrain point"}

                    {selectedPoints.length === 1 &&
                      "Click the second terrain point"}

                    {selectedPoints.length === 2 &&
                      "Slope calculation complete"}
                  </span>
                </>
              )}

              {activeTool === "point" && (
                <>
                  <strong>📍 Point Information</strong>

                  <span>
                    Click two terrain points
                  </span>
                </>
              )}

            </div>
          )}

          {activeTool === "height" &&
            selectedPoints.length === 2 && (
              <div className="point-info-card">

                <strong>📏 Height Measurement</strong>

                <div>
                  Point A:{" "}
                  {selectedPoints[0][1].toFixed(2)} m
                </div>

                <div>
                  Point B:{" "}
                  {selectedPoints[1][1].toFixed(2)} m
                </div>

                <div>
                  Height Difference:{" "}
                  {heightDifference.toFixed(2)} m
                </div>

                <small>
                  Demo terrain measurement
                </small>

              </div>
            )}

          {activeTool === "slope" &&
            selectedPoints.length === 2 && (
              <div className="point-info-card">

                <strong>📐 Slope Measurement</strong>

                <div>
                  Height Difference:{" "}
                  {heightDifference.toFixed(2)} m
                </div>

                <div>
                  Horizontal Distance:{" "}
                  {horizontalDistance.toFixed(2)} m
                </div>

                <div>
                  Slope Angle:{" "}
                  {slopeAngle.toFixed(2)}°
                </div>

                <small>
                  Demo terrain measurement
                </small>

              </div>
            )}

          {activeTool === "point" &&
            selectedPoints.length > 0 && (
              <div className="point-info-card">

                <strong>📍 Selected Point</strong>

                <div>
                  X:{" "}
                  {selectedPoints[
                    selectedPoints.length - 1
                  ][0].toFixed(2)} m
                </div>

                <div>
                  Y:{" "}
                  {selectedPoints[
                    selectedPoints.length - 1
                  ][1].toFixed(2)} m
                </div>

                <div>
                  Z:{" "}
                  {selectedPoints[
                    selectedPoints.length - 1
                  ][2].toFixed(2)} m
                </div>

                <small>
                  {selectedPoints.length} point
                  {selectedPoints.length > 1 ? "s" : ""} selected
                </small>

              </div>
            )}

          <div className="viewer-toolbar">

            <button onClick={resetView}>
              Reset View
            </button>

            <button
              onClick={() => setWireframe((value) => !value)}
            >
              {wireframe ? "Solid Mode" : "Wireframe"}
            </button>

            <button onClick={zoomOut}>
              − Zoom Out
            </button>

            <button onClick={zoomIn}>
              + Zoom In
            </button>

            <label>
              Height

              <input
                type="range"
                min="0.5"
                max="2.5"
                step="0.1"
                value={heightScale}
                onChange={(event) =>
                  setHeightScale(
                    Number(event.target.value)
                  )
                }
              />

              <span>
                {heightScale.toFixed(1)}x
              </span>
            </label>

          </div>

        </div>

        <aside className="analysis-panel">

          <div className="analysis-heading">
            <div>
              <h3>Terrain Analysis</h3>
              <span>Current terrain overview</span>
            </div>

            <span className="demo-badge">
              DEMO
            </span>
          </div>

          <div className="analysis-grid">

            <div className="analysis-card">
              <span>Elevation</span>
              <strong>128.4 m</strong>
            </div>

            <div className="analysis-card">
              <span>Slope</span>
              <strong>17.2°</strong>
            </div>

            <div className="analysis-card">
              <span>Resolution</span>
              <strong>1.2 m</strong>
            </div>

            <div className="analysis-card">
              <span>Mode</span>
              <strong>DSM</strong>
            </div>

          </div>

          <div className="active-tool-card">

            <span>Active Tool</span>

            <strong>
              {activeToolLabel}
            </strong>

          </div>

          <div className="analysis-tools">

            <h4>Tools</h4>

            <button
              className={
                activeTool === "height"
                  ? "tool-active"
                  : ""
              }
              onClick={() => selectTool("height")}
            >
              📏 Measure Height
            </button>

            <button
              className={
                activeTool === "slope"
                  ? "tool-active"
                  : ""
              }
              onClick={() => selectTool("slope")}
            >
              📐 Measure Slope
            </button>

            <button
              className={
                activeTool === "point"
                  ? "tool-active"
                  : ""
              }
              onClick={() => selectTool("point")}
            >
              📍 Point Information
            </button>

          </div>

          <div className="analysis-footer">
            Demo terrain data
          </div>

        </aside>

      </div>

      <div className="terrain-controls">
        <span>Mouse — Rotate</span>
        <span>Right Click — Pan</span>
        <span>Scroll — Zoom</span>
      </div>

    </div>
  );
}

export default TerrainViewer;