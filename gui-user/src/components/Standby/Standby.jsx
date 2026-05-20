import React, { useEffect, useState, useRef } from "react";
import * as THREE from 'three';
import "./Standby.css"
import { ParticlesSwarm } from "../../particles/luna";

const PARTICLE_COUNT=2000;

export default function Standby({onWake}) {
    const canvasRef=useRef(null);
    const containerRef=useRef(null);
    const [time, setTime]=useState(new Date());
    useEffect(()=>{
        const t=setInterval(()=>setTime(new Date()), 1000);
        return () => clearInterval(t);
    }, []);

    useEffect(()=>{
        const canvas=canvasRef.current;
        if(!canvas) {
            return;
        }
        //Renderer
        const renderer=new THREE.WebGLRenderer({canvas, alpha: true, antialias: false});
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setSize(canvas.clientWidth, canvas.clientHeight);
        renderer.setClearColor(0x000000, 0);
        //Scene + Camera
        const scene=new THREE.Scene();
        const camera=new THREE.PerspectiveCamera(60, canvas.clientWidth/canvas.clientHeight, 0.1, 200);
        camera.position.set(0, 0, 50);
        //Geometry
        const positions=new Float32Array(PARTICLE_COUNT*3);
        const colors=new Float32Array(PARTICLE_COUNT*3);
        const sizes=new Float32Array(PARTICLE_COUNT);
        const phases=new Float32Array(PARTICLE_COUNT);
        const speeds=new Float32Array(PARTICLE_COUNT);
        const color=new THREE.Color();
        for(let i=0; i<PARTICLE_COUNT; i++) {
            const theta=Math.random()*Math.PI*2;
            const phi=Math.acos(2*Math.random()-1);
            const r=20+Math.random()*30;
            positions[i*3]=r*Math.sin(phi)*Math.cos(theta);
            positions[i*3+1]=r*Math.sin(phi)*Math.sin(theta);
            positions[i*3+2]=r*Math.cos(phi);

            const t=Math.random();
            if(t<0.5) {
                color.setHSL(0.1+Math.random()*0.05, 0.9, 0.5+Math.random()*0.2);//Gold
            }
            else if(t<0.8) {
                color.setHSL(0.08, 0.6, 0.75+Math.random()*0.2);//Warm White
            }
            else {
                color.setHSL(0.04, 0.8, 0.55+Math.random()*0.15);
            }
            colors[i*3]=color.r;
            colors[i*3+1]=color.g;
            colors[i*3+2]=color.b;
            sizes[i]=0.8+Math.random()*2.2;
            phases[i]=Math.random()*Math.PI*2;
            speeds[i]=0.15+Math.random()*0.35;
        }
        const geometry=new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        //Glowing
        const material=new THREE.ShaderMaterial({
            uniforms:{uTime:{value:0}},
            vertexColors: true,
            transparent: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
            vertexShader: `
                attribute float size;
                varying vec3 vColor;
                uniform float uTime;
                void main() {
                    vColor=color;
                    vec4 mvPos=modelViewMatrix*vec4(position, 1.0);
                    gl_PointSize=size*(200.0/-mvPos.z);
                    gl_Position=projectionMatrix*mvPos;
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                void main() {
                    float d=length(gl_PointCoord-vec2(0.5));
                    if(d>0.5) {
                        discard;
                    }
                        float alpha=1.0-smoothstep(0.1, 0.5, d);
                        gl_FragColor=vec4(vColor, alpha*0.75);
                }
            `,
        });
        const points=new THREE.Points(geometry, material);
        scene.add(points);
        //Animation
        let rafId;
        let elapsed=0;
        let last=performance.now();
        const orig=new Float32Array(positions);
        const animate=(now)=>{
            rafId=requestAnimationFrame(animate);
            const dt=(now-last)/1000;
            last=now;
            elapsed+=dt;
            material.uniforms.uTime.value=elapsed;
            const pos=geometry.attributes.position.array;
            for(let i=0; i<PARTICLE_COUNT; i++) {
                const ox=orig[i*3];
                const oy=orig[i*3+1];
                const oz=orig[i*3+2];
                const ph=phases[i];
                const sp=speeds[i];
                const wave=Math.sin(elapsed*sp+ph)*1.2;
                const drift=Math.cos(elapsed*sp*0.7+ph)*0.8;
                pos[i*3]=ox+wave*Math.cos(ph);
                pos[i*3+1]=oy+wave*Math.sin(ph)+drift;
                pos[i*3+2]=oz+Math.sin(elapsed*sp*0.5+ph)*0.6;
            }
            geometry.attributes.position.needsUpdate=true;
            //Orbit camera
            camera.position.x=Math.sin(elapsed*0.06)*8;
            camera.position.y=Math.cos(elapsed*0.04)*4;
            camera.lookAt(0, 0, 0);
            renderer.render(scene, camera);
        };
        rafId=requestAnimationFrame(animate);
        //Resize
        const onResize=()=>{
            if(!canvas.parentElement) {
                return;
            }
            const w=canvas.clientWidth;
            const h=canvas.clientHeight;
            renderer.setSize(w, h);
            camera.aspect=w/h;
            camera.updateProjectionMatrix();
        };
        window.addEventListener('resize', onResize);
        return() =>{
            cancelAnimationFrame(rafId);
            window.removeEventListener('resize', onResize);
            geometry.dispose();
            material.dispose();
            renderer.dispose();
        };
    }, []);

    useEffect(()=>{
        const container=containerRef.current;
        const swarm=new ParticlesSwarm(container, 8000);
        swarm.material.color.setHex(0xC8973A);
        return () => {
            swarm.dispose();
            container.querySelector(`canvas:not(.standby-canvas)`)?.remove();
        };
    }, []);

    const pad=(n)=>n<10 ? `0${n}` : `${n}`;
    const timeStr=`${pad(time.getHours())}:${pad(time.getMinutes())}`;
    const days=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const months=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const dateStr=`${days[time.getDay()]}, ${time.getDate()} ${months[time.getMonth()]} ${time.getFullYear()}`;

    return (
        <div className="standby" onClick={onWake} style={{cursor: 'pointer'}}>
            {/*3D PARTICLES*/}
            <canvas ref={canvasRef} className="standby-canvas"/>
            <div ref={containerRef} className="standby-bg"/>
            <div className="standby-content">
                {/*LOGO*/}
                <div className="standby-logo">
                    <div className="standby-logo-mark">TELKONET</div>
                    <div className="standby-logo-name">OMNI</div>
                </div>
                {/*CLOCK*/}
                <div className="standby-clock">{timeStr}</div>
                <div className="standby-date">{dateStr}</div>
                {/*HINT*/}
                <div className="standby-hint">Tap to activate</div>
            </div>
            <div className="standby-ring"/>
        </div>
    );
}