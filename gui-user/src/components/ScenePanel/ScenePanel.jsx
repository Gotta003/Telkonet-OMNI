import React, {useState, useRef, useEffect} from 'react';
import './ScenePanel.css';

export const SCENES = [
  { id: 'morning',  name: 'Morning',  desc: 'bright & fresh',   icon: 'sun',     params: { light: 95, climate: 68, music: 35, windows: 90 } },
  { id: 'work',     name: 'Focus',    desc: 'crisp & quiet',    icon: 'lamp',    params: { light: 70, climate: 70, music: 25, windows: 70 } },
  { id: 'cinema',   name: 'Cinema',   desc: 'dim & warm',       icon: 'tv',      params: { light: 12, climate: 72, music: 78, windows: 0  } },
  { id: 'dinner',   name: 'Dinner',   desc: 'soft & savory',    icon: 'cutlery', params: { light: 55, climate: 71, music: 50, windows: 30 } },
  { id: 'sleep',    name: 'Sleep',    desc: 'off & still',      icon: 'moon',    params: { light: 0,  climate: 65, music: 0,  windows: 10 } },
];

const Icons = {
  sun: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" /></svg>,
  lamp: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M8 3h8l3 8H5zM12 11v6M8 21h8M10 17h4v4h-4z" /></svg>,
  tv: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="5" width="18" height="13" rx="1.5" /><path d="M9 21h6" /></svg>,
  cutlery: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7 3v18M7 9c2 0 3-1.5 3-3V3M7 9c-2 0-3-1.5-3-3V3M17 3c-2 1-3 4-3 6 0 1.5 1 3 3 3v9" /></svg>,
  moon: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" /></svg>
};

export default function ScenePanel({onActivate}) {
    const [activeScene, setActiveScene]=useState(null);
    const [rippleScene, setRippleScene]=useState(null);

    const rowRef=useRef(null);
    const isDragging=useRef(null);
    const startX=useRef(false);
    const scrollLeft=useRef(0);
    const didDrag=useRef(false);

    const handleActivate=(scene)=>{
        if(didDrag.current) return;
        setActiveScene(scene.id);
        setRippleScene(scene.id);
        setTimeout(()=>setRippleScene(null), 700);
        if (onActivate) {
            onActivate(scene);
        }
    };

    useEffect(()=>{
        const el=rowRef.current;
        if(!el) {
            return;
        }
        const onDown=(e)=>{
            isDragging.current=true;
            didDrag.current=false;
            startX.current=e.pageX-el.offsetLeft;
            scrollLeft.current=el.scrollLeft;
            el.style.cursor='grabbing';
        };
        const onMove=(e)=>{
            if(!isDragging.current) {
                return;
            }
            e.preventDefault();
            const x=e.pageX-el.offsetLeft;
            const walk=x-startX.current;
            if(Math.abs(walk)>4) {
                didDrag.current=true;
            }
            el.scrollLeft=scrollLeft.current-walk;
        };
        const onUp=()=>{
            isDragging.current=false;
            el.style.cursor='grab';
            requestAnimationFrame(()=>{didDrag.current=false;});
        };

        el.addEventListener('mousedown', onDown);
        el.addEventListener('mousemove', onMove);
        el.addEventListener('mouseup', onUp);
        el.addEventListener('mouseleave', onUp);
        return () => {
            el.removeEventListener('mousedown', onDown);
            el.removeEventListener('mousemove', onMove);
            el.removeEventListener('mouseup', onUp);
            el.removeEventListener('mouseleave', onUp);
        };
    }, []);

    return (
        <div className='card scenes-card'>
            <div className="eyebrow">
                <span>SCENES</span>
                <span className='bar'/>
                <span className='scene-count'>5</span>
            </div>
            <div className='scenes-row' ref={rowRef}>
                {SCENES.map((s)=>{
                    const IconComponent=Icons[s.icon];
                    const isActive=activeScene===s.id;
                    const isRipple=rippleScene===s.id;
                    return (
                        <button key={s.id} className={`scene-btn ${isActive ? 'active' : ''} ${isRipple ? 'ripple' : ''}`} onClick={() => handleActivate(s)}>
                            <span className="scene-ic">
                                {IconComponent && <IconComponent/>}
                            </span>
                            <span className="scene-name">{s.name}</span>
                            <span className="scene-desc">{s.desc}</span>
                        </button>
                    );
                })}
            </div>
            <div className='scenes-fade'/>
        </div>
    );
}