// Renders a rotating 3D DNA double-helix in the hero section using Three.js.
const DnaAnimation = {
  init() {
    const canvas = document.getElementById("dna-canvas");
    if (!canvas || typeof THREE === "undefined") return;

    const width = canvas.clientWidth || window.innerWidth;
    const height = canvas.clientHeight || window.innerHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
    camera.position.set(0, 0, 42);

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const group = new THREE.Group();
    scene.add(group);

    const cyan = new THREE.Color(0x00e5ff);
    const violet = new THREE.Color(0x7b5cff);

    const helixHeight = 46;
    const turns = 4;
    const pointsPerTurn = 14;
    const totalPoints = turns * pointsPerTurn;
    const radius = 7;

    const sphereGeo = new THREE.SphereGeometry(0.42, 12, 12);
    const rungGeo = new THREE.CylinderGeometry(0.06, 0.06, radius * 2 * 0.92, 6);

    for (let i = 0; i < totalPoints; i++) {
      const t = i / pointsPerTurn;
      const angle = t * Math.PI * 2;
      const y = (i / totalPoints) * helixHeight - helixHeight / 2;

      const x1 = Math.cos(angle) * radius;
      const z1 = Math.sin(angle) * radius;
      const x2 = Math.cos(angle + Math.PI) * radius;
      const z2 = Math.sin(angle + Math.PI) * radius;

      const matA = new THREE.MeshBasicMaterial({ color: cyan, transparent: true, opacity: 0.9 });
      const matB = new THREE.MeshBasicMaterial({ color: violet, transparent: true, opacity: 0.9 });

      const nodeA = new THREE.Mesh(sphereGeo, matA);
      nodeA.position.set(x1, y, z1);
      group.add(nodeA);

      const nodeB = new THREE.Mesh(sphereGeo, matB);
      nodeB.position.set(x2, y, z2);
      group.add(nodeB);

      if (i % 2 === 0) {
        const rungMat = new THREE.MeshBasicMaterial({ color: cyan, transparent: true, opacity: 0.18 });
        const rung = new THREE.Mesh(rungGeo, rungMat);
        rung.position.set((x1 + x2) / 2, y, (z1 + z2) / 2);
        const dir = new THREE.Vector3(x2 - x1, 0, z2 - z1).normalize();
        rung.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
        group.add(rung);
      }
    }

    group.rotation.x = 0.25;

    let raf;
    function animate() {
      group.rotation.y += 0.0034;
      renderer.render(scene, camera);
      raf = requestAnimationFrame(animate);
    }
    animate();

    function onResize() {
      const w = canvas.clientWidth || window.innerWidth;
      const h = canvas.clientHeight || window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }
    window.addEventListener("resize", onResize);

    this._cleanup = () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
      renderer.dispose();
    };
  },

  destroy() {
    if (this._cleanup) {
      this._cleanup();
      this._cleanup = null;
    }
  },
};
