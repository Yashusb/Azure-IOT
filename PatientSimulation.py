from azure.iot.device import IoTHubDeviceClient, Message
import random
import time
import json
from datetime import datetime, timezone  # Import timezone-aware datetime

CONNECTION_STRINGS = [
    "HostName=FogAndEdgeAzure.azure-devices.net;DeviceId=patient-1;SharedAccessKey=Qc/+WMy9XlBxZEpo9yVG73spGQn70DnHO3rLel3Fcg4=",  # For patient 1
    "HostName=FogAndEdgeAzure.azure-devices.net;DeviceId=patient-2;SharedAccessKey=RfYDm3ldDbJv1VNQl/SEUAril9p4K1pY0Sf8u57cVrc=",  # For patient 2
    # Add more patients here
]

SENSORS = [
    "heartbeat",
    "blood_pressure",
    "proximity",
    "temperature",
    "fall_detection"
]


def generate_sensor_value(sensor_type):
    if sensor_type == "heartbeat":
        return random.randint(60, 100)  # Normal range: 60-100 bpm
    elif sensor_type == "blood_pressure":
        systolic = random.randint(90, 140)
        diastolic = random.randint(60, 90)
        return f"{systolic}/{diastolic}"
    elif sensor_type == "proximity":
        return random.choice(["bed", "chair", "bathroom", "hallway"])
    elif sensor_type == "temperature":
        return round(random.uniform(36.0, 38.5), 1)  # Celsius
    elif sensor_type == "fall_detection":
        return 1 if random.random() > 0.9 else 0  # 10% chance of fall
    else:
        return 0


def send_patient_telemetry(client, patient_id):
    for sensor in SENSORS:
        telemetry = {
            "patientId": patient_id,
            "sensorType": sensor,
            "value": generate_sensor_value(sensor),
            "timestamp": datetime.now(timezone.utc).isoformat(),  # Ensure the timestamp is in UTC
            "alert": False
        }

        # Adding alert conditions
        if sensor == "heartbeat" and isinstance(telemetry["value"], int):
            if telemetry["value"] < 50 or telemetry["value"] > 120:
                telemetry["alert"] = True
        elif sensor == "blood_pressure":
            systolic, diastolic = map(int, telemetry["value"].split('/'))
            if systolic > 140 or diastolic > 90 or systolic < 90 or diastolic < 60:
                telemetry["alert"] = True
        elif sensor == "fall_detection" and telemetry["value"] == 1:
            telemetry["alert"] = True

        message = Message(json.dumps(telemetry))
        message.content_encoding = "utf-8"
        message.content_type = "application/json"

        print(f"Sending {sensor} data for {patient_id}: {telemetry}")
        try:
            client.send_message(message)
            print("Message sent")
        except Exception as e:
            print(f"Send error: {e}")


def connect_with_retry(client, retries=5, delay=5):
    for attempt in range(retries):
        try:
            client.connect()
            print(f"Connected to Azure IoT Hub")
            return True
        except (ConnectionDroppedError, NoConnectionError) as e:
            print(f"Connection attempt failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    print("Failed to connect after multiple attempts.")
    return False


def main():
    clients = []
    patient_ids = []

    for i, conn_str in enumerate(CONNECTION_STRINGS):
        client = IoTHubDeviceClient.create_from_connection_string(conn_str)
        clients.append(client)
        patient_ids.append(f"patient-{i+1}")  # Generate patient IDs dynamically

    try:
        # Connect all clients
        for client in clients:
            if not connect_with_retry(client):
                print("Unable to connect to IoT Hub. Exiting...")
                return

        print("Connected to Azure IoT Hub")

        # Simulate sending telemetry every 5 seconds for each patient
        while True:
            for i, client in enumerate(clients):
                send_patient_telemetry(client, patient_ids[i])  # Send data for each patient
            time.sleep(5)

    except KeyboardInterrupt:
        print("Simulation stopped by user")
    finally:
        # Shutdown all clients
        for client in clients:
            client.shutdown()
            print(f"Shutdown completed for client {client}")


if __name__ == "__main__":
    main()
