import random
import time
from azure.iot.device import IoTHubDeviceClient, Message

# Paste your connection string here
CONN_STR = "HostName=ElderlyCareHub.azure-devices.net;DeviceId=HeartRate1;SharedAccessKey=kNWeneQvTqyIaaZ0AYtWYBbvLKa4kbJHwzyaxAfBKVA="
client = IoTHubDeviceClient.create_from_connection_string(CONN_STR)

while True:
    heart_rate = random.randint(60, 100)  # Fake heart rate
    message = Message(f'{{"heart_rate1": {heart_rate}}}')
    client.send_message(message)
    print(f"Sent: heart_rate1 = {heart_rate} bpm")
    time.sleep(10)  # Send every 10 seconds