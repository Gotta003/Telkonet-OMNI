import React, {useRef} from 'react';
import GlowSlider from '../GlowSlider/GlowSlider';
import {ROOM_META, TONE_COLORS, roomAnyLightOn} from '../../constants/floorplandata';
import './RoomParams.css'

//Icons
const Icons = {
  thermometer: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 14.76V4a2 2 0 0 0-4 0v10.76a4 4 0 1 0 4 0z" /></svg>,
  speaker: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M11 5 6 9H3a1 1 0 0 0-1 1v4a1 1 0 0 0 1 1h3l5 4zM16 8a5 5 0 0 1 0 8M19 5a9 9 0 0 1 0 14" /></svg>,
  blinds: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="4" y="4" width="16" height="2" rx="0.5" /><rect x="4" y="9" width="16" height="2" rx="0.5" /><rect x="4" y="14" width="16" height="2" rx="0.5" /><rect x="4" y="19" width="16" height="1" rx="0.5" /></svg>,
  lamp: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M8 3h8l3 8H5zM12 11v6M8 21h8M10 17h4v4h-4z" /></svg>,
  map: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2zM9 4v14M15 6v14" /></svg>,
  x: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18M6 6l12 12" /></svg>
};

const CAP_SLIDER_DEF = {
  climate: { label: 'Climate', icon: <Icons.thermometer />, unit: '°', min: 60, max: 78 },
  music:   { label: 'Audio',   icon: <Icons.speaker />,     unit: '%', min: 0,  max: 100 },
  windows: { label: 'Blinds',  icon: <Icons.blinds />,      unit: '%', min: 0,  max: 100 },
};

function FixtureRow({fixture, value=0, onChange, isSelected, onSelect}) {
    const trackRef=useRef(null);
    const draggingRef=useRef(false);
    const on=value>5;
    const setFromClientX=(clientX)=>{
        if(!trackRef.current) {
            return;
        }
        const rect=trackRef.current.getBoundingClientRect();
        const t=Math.max(0, Math.min(1, (clientX-rect.left)/rect.width));
        onChange(Math.round(t*100));
    };
    const onDown=(e)=>{
        draggingRef.current=true;
        if(onSelect) {
            onSelect();
        }
        setFromClientX(e.clientX);
        const move=(ev)=>draggingRef.current && setFromClientX(ev.clientX);
        const up=()=>{
            draggingRef.current=false;
            window.removeEventListener('pointermove', move);
        };
        window.addEventListener('pointermove', move);
        window.addEventListener('pointerup', up, {once:true});
        e.preventDefault();
    };
    const toneInfo=TONE_COLORS[fixture.tone] || TONE_COLORS.warm;
    const glow=toneInfo.glow;
    return (
        <div className={`fx-row ${on ? 'on' : ''} ${isSelected ? 'selected' : ''}`} onMouseEnter={onSelect}>
            <button className='fx-toggle' onClick={()=>onChange(on ? 0 : 70)} aria-label="Toggle fixture" style={on ? {background: glow, borderColor: glow} : {}}>
                <span className={`fx-glyph ${fixture.icon}`}/>
            </button>
            <span className="fx-name">{fixture.name}</span>
            <div className='fx-track nosel' ref={trackRef} onPointerDown={onDown}>
                <div className='fx-fill' style={{width: `${value}%`, ...(on ? {background: glow} : {})}}/>
                <div className='fx-thumb' style={{left: `${value}%`, ...(on ? {borderColor: glow} : {})}}/>
            </div>
            <span className='fx-val'>
                {value}
                <span style={{opacity: 0.6}}>%</span>
            </span>
        </div>
    )
}

export default function RoomParams({room, roomState, onChangeParam, onChangeFixture, selectedFixture, onSelectFixture}) {
    if(!room) {
        return(
            <div className='card params-card'>
                <div className='params-empty'>
                    <div className='empty-icon'><Icons.map/></div>
                    <div className='empty-hint'>Tap a room to control<br/>its lighting and features</div>
                </div>
            </div>
        );
    }
    const meta=ROOM_META[room.id] || {fixtures: [], caps: []};
    const params=roomState[room.id] || {};
    const fixturesStates=params.fixtures || {};
    const isActive=roomAnyLightOn(roomState, room.id);
    const safeFixtureValues=Object.values(fixturesStates).filter(v=>typeof v === 'number');
    const anyLightOn=safeFixtureValues.some(v=>v>5);
    return (
        <div className='card params-card'>
            <div className='params-head'>
                <div className='title'>
                    <span className='name'>{room.name}</span>
                    <span className='sub'>- {meta.fixtures.length} fixtures</span>
                </div>
                <div className='pwr'>
                    <span className={`pwr-dot ${isActive ? 'active' : ''}`}/>
                    {isActive ? 'Active' : 'Idle'}
                </div>
            </div>
            <div className='params-list'>
                {/*Lighting Section*/}
                {meta.fixtures.length>0 && (
                    <div className='fix-section'>
                        <div className='fix-section-head'>
                            <span className='ic'><Icons.lamp/></span>
                            <span>Lighting</span>
                            <span className='bar'/>
                            <button className='fix-btn-mini' onClick={() => {
                                meta.fixtures.forEach(f=>onChangeFixture(room.id, f.id, anyLightOn ? 0 : 70));
                            }}>
                                {Object.values(fixturesStates).some(v=>v>5) ? 'All off' : 'All on'}
                            </button>
                        </div>
                        {meta.fixtures.map((f)=>(
                            <FixtureRow key={f.id} fixture={f} value={fixturesStates[f.id] || 0} onChange={(v) => onChangeFixture(room.id, f.id, v)} isSelected={selectedFixture===f.id} onSelect={() => onSelectFixture(f.id)}
                            />
                        ))}
                    </div>
                )}
                {/* Climate, Audio, Blinds */}
                {['climate', 'music', 'windows'].filter(c=>meta.caps.includes(c)).map((c)=>{
                    const def=CAP_SLIDER_DEF[c];
                    return (
                        <GlowSlider key={c} value={params[c] ?? def.min} label={def.label} icon={def.icon} unit={def.unit} min={def.min} max={def.max} onChange={(v)=>onChangeParam(room.id, c, v)}/>
                    );
                })}
                {/* Missing Capabilities Indicator */}
                <div className="cap-summary">
                    {['climate', 'music', 'windows'].filter(c=>!meta.caps.includes(c)).map((c)=>{
                        const lbl=c==='climate' ? 'No climate zone' : c==='music' ? 'No audio' : 'No blinds';
                        return (
                            <span key={c} className='cap-missing'>
                                <Icons.x/>
                                {lbl}
                            </span>
                        );
                    })}
                </div>
            </div>
        </div>
    )
}