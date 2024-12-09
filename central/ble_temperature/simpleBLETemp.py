import asyncio
from bleak import BleakScanner, BleakClient

# UUIDs for temperature service and characteristic (ensure these match Arduino code)
TEMPERATURE_SERVICE_UUID = "00000000-5EC4-4083-81CD-A10B8D5CF6EC"
TEMPERATURE_CHARACTERISTIC_UUID = "00000001-5EC4-4083-81CD-A10B8D5CF6EC"
DEVICE_NAME = "BLE-TEMP"  # BLE device name as set in the Arduino sketch

async def connect_to_device():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    
    target_device = None
    for device in devices:
        print(f"Found device: {device.name}, Address: {device.address}")
        if device.name == DEVICE_NAME:
            target_device = device
            break

    if not target_device:
        print(f"Device '{DEVICE_NAME}' not found. Make sure it's advertising and try again.")
        return

    print(f"Connecting to {DEVICE_NAME} at address {target_device.address}...")
    async with BleakClient(target_device.address) as client:
        print(f"Connected to {DEVICE_NAME}!")

        print("Discovering services and characteristics...")
        # Properly discover services and match UUIDs
        for service in client.services:
            print(f"Service: {service.uuid}")
            if service.uuid.lower() == TEMPERATURE_SERVICE_UUID.lower():
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid} - Properties: {char.properties}")
                    if char.uuid.lower() == TEMPERATURE_CHARACTERISTIC_UUID.lower():
                        print("Subscribing to temperature notifications...")
                        
                        # Handle temperature notifications
                        def handle_temperature_data(sender, data):
                            temperature = data.decode("utf-8")
                            print(f"Temperature: {temperature} °C")

                        await client.start_notify(char.uuid, handle_temperature_data)
                        print("Receiving temperature data... Press Ctrl+C to exit.")
                        try:
                            while True:
                                await asyncio.sleep(1)
                        except KeyboardInterrupt:
                            print("\nStopping notifications...")
                            await client.stop_notify(char.uuid)
                            print("Disconnected.")
                            return
        print("Temperature service or characteristic not found on the device.")

if __name__ == "__main__":
    asyncio.run(connect_to_device())
