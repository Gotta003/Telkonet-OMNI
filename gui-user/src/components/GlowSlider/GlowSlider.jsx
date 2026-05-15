import React, {useRef} from 'react';
import './GlowSlider.css';

export default function GlowSlider({
    value=0,
    min=0,
    max=100,
    onChange,
    label='',
    icon=null,
    unit='%',
    color='var(--accent, #B65B3A)'
}) {
    const trackRef=useRef(null);
    const draggingRef=useRef(false);
    const setFromClientX=(clientX)=>{
        if(!trackRef.current) {
            return;
        }
        const rect=trackRef.current.getBoundingClientRect();
        const t=Math.max(0, Math.min(1, (clientX-rect.left)/rect.width));
        const v=Math.round(min+t*(max-min));
        if(onChange) {
            onChange(v);
        }
    };
    const onDown=(e)=>{
        draggingRef.current=true;
        setFromClientX(e.clientX);
        const move=(ev)=>{
            if(draggingRef.current) {
                setFromClientX(ev.clientX);
            }
        };
        const up=() => {
            draggingRef.current=false;
            window.removeEventListener('pointermove', move);
        };
        window.addEventListener('pointermove', move);
        window.addEventListener('poinerup', up, {once: true});
        e.preventDefault();
    };
    const pct=((value-min)/(max-min))*100;
    return (
        <div className='gslider nosel'>
            <div className='gslider-head'>
                <div className='label'>
                    {icon && <span className='ic'>{icon}</span>}
                    <span className="name">{label}</span>
                </div>
                <span className='val'>{value}{unit}</span>
            </div>
            <div className='gslider-track-wrap' ref={trackRef} onPointerDown={onDown}>
                <div className='gslider-track'>
                    <div className='gslider-fill' style={{width: `${pct}%`, background: color}}/>
                    <div className='gslider-thumb' style={{left: `${pct}%`, borderColor: color}}/>
                </div>
            </div>
        </div>
    );
}