# Telkonet-OMNI
All in One Device developed for ICT Innovation Course at University of Trento for VDA Telkonet

# Project Structure
```bash
Telkonet-OMNI/
├── gui-user/               # React frontend (Vite)
├── main/
│   ├── main.ino            # Arduino main firmware
│   └── gui-reception.py    # Reception desk interface
├── sensor_acquisition/
│   └── sensor_acquisition.ino  # Sensor node firmware
├── app.py                  # Python backend (API server)
├── interface.py            # Hardware interface layer
├── requirements.txt        # Python dependencies
├── setup.sh                # One-shot setup script
├── Telkonet-OMNI.fzz       # Circuit diagram (open with Fritzing)
└── notebooks/              # Development & testing notebooks
```

# Prerequisites
| Tool | Version | Install |
|------|---------|---------|
|Python | 3.10+ | python.org |
|Node.js | 18+ | nodejs.org |
|npm | 9+ | Included with Node.js |
|Arduino IDE | 2.x | arduino.cc |


# Quick Start
## 1. Clone Repository:
```bash
git clone https://github.com/your-username/Telkonet-OMNI.git
cd Telkonet-OMNI
```

## 2. Python Backend
```bash
chmod +x setup.sh
./setup.sh
```

## 3. React Frontend
Go to https://nodejs.org/en/download and download Node.js compatible version. Check if it installed:
```bash
node -v
npm -v
```
Then navigate to gui-user/ folder and install node dependencies:
```bash
cd gui-user/
npm install
```
To start the developer server and continue the development of the interface, run:
```bash
npm run dev
```
To be able to run the interface with python app.py, it has to be built in dist/ folder, so just run:
```bash
npm run build
```

## 4. Run Application
```bash
cd ~/Telkonet-OMNI
source .omni_env/bin/activate
python app.py
```
