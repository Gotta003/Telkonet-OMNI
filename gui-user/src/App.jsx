import React, {useState, useEffect, useCallback} from 'react';
import RadialDial from './components/RadialDial/RadialDial';
import GlowSlider from './components/GlowSlider/GlowSlider';
import MiniSparkline from './components/MiniSparkline/MiniSparkline';
import ScenePanel from './components/ScenePanel/ScenePanel';
import ActivityLog from './components/ActivityLog/ActivityLog';
import FloorPlan from './components/FloorPlan/FloorPlan';
import RoomParams from './components/RoomParams/RoomParams';
import QuickActions from './components/QuickActions/QuickActions';
import Standby from './components/Standby/Standby';
import {ROOMS, ROOM_META, findRoom} from './constants/floorplandata';
import Settings, {DEFAULT_PREFS} from './components/Settings/Settings'
import Header from './components/Header/Header';
import SensorRow from './components/SensorRow/SensorRow';
import './App.css';

var POLL_INTERVAL=2000;
var HISTORY_LEN=30;
var LOG_MAX=60;

const pad2=(n)=>(n<10 ? '0'+n : ''+n);

const nowTime=()=>{
    const d=new Date();
    return `${pad2(d.getHours())}:${pad2(d.getMinutes())}:${pad2(d.getSeconds())}`;
};

const pushHistory = (arr, val) => {
    const next=[...arr, val];
    return next.length>HISTORY_LEN ? next.slice(next.length-HISTORY_LEN) : next;
};

var _logId=0;
const makeEntry = (text, type) => {
    _logId++;
    return {id: _logId, time: nowTime(), text: text, type: type || 'info'}; 
};

const makeInitialRoomState=()=>{
    const state={};
    ROOMS.forEach((r)=>{
        const meta=ROOM_META[r.id] || {fixtures: [], caps: []};
        const fixtures={};
        meta.fixtures.forEach((f)=>{
            fixtures[f.id]=0;
        });
        state[r.id]={light: 50, climate:68, music:30, windows:50, fixtures};
    });
    return state;
};

function applyPrefs(prefs) {
    const root=document.documentElement;
    //Theme
    const prefersDark=window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark=prefs.theme==='dark' || (prefs.theme==='auto' && prefersDark);
    root.setAttribute('data-theme', isDark ? 'dark' : 'light');
    //Accent Colour and Dim
    root.style.setProperty('--accent', prefs.accent);
    root.style.setProperty('--accent-soft', prefs.accent+'20');
    //Font
    root.style.setProperty('--base-font-size', `${prefs.fontSize}px`);
    const fontMap={
        modern: "'Inter', 'Segoe UI', system-ui, sans-serif",
        classic: "'Playfair Display', Georgia, serif",
        mono: "'JetBrains Mono', 'Courier New', monospace",
    };
    root.style.setProperty('--font-display', fontMap[prefs.fontStyle] || fontMap.modern);
    //Icon Sizes
    const iconScale={small: '0.75', medium: '1', large: '1.4', extralarge: '1.8'};
    root.style.setProperty('--fixture-scale', iconScale[prefs.iconSize] || '1');
    //Room Fill
    const fillMap={
        warm:    'rgba(200, 151, 58, 0.18)',
        neutral: 'rgba(100, 140, 160, 0.15)',
        minimal: 'rgba(0, 0, 0, 0.05)', 
    };
    const fillHi={
        warm:    'rgba(200, 151, 58, 0.38)',
        neutral: 'rgba(100, 140, 160, 0.30)',
        minimal: 'rgba(0, 0, 0, 0.10)',
    };
    root.style.setProperty('--room-fill-lit', fillMap[prefs.roomFill] || fillMap.warm);
    root.style.setProperty('--room-fill-hi', fillHi[prefs.roomFill] || fillHi.warm);
    //Animate Speed
    const speedMap={none: '0ms', fast: '250ms', slow: '500ms'};
    root.style.setProperty('--anim-speed', speedMap[prefs.animSpeed] || '250ms');
}

