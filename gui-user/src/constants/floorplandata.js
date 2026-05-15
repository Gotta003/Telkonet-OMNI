export const ROOMS = [
  { id: 'entry',    name: 'Entry',        x: 0,   y: 0,   w: 180, h: 120, key: 'entry',     iconAt: [50, 50] },
  { id: 'hall',     name: 'Hall',         x: 0,   y: 120, w: 180, h: 180, key: 'hall',      iconAt: [50, 200] },
  { id: 'bath',     name: 'Bath',         x: 0,   y: 300, w: 180, h: 100, key: 'bath',      iconAt: [50, 340] },
  { id: 'bedroom',  name: 'Bedroom',      x: 180, y: 0,   w: 300, h: 240, key: 'bed',       iconAt: [220, 60] },
  { id: 'ensuite',  name: 'En-suite',     x: 480, y: 0,   w: 160, h: 120, key: 'ensuite',   iconAt: [520, 50] },
  { id: 'kitchen',  name: 'Kitchenette',  x: 480, y: 120, w: 160, h: 120, key: 'kitchen',   iconAt: [520, 165] },
  { id: 'living',   name: 'Living',       x: 180, y: 240, w: 460, h: 160, key: 'living',    iconAt: [220, 300] },
];

export const ROOM_META = {
  entry:   { caps: ['light'], fixtures: [{ id: 'ceiling', name: 'Overhead', icon: 'lamp', x: 90, y: 30, tone: 'warm' }] },
  hall:    { caps: ['light'], fixtures: [{ id: 'sconce-n', name: 'Sconce · N', icon: 'sconce', x: 30, y: 160, tone: 'amber' }, { id: 'sconce-s', name: 'Sconce · S', icon: 'sconce', x: 30, y: 260, tone: 'amber' }] },
  bath:    { caps: ['light', 'climate'], fixtures: [{ id: 'ceiling', name: 'Ceiling', icon: 'lamp', x: 110, y: 330, tone: 'warm' }, { id: 'mirror', name: 'Mirror', icon: 'spot', x: 40, y: 330, tone: 'cool' }, { id: 'shower', name: 'Shower', icon: 'spot', x: 160, y: 380, tone: 'neutral' }] },
  bedroom: { caps: ['light', 'climate', 'music', 'windows'], fixtures: [{ id: 'ceiling', name: 'Ceiling', icon: 'lamp', x: 330, y: 50, tone: 'warm' }, { id: 'bedside-l', name: 'Bedside · L', icon: 'lamp', x: 215, y: 220, tone: 'amber' }, { id: 'bedside-r', name: 'Bedside · R', icon: 'lamp', x: 445, y: 220, tone: 'amber' }, { id: 'reading', name: 'Reading', icon: 'spot', x: 460, y: 50, tone: 'warm' }] },
  ensuite: { caps: ['light', 'climate', 'windows'], fixtures: [{ id: 'ceiling', name: 'Ceiling', icon: 'lamp', x: 580, y: 50, tone: 'warm' }, { id: 'mirror', name: 'Mirror', icon: 'spot', x: 510, y: 95, tone: 'cool' }] },
  kitchen: { caps: ['light', 'climate', 'music', 'windows'], fixtures: [{ id: 'ceiling', name: 'Ceiling', icon: 'lamp', x: 580, y: 145, tone: 'neutral' }, { id: 'counter', name: 'Counter', icon: 'strip', x: 510, y: 220, tone: 'cool' }] },
  living:  { caps: ['light', 'climate', 'music', 'windows'], fixtures: [{ id: 'ceiling', name: 'Ceiling', icon: 'lamp', x: 410, y: 270, tone: 'warm' }, { id: 'floor-lamp', name: 'Floor lamp', icon: 'lamp', x: 215, y: 380, tone: 'amber' }, { id: 'accent', name: 'Accent', icon: 'strip', x: 620, y: 280, tone: 'accent' }, { id: 'reading', name: 'Reading', icon: 'spot', x: 595, y: 370, tone: 'warm' }] },
};

export const TONE_COLORS = {
  amber:   { glow: '#EBA967', label: '2200K' },
  warm:    { glow: '#F2C078', label: '2700K' },
  neutral: { glow: '#F2E2BC', label: '3000K' },
  cool:    { glow: '#CBD8DB', label: '4000K' },
  accent:  { glow: 'var(--accent)', label: 'tint' },
};

export const findRoom=(id)=>ROOMS.find((r)=>r.id===id) || null;

export function roomAvgLight(roomState, id) {
    const s=roomState && roomState[id];
    if(!s || !s.fixtures) {
        return 0;
    }
    const vals=Object.values(s.fixtures).filter(v=>typeof v==='number');
    if(!vals.length) {
        return 0;
    }
    return vals.reduce((a, b)=>a+b, 0)/vals.length;
}

export function roomAnyLightOn(roomState, id) {
    const s=roomState && roomState[id];
    if(!s || !s.fixtures) {
        return false;
    }
    const vals=Object.values(s.fixtures).filter(v=>typeof v==='number');
    return vals.some((v)=>v>5);
}