import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

export class ParticlesSwarm {
    constructor(container, count = 50000) {
        this.count = count;
        this.container = container;
        this.speedMult = 0.3;
        
        // SETUP
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.FogExp2(0x000000, 0.01);
        this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
        this.camera.position.set(0, 0, 100);
        
        this.renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.container.appendChild(this.renderer.domElement);

        // POST PROCESSING
        this.composer = new EffectComposer(this.renderer);
        this.composer.addPass(new RenderPass(this.scene, this.camera));
        const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
        bloomPass.strength = 0.6; bloomPass.radius = 0.4; bloomPass.threshold = 0;
        this.composer.addPass(bloomPass);

        // OBJECTS
        this.dummy = new THREE.Object3D();
        this.color = new THREE.Color();
        this.target = new THREE.Vector3();
        this.pColor = new THREE.Color();
        
        this.geometry = new THREE.BoxGeometry(0.3, 0.3, 0.3);
        this.material = new THREE.MeshBasicMaterial({ color: 0x00ff88, wireframe: true });
        
        this.mesh = new THREE.InstancedMesh(this.geometry, this.material, this.count);
        this.mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
        this.scene.add(this.mesh);
        
        this.positions = [];
        for(let i=0; i<this.count; i++) {
            this.positions.push(new THREE.Vector3((Math.random()-0.5)*100, (Math.random()-0.5)*100, (Math.random()-0.5)*100));
            this.mesh.setColorAt(i, this.color.setHex(0x00ff88));
        }
        
        this.clock = new THREE.Clock();
        this.animate = this.animate.bind(this);
        this.animate();
    }

    animate() {
        requestAnimationFrame(this.animate);
        const time = this.clock.getElapsedTime() * this.speedMult;
        
        if(this.material.uniforms && this.material.uniforms.uTime) {
            this.material.uniforms.uTime.value = time;
        }

        // API Stubs
        const PARAMS = {"spin":0.8,"size":60,"pulse":1};
        const addControl = (id, l, min, max, val) => {
             return PARAMS[id] !== undefined ? PARAMS[id] : val;
        };
        const setInfo = () => {};
        const annotate = () => {};
        let THREE_LIB = THREE;
        const count = this.count; // Alias for user code
        
        for(let i=0; i<this.count; i++) {
            let target = this.target;
            let color = this.pColor;
            
            // INJECTED CODE
            
            const spin = addControl("spin", "4D Spin", 0.1, 3, 0.8);
            const size = addControl("size", "Scale", 20, 500, 300);
            const pulse = addControl("pulse", "Pulse", 0, 2, 1);
            
            const t = time * spin;
            const phi = (i / count) * Math.PI * 16;
            const layer = i / count;
            
            // 4D rotation projected into 3D
            const w = Math.sin(phi * 0.5 + t) * pulse;
            const cos4 = Math.cos(t * 0.7);
            const sin4 = Math.sin(t * 0.7);
            
            const x4 = Math.cos(phi) * size;
            const y4 = Math.sin(phi) * size;
            const z4 = Math.cos(phi * 2 + t) * size * 0.6;
            const w4 = Math.sin(phi * 1.5 + t * 0.5) * size * 0.4;
            
            // Project 4D → 3D (perspective divide by w dimension)
            const wDist = 2.5 - w4 / size;
            const x = (x4 * cos4 - w4 * sin4) / wDist;
            const y = (y4 + Math.sin(t * 0.3) * size * 0.3) / wDist;
            const z = (z4 * cos4 + x4 * sin4 * 0.5) / wDist;
            
            // Breathing effect
            const breath = 1 + 0.15 * Math.sin(time * 1.5 + layer * Math.PI * 4);
            target.set(x * breath, y * breath, z * breath);
            
            // Deep space color: ultraviolet → electric blue → hot white core
            const hue = 0.65 + 0.15 * Math.sin(phi + time * 0.4);
            const light = 0.4 + 0.4 * Math.abs(Math.sin(phi * 0.5 + time));
            color.setHSL(hue, 1.0, light);
            
            if (i === 0) setInfo("Tesseract", "A 4D hypercube rotating through spacetime.");
            
            
            // UPDATE
            this.positions[i].lerp(this.target, 0.1);
            this.dummy.position.copy(this.positions[i]);
            this.dummy.updateMatrix();
            this.mesh.setMatrixAt(i, this.dummy.matrix);
            this.mesh.setColorAt(i, this.pColor);
        }
        this.mesh.instanceMatrix.needsUpdate = true;
        this.mesh.instanceColor.needsUpdate = true;
        
        this.composer.render();
    }
    
    dispose() {
        this.geometry.dispose();
        this.material.dispose();
        this.scene.remove(this.mesh);
        this.renderer.dispose();
    }
}