import React from 'react';
import RadialDial from '../RadialDial/RadialDial';
import MiniSparkline from '../MiniSparkline/MiniSparkline';
import './SensorRow.css'

const SENSORS = [
  { key: 'temperature', label: 'TEMP',     unit: '°C', icon: '🌡️', color: '#f97316', max: 50 },
  { key: 'humidity',    label: 'HUMIDITY', unit: '%',  icon: '💧', color: '#38bdf8', max: 100 },
  { key: 'light',       label: 'AMBIENT',  unit: 'lx', icon: '☀️', color: '#e8a020', max: 1000 },
];

export default function SensorRow({data={}, history={}}) {
    return (
        <div className='sensor-row'>
            {SENSORS.map((sensor)=>{
                const val=data[sensor.key];
                const numericValue=typeof val === 'number' ? val : parseFloat(val);
                const hist=history[sensor.key] || [];
                return (
                    <div key={sensor.key} className='sensor-col'>
                        <RadialDial
                            value={isFinite(numericValue) ? numericValue : 0}
                            max={sensor.max}
                            label={sensor.label}
                            unit={sensor.unit}
                            icon={sensor.icon}
                            color={sensor.color}
                            size={94}
                        />
                        <div className='sensor-spark'>
                            <MiniSparkline
                                values={hist}
                                width={84}
                                height={20}
                                min={0}
                                max={sensor.max}
                                color={sensor.color}
                                style="area"
                            />
                        </div>
                    </div>
                )
            })}
        </div>
    )
}