import React from 'react';
import './MiniSparkline.css';

export default function MiniSparkline({
    values=[],
    width=80,
    height=24,
    min=0,
    max=100,
    color='var(--accent, #B65B3A)',
    style='area', //area | line | dotted
}) {
    if(!values || values.length<2) {
        return (
            <svg className="spark" width={width} height={height}>
                <line x1={0} y1={height/2} x2={width} y2={height/2} stroke="var(--ink-5, rgba(0,0,0,0.1))" strokeWidth="1" strokeDasharray="2 2"/>
            </svg>
        );
    }
    const n=values.length;
    const padX=2;
    const padY=3;
    const xs=(i)=> padX+(i*width-2*padX)/(n-1);
    const ys=(v)=> {
        const range=max-min||1;
        const t=(v-min)/range;
        return height-padY-Math.max(0, Math.min(1, t))*(height-2*padY);
    };
    const points=values.map((v, i)=>[xs(i), ys(v)]);
    const linePath=points.map(([x, y], i) => (i===0 ? `M ${x} ${y}` : `L ${x} ${y}`)).join(' ');
    const areaPath=`${linePath} L ${points[n-1][0]} ${height-padY} L ${points[0][0]} ${height-padY} Z`;
    const last=points[n-1];
    return (
        <svg className='spark' width={width} height={height}>
            {style==="area" && (
                <path className='spark-area' d={areaPath} style={{fill: color, opacity: 0.15}}/>
            )}
            {style!=='dotted' && (
                <path className='spark-line' d={linePath} style={{stroke: color}}/>
            )}
            {style!='dotted' && points.map(([x, y], i)=>(
                <circle key={i} cx={x} cy={y} r={1.4} fill={color} opacity={0.3+0.7*(i/(n-1))}/>
            ))}
            <circle className='spark-dot' cx={last[0]} cy={last[1]} r={2.2} style={{fill:color}}/>
        </svg>
    )
}