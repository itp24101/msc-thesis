from flask import Flask, render_template, jsonify
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
import threading
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Storage file
STORAGE_FILE = "mqtt_data.json"

# Store received messages
messages = []
latest_data = {}

# Load data from file on startup
def load_data():
    global messages, latest_data
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r') as f:
                stored = json.load(f)
                messages = stored.get('messages', [])
                latest_data = stored.get('latest_data', {})
            print(f"✅ Loaded {len(messages)} messages from storage")
        except Exception as e:
            print(f"⚠️  Could not load storage: {e}")

# Save data to file
def save_data():
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump({
                'messages': messages,
                'latest_data': latest_data
            }, f, indent=2)
        print(f"💾 Saved {len(messages)} messages to storage")
    except Exception as e:
        print(f"⚠️  Could not save storage: {e}")

# Auto-save every 30 seconds
def auto_save():
    while True:
        threading.Event().wait(30)
        save_data()

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "#"  # Subscribe to all topics

# MQTT Client Setup
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        message = {
            "topic": msg.topic,
            "data": data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        messages.append(message)
        latest_data[msg.topic] = message
        
        # Keep only last 100 messages
        if len(messages) > 100:
            messages.pop(0)
            
        print(f"Received: {msg.topic} -> {data}")
    except:
        pass

# Start MQTT client in background thread
def start_mqtt():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()

# Load existing data
load_data()

# Start MQTT in a separate thread
mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
mqtt_thread.start()

# Start auto-save thread
save_thread = threading.Thread(target=auto_save, daemon=True)
save_thread.start()

# Web Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/messages')
def get_messages():
    return jsonify(messages)

@app.route('/api/latest')
def get_latest():
    return jsonify(latest_data)

if __name__ == '__main__':
    print("🚀 Starting MQTT Web Dashboard...")
    print("📡 Connecting to MQTT broker...")
    print("💾 Auto-save enabled (every 30 seconds)")
    print("🌐 Open browser at: http://localhost:5000")
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    finally:
        # Save data on shutdown
        save_data()
        print("👋 Data saved. Goodbye!")
