import React from 'react';
import './ActivityLog.css';

const Icons = {
  success: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>,
  error: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>,
  action: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></svg>,
  info: () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6" /></svg>
};

export default function ActivityLog({entries=[], maxRows=6}) {
    const rows=entries.slice(-maxRows).reverse();
    const getIcon=(type)=>{
        if (type==='success') return <Icons.success/>;
        if (type==='error') return <Icons.error/>;
        if (type==='action') return <Icons.action/>;
        return <Icons.info/>;
    };
    return (
        <div className='card log-card'>
            <div className='eyebrow'>
                <span>ACTIVITY</span>
                <span className='bar'/>
                <span className='log-count'>{entries.length} EVTS</span>
            </div>
            <div className='log-list'>
                {rows.length===0 ? (
                    <div className='log-row info'>
                        <span className='time'>--:--:--</span>
                        <span className='log-ic'><Icons.info/></span>
                        <span className='msg'>awaiting events</span>
                    </div>
                ) : (
                    rows.map((r)=>(
                        <div key={r.id} className={`log-row ${r.type || 'info'}`}>
                            <span className='time'>{r.time}</span>
                            <span className='log-ic'>{getIcon(r.type)}</span>
                            <span className='msg'>{r.text}</span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}