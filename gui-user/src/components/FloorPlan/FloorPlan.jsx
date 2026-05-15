import React, {useState, useEffect, useRef} from 'react';
import {ROOMS, ROOM_META, TONE_COLORS, roomAvgLight, roomAnyLightOn} from '../../constants/floorplandata';
import './FloorPlan.css';

const W=640;
const H=400;

function easeInOut(t) {
    return t<0.5 ? 2*t*t : -1+(4-2*t)*t;
}

function lerpState(a, b, t) {
    return {
        tx: a.tx+(b.tx-a.tx)*t,
        ty: a.ty+(b.ty-a.ty)*t,
        scale: a.scale+(b.scale-a.scale)*t,
        opacity: a.opacity+(b.opacity-a.opacity)*t,
    };
}

function isolateTransform(room, availableW=W) {
    const PAD=60;
    const scaleX=(availableW-PAD*2)/room.w;
    const scaleY=(H-PAD*2)/room.h;
    const scale=Math.min(scaleX, scaleY, 3.5);
    const rcx=room.x+room.w/2;
    const rcy=room.y+room.h/2;
    const tx=availableW/2-rcx*scale;
    const ty=H/2-rcy*scale;
    return {tx, ty, scale, opacity:1};
}

const IDENTITY={tx: 0, ty: 0, scale: 1, opacity: 1};

const RoomIcon = (props) => {
    const commonProps = {
        width: "24", 
        height: "24", 
        viewBox: "0 0 24 24", 
        fill: "none",
        stroke: "currentColor", 
        strokeWidth: "1.2", 
        strokeLinecap: "round",
        strokeLinejoin: "round",
        className: props.className,
    };
    
    const x = props.x || 0;
    const y = props.y || 0;

    if (props.kind === 'bed') return <g transform={`translate(${x}, ${y})`} className="fp-room-icon"><path d="M2 14V6h16v8M2 11h16M2 14v3M18 14v3M5 7v3h4V7" {...commonProps} /></g>;
    if (props.kind === 'bath') return <g transform={`translate(${x}, ${y})`} className="fp-room-icon"><path d="M3 11h14v3a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v-3zM5 11V6a2 2 0 0 1 4 0M14 5h2v2M5 17l-1 2M15 17l1 2" {...commonProps} /></g>;
    if (props.kind === 'ensuite') return <g transform={`translate(${x}, ${y})`} className="fp-room-icon"><path d="M4 18v-7a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3v7M4 14h12" {...commonProps} /><circle cx="10" cy="5" r="2" fill="none" stroke="currentColor" strokeWidth="1.2" /></g>;
    if (props.kind === 'kitchen') return <g transform={`translate(${x}, ${y})`} className="fp-room-icon"><rect x="3" y="3" width="14" height="14" rx="1.5" {...commonProps} /><circle cx="7" cy="8" r="1.5" {...commonProps} /><circle cx="13" cy="8" r="1.5" {...commonProps} /><path d="M5 13h10" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" /></g>;
    if (props.kind === 'living') return <g transform={`translate(${x}, ${y})`} className="fp-room-icon"><path d="M4 12v5M16 12v5M2 12h16v-2a3 3 0 0 0-3-3H5a3 3 0 0 0-3 3v2zM4 12v-2a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v2" {...commonProps} /></g>;
    if (props.kind === 'entry') return <g transform={`translate(${x}, ${y})`} className="fp-room-icon"><path d="M5 2h10v16H5z M9 10h0.01M5 18h10" {...commonProps} /><circle cx="11" cy="10" r="0.8" fill="currentColor" /></g>;
    if (props.kind === 'hall') return <g transform={`translate(${x}, ${y})`} className="fp-room-icon"><path d="M3 17 17 3M8 3h9v9" {...commonProps} /></g>;
    return null;
}

function FixtureGlyph({kind, cx, cy, on, color, isSelected}) {
    const stroke=isSelected ? 'var(--accent, #C8973A)' : on ? color : '#9A9085';
    const fill=on ? color : '#FBFAF6';
    const innerDot=on ? "#fff" : "#C2B9AC";
    const sw=isSelected ? "2" : "1";
    if (kind === 'lamp') return <><circle cx={cx} cy={cy} r={5} fill={fill} stroke={stroke} strokeWidth={sw} /><circle cx={cx} cy={cy} r={1.5} fill={innerDot} /></>;
    if (kind === 'spot') return <><rect x={cx - 4.5} y={cy - 4.5} width={9} height={9} rx={1.5} fill={fill} stroke={stroke} strokeWidth={sw} /><circle cx={cx} cy={cy} r={1.5} fill={innerDot} /></>;
    if (kind === 'sconce') return <path d={`M ${cx - 5} ${cy + 3} L ${cx} ${cy - 5} L ${cx + 5} ${cy + 3} Z`} fill={fill} stroke={stroke} strokeWidth={sw} strokeLinejoin="round" />;
    if (kind === 'strip') return <rect x={cx - 9} y={cy - 2.5} width={18} height={5} rx={1.5} fill={fill} stroke={stroke} strokeWidth={sw} />;
    return <circle cx={cx} cy={cy} r={4} fill={fill} stroke={stroke} strokeWidth={sw}></circle>
}

