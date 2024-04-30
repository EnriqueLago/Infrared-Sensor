import asyncio
import random
import nats
import logging
import os
import sys
import argparse

# Create the "logs" directory if it does not exist
logs_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure the output of logs to the "sensor_log.log" file inside the "logs" folder
log_file = os.path.join(logs_dir, 'sensor_log.log')
logging.basicConfig(filename=log_file, level=logging.INFO)

async def main(args):
    if args.sensor_type == 'real':
        print("Attention! The real sensor is not implemented yet.")
        while True:
            user_input = input("Do you want to change to the mockup? (Y/N): ").strip().lower()
            if user_input in ("y", "n"):
                break
            else:
                print("Please enter Y or N.")
        if user_input == "y":
            args.sensor_type = 'mockup'
        else:
            print("The program will close")
            sys.exit()
    
     # Controls the min and max values
    if args.min_value < 0:
        args.min_value = 0
    if args.max_value > 65535:
        args.max_value = 65535
    if args.min_value > args.max_value:
        print("The minimum value cannot be greater than the maximum value.")
        sys.exit()

    # Connect to NATS server asynchronously
    try:
        nc = nats.NATS()
        await nc.connect()
    except Exception as e:  # Catch any connection-related errors
        logging.error(f"Failed to connect to NATS server: {e}")
        sys.exit(1)

    # Variable to track whether to display sensor data
    display_data_flag = False

    # Event to signal the start or stop of displaying data
    display_event = asyncio.Event()

    # Simulates the operation of the infrared sensor
    def generate_sensor_data(min_value, max_value):
        data = []
        for _ in range(64):
            datum = random.randint(min_value, max_value)
            data.append(datum)
        return data

    # Displays the values of the sensor on the screen with decorative border
    def display_data(data):
        data_str = ", ".join(str(datum) for datum in data)
        terminal_width = os.get_terminal_size().columns
        border = "#" + "-" * (terminal_width - 2) + "#"
        print(border)
        print(f"   [Datos: {{{data_str}}}]\n{border}")

    # Handles the incoming start/stop/exit message and starts/stops/displaying data or exits accordingly
    async def handle_instructions(msg):
        nonlocal display_data_flag
        instruction = msg.data.decode()
        if instruction == "start":
            logging.info("Received start instruction")
            display_data_flag = True
            display_event.set()  # Set the event to start displaying data
        elif instruction == "stop":
            logging.info("Received stop instruction")
            if display_data_flag:  # Solo permite "stop" si ya está en curso "start"
                display_data_flag = False
                display_event.clear()  # Clear the event to stop displaying data
                print("Waiting for instructions...")
            else:
                print("Cannot stop. Start command has not been received.")
        
        elif instruction == "exit": #The nats connection stop
            logging.info("Received exit instruction")
            display_data_flag = False
            display_event.clear()
            while True:
                user_input = input("Do you want to continue using the program? (Y/N): ").strip().lower()
                if user_input in ("y", "n"):
                    break
                else:
                    print("Please enter Y or N.")
            if user_input == "n":
                await nc.close()
                sys.exit()
            print("Waiting for instructions...")
            
    # Start displaying data every two seconds
    async def start_displaying_data():
        while True:
            # Wait for the event to be set (start displaying data) or cleared (stop displaying data)
            await display_event.wait()
            if display_data_flag:
                # Generate data
                data = generate_sensor_data(args.min_value, args.max_value)

                # Display data
                display_data(data)

                # Wait 2 seconds
                await asyncio.sleep(args.reading_frequency)
    
    # Subscribe to the topic asynchronously
    await nc.subscribe("sensor_instructions", cb=handle_instructions)

    print("Waiting for instructions...")

    # Start the task to display data
    asyncio.create_task(start_displaying_data())

    # Process messages indefinitely within the async event loop
    await asyncio.Future()  # Placeholder to keep the program running

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sensor parameters control')
    parser.add_argument('--sensor-type', type=str, choices=['mockup', 'real'], default='mockup', help='Type of sensor to use (mockup or real)')
    parser.add_argument('--reading-frequency', type=int, default=2, help='Frequency of sensor readings in seconds')
    parser.add_argument('--min-value', type=int, default=0, help='Minimum value generated by the infrared sensor when it is of mockup type')
    parser.add_argument('--max-value', type=int, default=65535, help='Maximum value generated by the infrared sensor when it is of mockup type')
    args = parser.parse_args()
    
    asyncio.run(main(args))
