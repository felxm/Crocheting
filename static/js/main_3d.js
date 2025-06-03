// Global variables for Three.js components
let scene, camera, renderer;
let stitchMeshes = []; // To keep track of added stitches for easy removal
let currentAnimationFrameId = null; // To manage animation loop

// --- Constants for easy tweaking ---
const STITCH_SPHERE_RADIUS = 0.075; // Radius of the spheres representing stitches
const STITCH_SPHERE_SEGMENTS = 12;  // Detail of the spheres (width/height segments)
const STITCH_MATERIAL_COLOR = 0x007bff; // Blue color for stitches
const STITCH_MATERIAL_ROUGHNESS = 0.5;
const STITCH_MATERIAL_METALNESS = 0.1;

const AMBIENT_LIGHT_COLOR = 0xffffff;
const AMBIENT_LIGHT_INTENSITY = 0.6;
const DIRECTIONAL_LIGHT_COLOR = 0xffffff;
const DIRECTIONAL_LIGHT_INTENSITY = 0.8;
const DIRECTIONAL_LIGHT_POSITION = { x: 5, y: 10, z: 7.5 };

const SCENE_BACKGROUND_COLOR = 0xf0f0f0; // Light grey

function showPlaceholderMessage(container, message) {
    // Clear any existing content (like a previous canvas or message)
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
    const p = document.createElement('p');
    p.textContent = message;
    p.style.textAlign = 'center';
    p.style.paddingTop = '20px';
    container.appendChild(p);
}

function init3DScene() {
    const container = document.getElementById('scene-container');
    if (!container) {
        console.error('Scene container not found!');
        return;
    }

    // Stop any existing animation loop
    if (currentAnimationFrameId) {
        cancelAnimationFrame(currentAnimationFrameId);
        currentAnimationFrameId = null;
    }

    // Clear any previously existing Three.js scene resources fully
    // This is important if init3DScene is called multiple times (e.g. new file upload)
    clearSceneResources();

    // 1. Check for coordinates
    if (!window.patternCoordinates || window.patternCoordinates.length === 0) {
        console.log("No pattern coordinates found to render.");
        // clearSceneResources() was already called, so canvas is gone if it existed.
        showPlaceholderMessage(container, 'No pattern data to display. Upload a valid pattern file.');
        return;
    }

    // Clear container of any placeholder message if one was there
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    // 2. Scene Setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(SCENE_BACKGROUND_COLOR);

    const width = container.clientWidth;
    const height = container.clientHeight;

    camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000); // FOV, aspect, near, far

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement); // Appends the <canvas> element

    // 3. Add Lights
    const ambientLight = new THREE.AmbientLight(AMBIENT_LIGHT_COLOR, AMBIENT_LIGHT_INTENSITY);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(DIRECTIONAL_LIGHT_COLOR, DIRECTIONAL_LIGHT_INTENSITY);
    directionalLight.position.set(DIRECTIONAL_LIGHT_POSITION.x, DIRECTIONAL_LIGHT_POSITION.y, DIRECTIONAL_LIGHT_POSITION.z);
    scene.add(directionalLight);

    // 4. Create Objects from Coordinates
    // stitchMeshes array is already empty due to clearSceneResources -> clearStitchMeshesFromScene

    const stitchGeometry = new THREE.SphereGeometry(STITCH_SPHERE_RADIUS, STITCH_SPHERE_SEGMENTS, STITCH_SPHERE_SEGMENTS);
    const stitchMaterial = new THREE.MeshStandardMaterial({
        color: STITCH_MATERIAL_COLOR,
        roughness: STITCH_MATERIAL_ROUGHNESS,
        metalness: STITCH_MATERIAL_METALNESS
    });

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity, minZ = Infinity, maxZ = -Infinity;

    window.patternCoordinates.forEach(coord => {
        const [x, y, z] = coord;
        const mesh = new THREE.Mesh(stitchGeometry, stitchMaterial);
        mesh.position.set(x, y, z);
        scene.add(mesh);
        stitchMeshes.push(mesh); // Keep track for future cleanup (though cleared by clearSceneResources)

        if (x < minX) minX = x; if (x > maxX) maxX = x;
        if (y < minY) minY = y; if (y > maxY) maxY = y;
        if (z < minZ) minZ = z; if (z > maxZ) maxZ = z;
    });

    // 5. Camera Positioning
    if (stitchMeshes.length > 0) {
        const centerX = (minX + maxX) / 2;
        const centerY = (minY + maxY) / 2;
        const centerZ = (minZ + maxZ) / 2;
        const objectSizeX = Math.max(maxX - minX, 0.1);
        const objectSizeY = Math.max(maxY - minY, 0.1);

        const largerDim = Math.max(objectSizeX, objectSizeY);
        const distance = (largerDim / 2) / Math.tan(THREE.MathUtils.degToRad(camera.fov / 2) / camera.aspect); // Simplified distance calculation

        // Position camera to view the object, slightly from top for flat things
        camera.position.set(centerX, centerY + largerDim * 0.2 , centerZ + Math.max(distance * 1.2, 3)); // Min distance of 3 units
        camera.lookAt(centerX, centerY, centerZ); // Look at the center of the object
    } else {
        // Default camera position if somehow no stitches were created despite having coordinates
        camera.position.set(0, 0, 10);
        camera.lookAt(0, 0, 0);
    }
    camera.updateProjectionMatrix();

    // 6. Render Loop
    animate();
}

// Removes individual stitch meshes from the scene and disposes their geometry
function clearStitchMeshesFromScene() {
    stitchMeshes.forEach(mesh => {
        if (mesh.geometry) mesh.geometry.dispose();
        // Note: Material is shared. Do not dispose here if it's reused.
        // The current setup recreates material in init3DScene, so old one is GC'd if not referenced.
        if (scene && scene.children.includes(mesh)) { // Check if mesh is still in scene
             scene.remove(mesh);
        }
    });
    stitchMeshes = []; // Reset the array
}

// Cleans up major Three.js resources (scene, renderer) and stitch meshes
function clearSceneResources() {
    if (scene) {
        clearStitchMeshesFromScene(); // Remove meshes and dispose their geometries
        scene = null; // Allow scene object to be garbage collected
    }
    if (renderer) {
        renderer.dispose(); // Release WebGL context and associated resources
        // Also remove the canvas from DOM if it's still there
        const container = document.getElementById('scene-container');
        if (container && renderer.domElement && container.contains(renderer.domElement)) {
            container.removeChild(renderer.domElement);
        }
        renderer = null; // Allow renderer object to be garbage collected
    }
    // stitchMeshes array is already cleared by clearStitchMeshesFromScene if scene existed
}

function animate() {
    currentAnimationFrameId = requestAnimationFrame(animate);
    if (renderer && scene && camera) { // Ensure components exist
        renderer.render(scene, camera);
    }
}

// Initial call when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    init3DScene(); // Checks window.patternCoordinates and displays scene or placeholder
});

// Handle window resize to keep the scene proportional
window.addEventListener('resize', () => {
    if (camera && renderer) {
        const container = document.getElementById('scene-container');
        if (container) {
            const width = container.clientWidth;
            const height = container.clientHeight;

            if (width > 0 && height > 0) {
                 camera.aspect = width / height;
                 camera.updateProjectionMatrix();
                 renderer.setSize(width, height);
            }
        }
    }
});
