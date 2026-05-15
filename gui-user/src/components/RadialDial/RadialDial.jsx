import React from 'react';
import './RadialDial.css';

export default function RadialDial({
    value=0,
    max=100,
    label='',
    unit='',
    color='var(--accent, #B65B3A)',
    style='arc', // arc | ticks | thin
    size=100,
}) {
    const numericValue=typeof value=== 'number' && isFinite(value) ? value : 0
    const pct=Math.max(0, Math.min(1, numericValue/max));
    const center=size/2;
    const baseStroke=style==='thin' ? 3 : 7;
    const radius = center-baseStroke-2;
    const startAngle=-230;
    const endAngle=50;
    const sweep=280;
    const toRad=(a)=>(a*Math.PI)/180;
    const startX=center+radius*Math.cos(toRad(startAngle));
    const startY=center+radius*Math.sin(toRad(startAngle));
    const endX=center+radius*Math.cos(toRad(endAngle));
    const endY=center+radius*Math.sin(toRad(endAngle));
    const totalLen=2*Math.PI*radius*(sweep/360);
    const dashOffset=totalLen*(1-pct);
    const showVal = typeof value === 'number' && isFinite(value)
    ? (numericValue >= 100 ? Math.round(numericValue) : numericValue.toFixed(1).replace(/\.0$/, '')) : '—';
    const tickCount=30;
    
    return (
        <div className='dial' style={{width: size}}>
            <div style={{position: 'relative', width: size, height: size}}>
                <svg className='dial-svg' width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
                    {style === 'arc' && (
                        <>
                        <path className='dial-bg' d={`M ${startX} ${startY} A ${radius} ${radius} 0 1 1 ${endX} ${endY}`} strokeWidth={baseStroke}/>
                        <path className='dial-arc' d={`M ${startX} ${startY} A ${radius} ${radius} 0 1 1 ${endX} ${endY}`} strokeWidth={baseStroke} strokeDasharray={totalLen} strokeDashoffset={dashOffset} style={{stroke: color}}/>
                        </>
                    )}
                    {style === 'thin' && (
                        <>
                        <path
                            className="dial-bg"
                            d={`M ${startX} ${startY} A ${radius} ${radius} 0 1 1 ${endX} ${endY}`}
                            strokeWidth={2}
                        />
                        <path
                            className="dial-arc"
                            d={`M ${startX} ${startY} A ${radius} ${radius} 0 1 1 ${endX} ${endY}`}
                            strokeWidth={3.5}
                            strokeDasharray={totalLen}
                            strokeDashoffset={dashOffset}
                            style={{ stroke: color }}
                        />
                        {pct > 0 && (() => {
                            const a = startAngle + sweep * pct;
                            const x = center + radius * Math.cos(toRad(a));
                            const y = center + radius * Math.sin(toRad(a));
                            return <circle cx={x} cy={y} r={4} fill={color} />;
                        })()}
                        </>
                    )}

                    {style === 'ticks' && (
                        <g className="dial-ticks">
                        {Array.from({ length: tickCount }).map((_, i) => {
                            const a = startAngle + sweep * (i / (tickCount - 1));
                            const x1 = center + (radius - 1) * Math.cos(toRad(a));
                            const y1 = center + (radius - 1) * Math.sin(toRad(a));
                            const x2 = center + (radius - 8) * Math.cos(toRad(a));
                            const y2 = center + (radius - 8) * Math.sin(toRad(a));
                            const on = i / (tickCount - 1) <= pct;
                            return (
                            <line
                                key={i}
                                x1={x1} y1={y1} x2={x2} y2={y2}
                                className={on ? 'on' : ''}
                                style={on ? { stroke: color } : {}}
                            />
                            );
                        })}
                        </g>
                    )}
                </svg>
                <div className='dial-center'>
                    <div className='dial-value'>{showVal}</div>
                    {unit && <div className='dial-unit'>{unit}</div>}
                </div>
            </div>
            {label && <div className="dial-label">{label}</div>}
        </div>
    );
}