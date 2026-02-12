// server.js - Save this on your VPS
const express = require('express');
const mqtt = require('mqtt');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

app.use(express.json());
app.use(express.static('public')); // For your dashboard

const TEAM_ID = "ubuliza_david";
const client = mqtt.connect('mqtt://157.173.101.159');

// Forward MQTT updates to WebSockets (Dashboard)
client.on('connect', () => {
    client.subscribe(`rfid/${TEAM_ID}/card/status`);
    console.log("Connected to MQTT Broker");
});

client.on('message', (topic, message) => {
    wss.clients.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(message.toString());
        }
    });
});

// HTTP Endpoint for Top-Up
app.post('/topup', (req, res) => {
    const { uid, amount } = req.body;
    const payload = JSON.stringify({ uid, amount });
    client.publish(`rfid/${TEAM_ID}/card/topup`, payload);
    res.json({ status: "Top-up command sent to device" });
});

server.listen(9216, () => console.log('Backend running on port 9216'));