const WALLS_D = `
  M 0 0 L 640 0 L 640 400 L 0 400 Z
  M 180 0   L 180 400
  M 480 0   L 480 240
  M 0  120  L 180 120
  M 480 120 L 640 120
  M 180 240 L 640 240
  M 0  300  L 180 300
`;

const DOORS_D = `
  M 50 120 L 110 120
  M 180 76 L 180 116
  M 90 300 L 130 300
  M 180 270 L 180 295
  M 180 360 L 180 395
  M 480 60 L 480 100
  M 540 240 L 580 240
`;

export default function FloorPlan({selectedId, onSelect, roomState, selectedFixture, onSelectFixture, homeMode=false, onDismiss,}) {
    const initStates=()=>{
        const s={};
        ROOMS.forEach((r)=>{s[r.id]={...IDENTITY};});
        return s;
    };

    const [roomStates, setRoomStates]=useState(initStates);
    const animRef=useRef(null);
    const fromRef=useRef(null);
    const targetRef=useRef(null);
    const svgRef=useRef(null);

    const getSvgAvailableW=()=>{
        if(!svgRef.current) {
            return W;
        }
        const rect=svgRef.current.getBoundingClientRect();
        if(rect.width===0) {
            return W;
        }
        const pxPerUnit=rect.width/W;
        const panelPxW=380;
        const available=W-(panelPxW/pxPerUnit);
        return Math.max(200, available);
    };

    const buildTargets=(selId)=>{
        const targets={};
        if(!selId || !homeMode) {
            ROOMS.forEach((r)=>{targets[r.id]={...IDENTITY};});
        }
        else {
            const selRoom=ROOMS.find((r)=>r.id===selId);
            const availableW=getSvgAvailableW();
            const iso=selRoom ? isolateTransform(selRoom, availableW) : IDENTITY;
            ROOMS.forEach((r)=>{
                targets[r.id]=r.id===selId ? {...iso, opacity: 1} : {tx: 0, ty: 0, scale: 1, opacity: 0};    
            });
        }
        return targets;
    };

    const animateTo=(target)=>{
        if(animRef.current) {
            cancelAnimationFrame(animRef.current);
        }
        setRoomStates((current) => {
            fromRef.current=current;
            targetRef.current=target;
            return current;
        });
        const start=performance.now();
        const DURATION=500;
        const step=(now)=>{
            const t=Math.min(1, (now-start)/DURATION);
            const e=easeInOut(t);
            setRoomStates(()=>{
                const next={};
                ROOMS.forEach((r)=>{
                    next[r.id]=lerpState(fromRef.current[r.id] || IDENTITY, targetRef.current[r.id] || IDENTITY, e);
                });
                return next;
            });
            if(t<1) animRef.current=requestAnimationFrame(step);
        };
        animRef.current=requestAnimationFrame(step);
    };

    useEffect(()=>{
        const tid=setTimeout(()=>{
            animateTo(buildTargets(selectedId));
        }, selectedId ? 30 : 0);
        return ()=>{
            clearTimeout(tid);
            if(animRef.current) cancelAnimationFrame(animRef.current);
        };
    }, [selectedId, homeMode]);

    const isIsolated=homeMode && !!selectedId;

    return (
        <svg className={`fp-svg${isIsolated ? ' fp-isolated' : ''}`} viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet">
            <defs>
                <pattern id="fp-tile" width="20" height="20" patternUnits="userSpaceOnUse">
                    <rect width="20" height="20" fill="transparent"/>
                    <circle cx="10" cy="10" r="0.6" fill="rgba(28,24,18,0.06)"/>
                </pattern>
            </defs>
            <rect x="0" y="0" width={W} height={H} fill={isIsolated ? 'rgba(244,242,238,0.92)' : 'url(#fp-tile)'} onClick={isIsolated ? onDismiss : undefined} style={{cursor: isIsolated ? 'zoom-out' : 'default'}}/>
            {!isIsolated && (
                <rect x="0" y="0" width={W} height={H} fill="url(#fp-tile)" style={{pointerEvents: 'none'}}/>
            )}
            {/* Rooms*/}
            {ROOMS.map((r)=>{
                const light=roomAvgLight(roomState, r.id);
                const occupied=roomAnyLightOn(roomState, r.id);
                const selected=selectedId===r.id;
                const rs=roomStates[r.id] || IDENTITY;
                const cls=[
                    'fp-room',
                    selected ? 'selected' : '',
                    light>0 ? 'has-light' : '',
                    light>60 ? 'level-hi' : '',
                ].filter(Boolean).join(' ')
                
                return (
                    <g key={r.id} className={cls} 
                    style={{opacity: rs.opacity, pointerEvents: rs.opacity<0.05 ? 'none' : 'auto'}} transform={`translate(${rs.tx}, ${rs.ty}) scale(${rs.scale})`} onClick={(e) => {e.stopPropagation(); onSelect && onSelect(r.id);}}>
                        <rect className="fp-room-fill" x={r.x+0.5} y={r.y+0.5} width={r.w-1} height={r.h-1}/>
                        <RoomIcon kind={r.key} x={r.x+12} y={r.y+12}/>
                        <text className="fp-room-label" x={r.x+r.w/2} y={r.y+r.h/2-4}>{r.name.toUpperCase()}</text>
                        <text x={r.x+r.w/2} y={r.y+r.h/2+14} className="fp-room-label" style={{ fontSize: 9, fill: 'var(--ink-4)' }}>
                        {Math.round(light)}%
                        </text>
                        {occupied && <circle className="fp-occ-dot" cx={r.x+r.w-14} cy={r.y+14} r={4} />}
                    </g>
                );
            })}
            {/* WALLS */}
            <g style={{opacity: isIsolated ? 0 : 1, transition: 'opacity 0.35s ease', pointerEvents: 'none'}}>
                <path className="fp-walls" d={WALLS_D}/>
                <path d={DOORS_D} stroke="var(--paper)" strokeWidth="3" strokeLinecap="square"/>
                <g fill="none" stroke="var(--line-2)" strokeWidth="0.75">
                    <path d="M 50 120 a 60 60 0 0 1 60 -60" />
                    <path d="M 180 76 a 40 40 0 0 0 -40 40" />
                    <path d="M 90 300 a 40 40 0 0 0 40 -40" />
                    <path d="M 540 240 a 40 40 0 0 1 -40 -40" />
                    <path d="M 480 60 a 40 40 0 0 1 40 40" />
                </g>
            </g>
            {/*FIXTURES*/}
            {ROOMS.map((r)=>{
                const meta=ROOM_META[r.id];
                if(!meta?.fixtures) {
                    return null;
                }
                const fixState=(roomState?.[r.id]?.fixtures) || {};
                const rs=roomStates[r.id] || IDENTITY;
                return (
                    <g key={r.id+"-fx"} style={{opacity: rs.opacity, pointerEvents: rs.opacity<0.05 ? 'none' : 'auto'}} transform={`translate(${rs.tx}, ${rs.ty}) scale(${rs.scale})`}>
                        {meta.fixtures.map((fx)=>{
                            const v=fixState[fx.id] || 0;
                            const on=v>5;
                            const isSelected=selectedId===r.id && selectedFixture===fx.id;
                            const toneInfo=TONE_COLORS[fx.tone] || TONE_COLORS.warm;
                            const intensity=v/100;
                            return (
                                <g key={fx.id} className={`fp-fixture${on ? ' on' : ''}${isSelected ? ' selected' : ''}`} onClick={(e)=>{e.stopPropagation(); 
                                onSelectFixture && onSelectFixture(r.id, fx.id);}}>
                                    <rect x={fx.x-10} y={fx.y-10} width={20} height={20} fill="transparent" style={{cursor: 'pointer'}}/>
                                    {on && (
                                        <circle cx={fx.x} cy={fx.y} r={10+14*intensity} fill={toneInfo.glow} opacity={0.15+0.28*intensity} style={{mixBlendMode: 'multiply'}}/>
                                    )}
                                    {isSelected && (
                                        <circle cx={fx.x} cy={fx.y} r={11} fill="none" stroke="var(--accent)" strokeWidth="2"/>
                                    )}
                                    <FixtureGlyph kind={fx.icon} cx={fx.x} cy={fx.y} on={on} color={toneInfo.glow}
                                    isSelected={isSelected}/>
                                </g>
                            );
                        })}
                    </g>
                );
            })}
            {isIsolated  && (()=>{
                const r=ROOMS.find((rm)=>rm.id===selectedId);
                const rs=roomStates[selectedId];
                if(!r || !rs) {
                    return null;
                }
                const x1=r.x*rs.scale+rs.tx;
                const y1=r.y*rs.scale+rs.ty;
                const rw=r.w*rs.scale;
                const rh=r.h*rs.scale;
                return (
                    <g style={{pointerEvents: 'none'}}>
                        <rect x={x1} y={y1} width={rw} height={rh} fill="none" stroke="var(--accent, #C8973A)" strokeWidth="2" rx="4" opacity={rs.opacity}/>
                        <text x={x1+rw/2} y={y1+rh+28} textAnchor='middle' style={{
                            fontSize: Math.min(28, rw*0.18),
                            fill: 'var(--accent-dim, #A07828)',
                            fontFamily: 'var(--font-serif, serif)',
                            fontWeight: 700,
                            opacity: rs.opacity,
                        }}>{r.name}</text>
                        <text x={getSvgAvailableW()/2} y={H-16} textAnchor="middle" style={{
                            fontSize: 11,
                            fill: 'var(--text-muted, #9A948E)',
                            fontFamily: 'var(--font-mono, monospace)', letterSpacing: '1px',
                            opacity: rs.opacity*0.7
                        }}>TAP OUTSIDE TO RETURN</text>
                    </g>
                );
            })()}
        </svg>
    );
}