import paho.mqtt.client as mqtt
import json
import time
import random

class MQTTClient:
    def __init__(self, broker="localhost", port=1883):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.messages = []
        
    def connect(self):
        self.client.connect(self.broker, self.port, 60)
        print(f"✅ Connected to {self.broker}:{self.port}")
        
    def publish(self, topic, data):
        payload = json.dumps(data)
        self.client.publish(topic, payload)
        print(f"📤 Published to {topic}: {payload}")
        
    def subscribe(self, topic, callback=None):
        if callback:
            self.client.on_message = callback
        else:
            self.client.on_message = self._default_callback
            
        self.client.subscribe(topic)
        print(f"📥 Subscribed to {topic}")
        
    def _default_callback(self, client, userdata, msg):
        data = json.loads(msg.payload.decode())
        self.messages.append(data)
        print(f"📨 Received: {data}")
        
    def start_loop(self):
        self.client.loop_start()
        
    def stop_loop(self):
        self.client.loop_stop()
        
    def disconnect(self):
        self.client.disconnect()
        print("👋 Disconnected")

# SIMULATE A TEMPERATURE SENSOR
mqtt_client = MQTTClient()
mqtt_client.connect()

print("\n🌡️  Simulating temperature sensor...")
print("Publishing temperature readings...\n")

try:
    while True:  # Run forever
        temp_data = {
            "sensor_id": "temp_001",
            "temperature": round(random.uniform(18.0, 28.0), 1),
            "humidity": round(random.uniform(40.0, 70.0), 1),
            "unit": "celsius",
            "timestamp": time.time()
        }
        
        mqtt_client.publish("home/livingroom/temperature", temp_data)
        time.sleep(2)  # Send every 2 seconds
        
except KeyboardInterrupt:
    print("\n\n🛑 Stopping sensor...")
    mqtt_client.disconnect()
