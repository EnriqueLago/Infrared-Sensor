import asyncio
import random
import nats
import logging
import os

# Loggin configuration
logging.basicConfig(filename='sensor_log.log', level=logging.INFO)

async def main():
    # Connect to NATS server asynchronously
    nc = nats.NATS()
    await nc.connect()

    # Variable to track whether to display sensor data
    display_data_flag = False

    # Event to signal the start or stop of displaying data
    display_event = asyncio.Event()

    # Simulates the operation of the infrared sensor
    def generate_sensor_data():
        data = []
        for _ in range(64):
            # Generates values from 0 to 65535 (16-bit unsigned)
            datum = random.randint(0, 65535)
            data.append(datum)
        return data

    # Displays the values of the sensor on the screen with decorative border
    def display_data(data):
        data_str = ", ".join(str(datum) for datum in data)
        terminal_width = os.get_terminal_size().columns
        border = "#" + "-" * (terminal_width - 2) + "#"
        print(border)
        print(f"   [Datos: {{{data_str}}}]\n{border}")

    # Handles the incoming start/stop message and starts/stops displaying data accordingly
    async def handle_instructions(msg):
        nonlocal display_data_flag
        instruction = msg.data.decode()
        if instruction == "start":
            logging.info("Received start instruction")
            display_data_flag = True
            display_event.set()  # Set the event to start displaying data
        elif instruction == "stop":
            logging.info("Received stop instruction")
            display_data_flag = False
            display_event.clear()  # Clear the event to stop displaying data

    # Start displaying data every two seconds
    async def start_displaying_data():
        while True:
            # Wait for the event to be set (start displaying data) or cleared (stop displaying data)
            await display_event.wait()
            if display_data_flag:
                # Generate data
                data = generate_sensor_data()

                # Display data
                display_data(data)

                # Wait 2 seconds
                await asyncio.sleep(2)

    # Subscribe to the topic asynchronously
    await nc.subscribe("sensor_instructions", cb=handle_instructions)

    print("Waiting for instructions...")

    # Start the task to display data
    asyncio.create_task(start_displaying_data())

    # Process messages indefinitely within the async event loop
    await asyncio.Future()  # Placeholder to keep the program running

# Run the program asynchronously
if __name__ == "__main__":
    asyncio.run(main())
