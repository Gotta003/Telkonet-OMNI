import React from 'react';
import './Settings.css';

const Section=({title, children})=>(
    <div className='set-section'>
        <div className='set-section-title'>{title}</div>
        {children}
    </div>
);

const OptionRow=({label, hint, children})=>(
    <div className='set-row'>
        <div className='set-row-info'>
            <span className='set-row-label'>{label}</span>
            {hint && <span className='set-row-hint'>{hint}</span>}
        </div>
        <div className='set-row-control'>{children}</div>
    </div>
);

const SegmentedControl=({options, value, onChange})=>(
    <div className='seg-ctrl'>
        {options.map((opt)=>(
            <button key={opt.value} className={`seg-btn ${value===opt.value ? 'active' : ''}`} onClick={()=>onChange(opt.value)}>
                {opt.icon && <span className='seg-icon'>{opt.icon}</span>}
                <span>{opt.label}</span>
            </button>
        ))}
    </div>
);

const SliderControl=({value, min, max, step=1, onChange, formatLabel}) => (
    <div className='set-slider-wrap'>
        <input type="range" className='set-slider' min={min} max={max} step={step} value={value} onChange={(e)=>onChange(Number(e.target.value))}/>
        <span className='set-slider-val'>{formatLabel ? formatLabel(value) : value}</span>
    </div>
);

export default function Settings({prefs, onChange}) {
    const set=(key, val) => onChange({...prefs, [key]: val});
    return (
        <div className='settings-page'>
            <div className='settings-inner'>
                <div className='settings-hero'>
                    <h1 className='settings-title'>Personalisation</h1>
                    <p className='settings-sub'>Adjust the interface to your comfort and accessibility needs.</p>
                </div>
                {/*APPEARANCE*/}
                <Section title="Appearance">
                    <OptionRow label="Theme" hint="Choose between light and dark mode">
                        <SegmentedControl value={prefs.theme} onChange={(v)=>set('theme', v)} options={[
                            { value: 'light', label: 'Light', icon: '☀️' },
                            { value: 'dark',  label: 'Dark',  icon: '🌙' },
                            { value: 'auto',  label: 'Auto',  icon: '⚙️' },
                        ]}
                        />
                    </OptionRow>
                    <OptionRow label="Accent colour" hint="Highlight colour used throughout the interface">
                        <div className='colour-swatchess'>
                            {[
                                {name: 'Gold', value: '#C8973A'},
                                {name: 'Copper', value: '#B5663A'},
                                {name: 'Sage', value: '#5A8A6A'},
                                {name: 'Slate', value: '#4A6FA5'},
                                {name: 'Plum', value: '#7A4A8A'},
                                {name: 'Charcoal', value: '#4A4A4A'},
                            ].map((c)=>(
                                <button key={c.value} className={`swatch ${prefs.accent===c.value ? 'active' : ''}`} style={{background: c.value}} title={c.name} onClick={()=>set('accent', c.value)}/>
                            ))}
                        </div>
                    </OptionRow>
                </Section>
                {/*TYPOGRAPHY*/}
                <Section title="Typography">
                    <OptionRow label="Font size" hint="Base size for all text - larger helps readability">
                        <SliderControl value={prefs.fontSize} min={14} max={22} step={1} onChange={(v)=>set('fontSize', v)} formatLabel={(v)=>`${v}px`}/>
                    </OptionRow>
                    <OptionRow label="Font Style" hint="Interface typeface">
                        <SegmentedControl value={prefs.fontStyle} onChange={(v)=>set('fontStyle', v)} options={[
                            {value: 'mordern', label: 'Modern'},
                            {value: 'classic', label: 'Classic'},
                            {value: 'mono', label: 'Mono'},
                        ]}/>
                    </OptionRow>
                </Section>
                {/*FLOOR PLAN*/}
                <Section title="Floor Plan">
                    <OptionRow label="Fixture icon size" hint="Size of light fixture markers on the plan">
                        <SegmentedControl value={prefs.iconSize} onChange={(v)=>set('iconSize', v)}
                        options={[
                            {value: 'small', label: 'Small'},
                            {value: 'medium', label: 'Medium'},
                            {value: 'large', label: 'Large'},
                        ]}/>
                    </OptionRow>
                    <OptionRow label="Room Fill Style" hint="How lit rooms are shown on the plan">
                        <SegmentedControl value={prefs.roomFill} onChange={(v)=>set('roomFill', v)} options={[
                            {value: 'warn', label: 'Warm'},
                            {value: 'neutral', label: 'Neutral'},
                            {value: 'minimal', label: 'Minimal'},
                        ]}/>
                    </OptionRow>
                </Section>
                {/*CLOCK + STATUS*/}
                <Section title="Clock & Status">
                    <OptionRow label="Clock format" hint="How the time is shown in header">
                        <SegmentedControl value={prefs.clockFormat} onChange={(v)=>set('clockFormat', v)} options={[
                            {value: '24h', label: '24h'},
                            {value: '12h', label: '12h'},
                        ]}/>
                    </OptionRow>
                    <OptionRow label="Show seconds" hint="Display seconds in the clock">
                        <SegmentedControl value={prefs.showSeconds} onChange={(v)=>set('showSeconds', v)} options={[
                            {value: true, label: 'On'},
                            {value: false, label: 'Off'},
                        ]}/>
                    </OptionRow>
                </Section>
                {/*INTERACTION*/}
                <Section title="Interaction">
                    <OptionRow label="Panel animation speed" hint="How fast the right panel slides in and out">
                        <SegmentedControl value={prefs.animSpeed} onChange={(v)=>set('animSpeed', v)} options={[
                            {value: 'none', label: 'None'},
                            {value: 'fast', label: 'Fast'},
                            {value: 'slow', label: 'Slow'},
                        ]}/>
                    </OptionRow>
                </Section>
                <div className="settings-reset">
                    <button className="reset-btn" onClick={()=>onChange(DEFAULT_PREFS)}>
                        Reset to defaults
                    </button>
                </div>
            </div>
        </div>
    );
}

export const DEFAULT_PREFS={
    theme: 'light',
    accent: '#C8973A',
    fontSize: 16,
    fontStyle: 'modern',
    iconSize: 'medium',
    roomFill: 'warm',
    clockFormat: '24h',
    showSeconds: true,
    animSpeed: 'fast',
};