import asyncio
import random
import nats

async def main():
    # Connect to NATS server asynchronously
    nc = nats.NATS()
    await nc.connect()

    # Simulates the operation of the infrared sensor
    def generate_sensor_data():
        data = []
        for _ in range(64):
            datum = random.randint(0, 32767)
            data.append(datum)
        return data

    # Displays the values of the sensor on the screen
    def display_data(data):
        print("Sensor values:")
        for datum in data:
            print(datum)

    # Handles the incoming start message and display every two seconds the data
    async def handle_start_message(msg):
        print("Received start message")
        while True:
            # Generate data
            data = generate_sensor_data()

            # Display data
            display_data(data)

            # Wait 2 seconds
            await asyncio.sleep(2)

    # Subscribe to the topic asynchronously
    await nc.subscribe("sensor", cb=handle_start_message)

    print("Waiting for start message...")

    # Process messages indefinitely within the async event loop
    await asyncio.Future()  # Placeholder to keep the program running

# Run the program asynchronously
if __name__ == "__main__":
    asyncio.run(main())
