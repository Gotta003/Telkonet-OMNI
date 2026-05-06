HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <title>VDA All-in-One Device</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; margin: 0; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 15px; border: 1px solid #333; }
        .btn { background: #333; color: white; border: none; padding: 20px; border-radius: 10px; font-size: 1.2em; cursor: pointer; transition: 0.3s; }
        .btn:active { background: #007bff; transform: scale(0.95); }
        .status { font-size: 2em; color: #007bff; font-weight: bold; }
        h1 { margin-top: 30px; color: #888; }
    </style>
</head>
<body>
    <h1>Room Control</h1>
    
    <div class="grid">
        <div class="card">Temp: <div id="temp" class="status">--</div>°C</div>
        <div class="card">Luce: <div id="luce" class="status">--</div></div>
    </div>

    <div class="grid">
        <button class="btn" onclick="manda('H')">Tutto ON</button>
        <button class="btn" onclick="manda('L')">Tutto OFF</button>
        <button class="btn" onclick="manda('N')">Night Mode</button>
        <button class="btn" onclick="manda('D0')">Toggle Led 0</button>
    </div>

    <script>
        function manda(cmd) {
            fetch('/comando/' + cmd);
        }

        // Aggiorna i dati ogni secondo
        setInterval(() => {
            fetch('/api/dati')
            .then(r => r.json())
            .then(data => {
                document.getElementById('temp').innerText = data.temperature;
                document.getElementById('luce').innerText = data.light;
            });
        }, 1000);
    </script>
</body>
</html>
"""