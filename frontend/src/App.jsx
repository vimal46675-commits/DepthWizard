import React, { useEffect, useMemo, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, useTexture } from "@react-three/drei";
import * as THREE from "three";

function Terrain() {
  const [data, setData] = useState(null);
  const texture = useTexture("/satellite.jpg");

  useEffect(() => {
    fetch("/elevation_256.json")
      .then((r) => r.json())
      .then((json) => setData(json.data))
      .catch((err) => console.error("Elevation error:", err));
  }, []);

  const geometry = useMemo(() => {
    if (!data) return null;

    const rows = data.length;
    const cols = data[0].length;

    const geo = new THREE.PlaneGeometry(
      12,
      12,
      cols - 1,
      rows - 1
    );

    geo.rotateX(-Math.PI / 2);

    const positions = geo.attributes.position;

    for (let i = 0; i < positions.count; i++) {
      const x = i % cols;
      const z = Math.floor(i / cols);

      const height = (data[z][x] - 105) * 1.5;

      positions.setY(i, height);
    }

    positions.needsUpdate = true;
    geo.computeVertexNormals();

    return geo;
  }, [data]);

  if (!geometry) return null;

  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial
        map={texture}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

function App() {
  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        background: "#87ceeb",
        overflow: "hidden",
      }}
    >
      <Canvas
        camera={{
          position: [10, 8, 10],
          fov: 50,
        }}
      >
        <ambientLight intensity={1.5} />

        <directionalLight
          position={[10, 20, 10]}
          intensity={2}
        />

        <Terrain />

        <OrbitControls
          enableDamping={false}
          enablePan={true}
          enableZoom={true}
        />
      </Canvas>

      {/* TOP INFORMATION PANEL */}
      <div
        style={{
          position: "absolute",
          top: 20,
          left: 20,
          background: "rgba(0,0,0,0.75)",
          color: "white",
          padding: "15px 20px",
          borderRadius: 10,
          fontFamily: "Arial",
        }}
      >
        <div
          style={{
            fontSize: 22,
            fontWeight: "bold",
          }}
        >
          DepthWizard 3D Terrain
        </div>

        <div style={{ marginTop: 8 }}>
          Calibrated Elevation
        </div>

        <div style={{ marginTop: 5 }}>
          Source: 2048 × 2048
        </div>

        <div style={{ marginTop: 5 }}>
          3D Mesh: 256 × 256
        </div>
        <div style={{ marginTop: 5 }}>
  3D Flythrough: Enabled
</div>

<div style={{ marginTop: 5 }}>
  Interactive camera navigation
</div>

        <div
          style={{
            marginTop: 10,
            fontSize: 13,
            opacity: 0.8,
          }}
        >
          Drag = rotate • Scroll = zoom • Right-drag = pan
        </div>
      </div>

      {/* TERRAIN ANALYSIS PANEL */}
      <div
        style={{
          position: "absolute",
          bottom: 20,
          left: 20,
          background: "rgba(0,0,0,0.75)",
          color: "white",
          padding: "15px 20px",
          borderRadius: 10,
          fontFamily: "Arial",
          fontSize: 14,
        }}
      >
        <div>
          <b>Terrain Analysis</b>
        </div>

        <div style={{ marginTop: 6 }}>
          Elevation range: 101.1 – 108.2 m
        </div>

        <div style={{ marginTop: 4 }}>
          Vertical exaggeration: 1.5×
        </div>

        <div style={{ marginTop: 4 }}>
          Surface: Calibrated elevation
        </div>

        <div style={{ marginTop: 4 }}>
          Texture: Satellite RGB
        </div>
      </div>
    </div>
  );
}

export default App;