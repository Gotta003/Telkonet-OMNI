import React from 'react';
import './QuickActions.css'

const Icons = {
  lightOn: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M8 3h8l3 8H5zM12 11v6M8 21h8M10 17h4v4h-4z" /></svg>,
  lightOff: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" /></svg>,
  climateOn: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 12c0-3 1.5-7 5-7s5 4 0 4-5-1-5 3zM12 12c-3 0-7 1.5-7 5s4 5 4 0-1-5 3-5zM12 12c0 3-1.5 7-5 7s-5-4 0-4 5 1 5-3zM12 12c3 0 7-1.5 7-5s-4-5-4 0 1 5-3 5z"/><circle cx="12" cy="12" r="1.5" /></svg>,
  climateOff: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 14.76V4a2 2 0 0 0-4 0v10.76a4 4 0 1 0 4 0z" /></svg>,
  allOn: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M13 3 5 14h6l-1 7 8-11h-6l1-7z" /></svg>,
  powerOff: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18.36 6.64a9 9 0 1 1-12.72 0M12 2v10" /></svg>
};

const ACTIONS = [
  { label: 'Lights On',   cmd: 'lights_on',   icon: 'lightOn',    type: 'primary' },
  { label: 'Lights Off',  cmd: 'lights_off',  icon: 'lightOff',   type: 'default' },
  { label: 'Climate On',  cmd: 'climate_on',  icon: 'climateOn',  type: 'primary' },
  { label: 'Climate Off', cmd: 'climate_off', icon: 'climateOff', type: 'default' },
  { label: 'All On',      cmd: 'all_on',      icon: 'allOn',      type: 'primary' },
  { label: 'Power Off',   cmd: 'power_off',   icon: 'powerOff',   type: 'danger' },
];

export default function QuickActions({onAction}) {
    return (
        <div className='card actions-card'>
            <div className='eyebrow'>
                <span>QUICK ACTIONS</span>
                <span className='bar'/>
            </div>
            <div className='actions-grid'>
                {ACTIONS.map((a)=>{
                    const IconComponent=Icons[a.icon];
                    return (
                        <button key={a.cmd} className={`qa-btn qa-${a.type}`} onClick={()=>onAction && onAction(a.cmd, a.label)}>
                            <span className="qa-ic">
                                {IconComponent && <IconComponent/>}
                            </span>
                            <span className='qa-label'>{a.label}</span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}