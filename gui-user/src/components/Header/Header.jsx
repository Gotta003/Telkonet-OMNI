import React, { useState, useEffect } from 'react';
import "./Header.css"

// Modern Utilities
const pad2 = (n) => n<10 ? `0${n}` : `${n}`;

const formatClock=(d, prefs) => {
    if(!prefs) {
        return `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
    }
    let h=d.getHours();
    const m=pad2(d.getMinutes());
    const s=pad2(d.getSeconds());
    if(prefs.clockFormat==='12h') {
        const ampm=h>=12 ? 'PM' : 'AM';
        h=h%12 || 12;
        return prefs.showSeconds ? `${pad2(h)}:${m}:${s} ${ampm}` : `${pad2(h)}:${m} ${ampm}`;
    }
    return prefs.showSeconds ? `${pad2(h)}:${m}:${s}`:`${pad2(h)}:${m}`;
};

const formatDate = (d) => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${days[d.getDay()]} ${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
};

const IcHome=()=>(
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z" />
    <path d="M9 21V12h6v9" />
  </svg>
);

const IcDashboard=()=>(
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7" rx="1" />
    <rect x="14" y="3" width="7" height="7" rx="1" />
    <rect x="3" y="14" width="7" height="7" rx="1" />
    <rect x="14" y="14" width="7" height="7" rx="1" />
  </svg>
)

const IcSettings = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
);

export default function Header({online, view, onHome, onDashboard, onSettings, prefs, volume=30, onVolumeChange}) {
    const [now, setNow]=useState(new Date());

    useEffect(()=>{
        const t=setInterval(()=>setNow(new Date()), 1000);
        return ()=>clearInterval(t);
    }, []);

    return (
        <header className='header'>
            <div className='header-left'>
                {/*NAV*/}
                <nav className='header-nav'>
                    <button className={`nav-btn ${view==='home' ? 'active' : ''}`} onClick={onHome} title="Home">
                        <IcHome/>
                        <span>HOME</span>    
                    </button>
                    <button className={`nav-btn ${view==='dashboard' ? 'active' : ''}`} onClick={onDashboard} title="Dashboard">
                        <IcDashboard/>
                        <span>DASHBOARD</span>
                    </button>
                </nav>
                <div className="header-divider"/>
                <span className="logo-title">OMNI Room Controller</span>
            </div>
            <div className='header-right'>
                <div className='clock-wrap'>
                    <span className='clock-date'>{formatDate(now)}</span>
                    <span className='clock-time'>{formatClock(now, prefs)}</span>
                </div>
                <div className='volume-pill' title="Volume">
                    <svg width="12" height="12" viewBox='0 0 24 24' fill='none' stroke='currentColor' strokeWidth="1.8" strokeLinecap='round' strokeLinejoin='round'>
                        {volume > 0  && <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>}
                        {volume > 50 && <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>}
                    </svg>
                    <span>{volume}%</span>
                </div>
                <div className={`status-pill ${online ? 'online' : 'offline'}`}>
                    <span className='status-dot'/>
                    {online ? 'ONLINE' : 'OFFLINE'}
                </div>
                <button className={`nav-btn settings-btn ${view==='settings' ? 'active' : ''}`} onClick={onSettings} title="Settings">
                    <IcSettings/>
                    <span>SETTINGS</span>
                </button>
            </div>
        </header>
    );
}