export default function App() {
    const [view, setView]=useState('dashboard');
    const [prefs, setPrefs]=useState(DEFAULT_PREFS);
    const [sensorData, setSensorData]=useState({temperature: '--', humidity: '--', light: '--'});
    const [sensorHistory, setSensorHistory]=useState({temperature: [], humidity: [], light: []});
    const [roomState, setRoomState]=useState(makeInitialRoomState());
    const [selectedRoom, setSelectedRoom]=useState(null);
    const [selectedFixture, setSelectedFixture]=useState(null);
    const [toast, setToast]=useState(null);
    const [log, setLog]=useState([makeEntry("System Boot", "info")]);
    const [online, setOnline]=useState(false);
    const [standby, setStandby]=useState(true);
    const [volume, setVolume]=useState(30);

    const addLog=useCallback((text, type)=>{
        setLog((prev)=>{
            const next=[...prev, makeEntry(text, type)];
            return next.length>LOG_MAX ? next.slice(next.length-LOG_MAX) : next;
        });
    }, []);

    const showToast=useCallback((message, type) => {
        setToast({message, type});
        setTimeout(()=>setToast(null), 3000);
    }, [])

    useEffect(()=>{applyPrefs(prefs);}, [prefs]);
    useEffect(()=>{document.documentElement.setAttribute('data-theme', 'light');}, []);
    useEffect(()=>{
        const es=new EventSource('/api/events');
        es.addEventListener('proximity', (e)=>{
            if(e.data==='wake') {
                setStandby(false);
                addLog('Proximity: screen woke', 'info');
            }
            else {
                setStandby(true);
                addLog('Proximity: screen sleeping', 'info');
            }
        });

        es.addEventListener('button', (e)=>{
            const btn=e.data;
            addLog(`Button: ${btn}`, 'info');
            switch(btn) {
                case 'home':
                    setStandby(false);
                    if (view!=='home') {
                        setView('home');
                    }
                    else {
                        setView('dashboard');
                    }
                    setSelectedRoom(null);
                    setSelectedFixture(null);
                    break;
                case 'settings':
                    setStandby(false);
                    setView('settings');
                    break;
                case 'volume_up':
                    setVolume((v)=>Math.min(100, v+10));
                    setStandby(false);
                    break;
                case 'volume_down':
                    setVolume((v)=>Math.max(0, v-10));
                    setStandby(false);
                    break;
                case 'call_service':
                    setStandby(false);
                    setView('dashboard');
                    showToast('Service requested', 'info');
                    break;
                case 'power':
                    setStandby((prev)=>!prev);
                    break;
                default:
                    break;
            }
        });
        es.onerror=()=>{
            addLog('Event stream disconnected', 'error');
        };
        return ()=>es.close();
    }, [addLog, showToast]);

    const selectRoom=(id) => {
        const next=selectedRoom===id ? null : id;
        setSelectedRoom(next);
        setSelectedFixture(null);
        fetch('/api/lights', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({room: next, fixtures: {}, selectedRoom: next}),
        }).catch(()=>{});
    };

    const selectRoomAndFixture=(roomId, fxId) => {
        setSelectedRoom(roomId);
        setSelectedFixture(fxId);
    }

    const selectFixture=(fxId)=>{
        setSelectedFixture(fxId);
    };

    const dismissSelection=()=>{
        if(view=='home') {
            setSelectedRoom(null);
            setSelectedFixture(null);
        }
    };

    const updateParam=(roomId, key, val)=>{
        setRoomState((prev)=>({
            ...prev,
            [roomId]: {
                ...prev[roomId],
                [key]: val,
            },
        }));
        if(key==='windows') {
            fetch('/api/curtain', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({value: val, room: roomId}),
            }).catch((e)=>addLog(`Curtain error: ${e.message}`, 'error'));
        }
    };

    const updateFixture=(roomId, fxId, val) => {
        setRoomState((prev) =>  {
            const newFixtures={...(prev[roomId]?.fixtures || {}), [fxId]: val};
            const newRoom={...prev[roomId], fixtures: newFixtures};
            const newState={...prev, [roomId]: newRoom};

            fetch('/api/lights', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    room: roomId,
                    fixtures: newFixtures,
                    selectedRoom: selectedRoom,
                }),
            }).catch((e)=>addLog(`Light sync error: ${e.message}`, 'error'));
            return newState;
        });
    };

    const handleActivateScene = (scene) => {
        addLog(`Scene activated: ${scene.name}`, 'info');
        setRoomState((prev)=>{
            const next={...prev};
            ROOMS.forEach((r)=>{
                const meta=ROOM_META[r.id] || {caps: [], fixtures: []};
                const prevRoom=prev[r.id] || {};
                const prevFixtures=prevRoom.fixtures || {};
                const newFixtures={...prevFixtures};
                if(scene.params.light!==undefined) {
                    meta.fixtures.forEach((f)=>{
                        newFixtures[f.id]=scene.params.light;
                    });
                }
                next[r.id]={
                    ...prevRoom,
                    fixtures: newFixtures,
                    ...(meta.caps.includes('climate') && scene.params.climate!==undefined ? {climate: scene.params.climate} : {}),
                    ...(meta.caps.includes('music') && scene.params.music!==undefined ? {music: scene.params.music} : {}),
                    ...(meta.caps.includes('windows') && scene.params.windows!==undefined ? {windows: scene.params.windows} : {}),
                };
            });
            return next;
        });
        showToast(`Scene: ${scene.name}`, "success");

        setTimeout(()=>{
            setRoomState((current)=>{
                ROOMS.forEach((r)=>{
                    const fixtures=current[r.id]?.fixtures || {};
                    if(Object.keys(fixtures).length>0) {
                        fetch('/api/lights', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({room: r.id, fixtures, selectedRoom}),
                        }).catch(()=>{});
                    }
                });
                return current;
            });
        }, 50)
    };

    const sendCommand=(cmd, label) => {
        addLog(`CMD -> ${cmd}`, 'info');
        fetch(`/api/command/${cmd}`).then((res)=>{
            if(!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        }).then(()=>{
            showToast(`✓ ${label}`, 'success');
            addLog(`${label} OK`, 'success');
        }).catch((err)=>{
            addLog(`Command Failed: ${err.message}`, 'error');
            showToast('Command Failed', 'error');
        });
        if(cmd==='lights_on') {
            setRoomState((prev)=>{
                const next={...prev};
                ROOMS.forEach((r)=>{
                    const fx={...(prev[r.id]?.fixtures || {})};
                    (ROOM_META[r.id]?.fixtures || []).forEach((f)=>{fx[f.id]=70;});
                    next[r.id]={...prev[r.id], fixtures: fx};
                });
                return next;
            });
        }
        else if(cmd=='lights_off') {
            setRoomState((prev)=>{
                const next={...prev};
                ROOMS.forEach((r)=>{
                    const fx={...(prev[r.id]?.fixtures || {})};
                    (ROOM_META[r.id]?.fixtures || []).forEach((f)=>{fx[f.id]=0;});
                    next[r.id]={...prev[r.id], fixtures: fx};
                });
                return next;
            });
        }
        else if(cmd=='all_on') {
            setRoomState((prev)=>{
                const next={...prev};
                ROOMS.forEach((r)=>{
                    const fx={...(prev[r.id]?.fixtures || {})};
                    (ROOM_META[r.id]?.fixtures || []).forEach((f)=>{fx[f.id]=80;});
                    next[r.id]={...prev[r.id], fixtures, climate: 70, music: 50, windows: 60};
                });
                return next;
            });
        }
        else if(cmd=='power_off') {
            setRoomState(makeInitialRoomState());
        }
    };

    useEffect(() => {
        const poll = () => {
        fetch('/api/dati')
            .then((res) => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
            })
            .then((json) => {
            setOnline((prevOnline) => {
                if (!prevOnline) addLog('Sensor link Established', 'success');
                return true;
            });
            
            setSensorData(json);
            setSensorHistory((prev) => {
                const t = parseFloat(json.temperature);
                const u = parseFloat(json.humidity);
                const l = parseFloat(json.light);
                return {
                temperature: isNaN(t) ? prev.temperature : pushHistory(prev.temperature, t),
                humidity: isNaN(u) ? prev.humidity : pushHistory(prev.humidity, u),
                light: isNaN(l) ? prev.light : pushHistory(prev.light, l),
                };
            });
            })
            .catch((err) => {
            setOnline((prevOnline) => {
                if (prevOnline) {
                addLog(`Sensor Lost: ${err.message}`, 'error');
                showToast('Connection Lost', 'error');
                }
                return false;
            });
            });
        };
        poll();
        const intervalId=setInterval(poll, POLL_INTERVAL);
        return () => clearInterval(intervalId);
    }, [addLog, showToast]);

    const activeRoom=selectedRoom ? findRoom(selectedRoom) : null;
    const homePanelOpen=view==='home' && selectedRoom!==null;

    return (
        <div className={`app view-${view}`}>
            {standby && (<Standby onWake={() => {
                setStandby(false);
                setView('dashboard');
            }}/>)}
            <Header online={online} view={view} onHome={()=>{setStandby(false); setView('home'); setSelectedRoom(null); setSelectedFixture(null);}} onDashboard={()=>{setStandby(false); setView('dashboard');}} onSettings={()=>{setStandby(false); setView('settings');}} prefs={prefs} volume={volume} onVolumeChange={setVolume}/>
            {/*SETTINGS VIEW*/}
            {view==='settings' && (
                <Settings prefs={prefs} onChange={setPrefs}/>
            )}
            {/*DASHBOARD + HOME VIEWS*/}
            {view!=='settings' && (
                <div className='body' onClick={view==='home' ? dismissSelection : undefined}>
                    {/*LEFT - FLOOR PLAN */}
                    <section className="panel-map" onClick={(e)=>e.stopPropagation()}>
                        {view==='dashboard' && (
                            <div className='panel-map-header'>
                                <span className='panel-label'>FLOOR PLAN</span>
                            </div>
                        )}
                        <div className="blueprint">
                            <FloorPlan selectedId={selectedRoom} onSelect={selectRoom} roomState={roomState} selectedFixture={selectedFixture} onSelectFixture={selectRoomAndFixture} homeMode={view==='home'} onDismiss={view==='home' ? dismissSelection : undefined} panelWidth={homePanelOpen ? 380 :0}/>
                            {view==='dashboard' &&(
                                <>
                                    <div className='section-divider'/>
                                    <ScenePanel onActivate={handleActivateScene}/>
                                </>
                            )}
                        </div>
                    </section>
                    {/*RIGHT - CONTROLS*/}
                    {view==='dashboard' && (
                        <aside className="panel-ctrl">
                            <div className='panel-label'>SENSOR READOUT</div>
                            <SensorRow data={sensorData} history={sensorHistory}/>
                            <div className='section-divider'/>
                            <RoomParams 
                            room={activeRoom}
                            roomState={roomState}
                            onChangeParam={updateParam}
                            onChangeFixture={updateFixture}
                            selectedFixture={selectedFixture}
                            onSelectFixture={selectFixture}/>
                            <div className='section-divider'/>
                            <QuickActions onAction={sendCommand}/>
                            <div className='section-divider'/>
                            <ActivityLog entries={log} maxRows={6}/>
                        </aside>
                    )}
                    {/*RIGHT - FOCUS MODE */}
                    {view==='home' && (
                        <aside className={`panel-ctrl panel-home ${homePanelOpen ? 'open' : ''}`} onClick={(e)=>e.stopPropagation()}>
                            <div className='panel-home-header'>
                                <div className='panel-label'>
                                {activeRoom ? activeRoom.name.toUpperCase() : ""}
                                </div>
                                <button className='panel-home-close' onClick={()=>{setSelectedRoom(null); setSelectedFixture(null);}}
                                title="Close">x</button>
                            </div>
                            <RoomParams 
                            room={activeRoom} 
                            roomState={roomState} 
                            onChangeParam={updateParam}
                            onChangeFixture={updateFixture}
                            selectedFixture={selectedFixture}
                            onSelectFixture={selectFixture}
                            />
                        </aside>
                    )}
                </div>
            )}
            {toast && (
                <div className="toast-container">
                    <div className={`toast ${toast.type || ''}`}>
                        <span className='toast-dot'/>
                        {toast.message}
                    </div>
                </div>
            )}
        </div>
    )
}