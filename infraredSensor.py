import asyncio
import random
import logging
import os
import sys
import argparse
import nats 
from nats.errors import ConnectionClosedError, TimeoutError


# --------------------AUXILIAR FUNCTIONS------------------------- #
# Simulates the operation of the infrared sensor
def generate_sensor_data(min_value, max_value):
    data = []
    for _ in range(64):
        datum = random.randint(min_value, max_value)
        data.append(datum)
    return data

# Función que modifica la variable global
def modify_global_variable():
    global continue_program  # Declaración global solo necesaria una vez en la función
    continue_program = False

# Displays the values of the sensor on the screen with decorative border
def display_data(data):
    data_str = ", ".join(str(datum) for datum in data)
    terminal_width = os.get_terminal_size().columns
    border = "#" + "-" * (terminal_width - 2) + "#"
    print(border)
    print(f"   [Datos: {{{data_str}}}]\n{border}")

# -------------------------MAIN CODE--------------------------#
async def main(args):
    #--------------------EVENT HANDLERS-----------------------#
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
                modify_global_variable()
                logging.info("Exit of the program confirmed")
                return
            print("Waiting for instructions...")
            
    # Start displaying data every two seconds
    async def start_displaying_data():
        while True:
            # Waits for the event to be set (start displaying data) or cleared (stop displaying data)
            await display_event.wait()
            if display_data_flag:
                data = generate_sensor_data(args.min_value, args.max_value) # Generate data
                display_data(data) 
                await asyncio.sleep(args.reading_frequency) # Waits as many seconds as indicated by the user (with the arg reading_frequency)
     
    #------------------------------MAIN---------------------------#
    # Variable to control whether to continue with the program
    global continue_program 
    continue_program = True
    
    # Warns that the real sensor functioning is not implemented yet and offers to change to mockup            
    if args.sensor_type == 'real':
        print("Attention! The real sensor functioning is not implemented yet.")
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
        nc = await asyncio.wait_for(nats.connect(), timeout=10) # Connects to de default port nats://localhost:4222
        logging.info("Connection to NATS server (nats://localhost:4222) succesful")
    except ConnectionClosedError:
        print("Connection to NATS server refused. Please make sure the server is running and reachable.")
        sys.exit()
    except TimeoutError:
        print("Connection to NATS server timed out. Please check your network connection and try again.")
        sys.exit()
    except Exception as e:  # Catch any other unexpected errors
        print(f"Failed to connect to NATS server: {e}")
        sys.exit()

    # Variable to track whether to display sensor data
    display_data_flag = False
    
    # Subscribe to the topic asynchronously
    await nc.subscribe("sensor_instructions", cb=handle_instructions)

    print("Waiting for instructions...")
  
    # Event to signal the start or stop of displaying data
    display_event = asyncio.Event()

    # Start the task to display data
    asyncio.create_task(start_displaying_data())

    # Process messages indefinitely within the async event loop
    try:
        while continue_program:
            await asyncio.sleep(0.1)  # Brief pause to avoid consuming too many resources
    finally:
        # Close the connection before exiting the program if continue_program is False
        if not continue_program:
            await nc.close()

if __name__ == "__main__":
    
    # Create an ArgumentParser object for parsing command-line arguments
    parser = argparse.ArgumentParser(description='Sensor parameters control')
    
    # Add command-line arguments for specifying sensor type, reading frequency, minimum value, and maximum value
    parser.add_argument('--sensor-type', type=str, choices=['mockup', 'real'], default='mockup', help='Type of sensor to use (mockup or real)')
    parser.add_argument('--reading-frequency', type=int, default=2, help='Frequency of sensor readings in seconds')
    parser.add_argument('--min-value', type=int, default=0, help='Minimum value generated by the infrared sensor when it is of mockup type')
    parser.add_argument('--max-value', type=int, default=65535, help='Maximum value generated by the infrared sensor when it is of mockup type')

    # Parse the command-line arguments and store them in the 'args' variable
    args = parser.parse_args()
    
    # Check if sensor type is 'real' and if so, ensure that min and max values are not provided
    if args.sensor_type == 'real':
        if args.min_value != 0 or args.max_value != 65535:
            parser.error("For 'real' sensor type, minimum and maximum values should not be provided.")
            
    # Create the "logs" directory if it does not exist
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Configure the output of logs to the "sensor_log.log" file inside the "logs" folder
    log_file = os.path.join(logs_dir, 'sensor_log.log')
    logging.basicConfig(filename=log_file, level=logging.INFO)
    
    # Record the values of the arguments provided by the user in the log file for reference.
    logging.info("New program execution. User provided arguments:")
    logging.info(f"Sensor type: {args.sensor_type}")
    logging.info(f"Reading frequency: {args.reading_frequency}")
    logging.info(f"Minimum value: {args.min_value}")
    logging.info(f"Maximum value: {args.max_value}")
    
    asyncio.run(main(args))