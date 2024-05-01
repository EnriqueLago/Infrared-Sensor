# Infrared-Sensor
**Communication User-Sensor with Nats (python)**

## Requeriments
The installation, running and deployment of [Nats-server & nats-cli](https://github.com/nats-io)

## Installation:
`git clone https://github.com/EnriqueLago/Infrared-Sensor.git`

## Configuration
```
# Start a new server in the default port:
nats-server

# For a Debug & Trace mode:
nats-server -DV
```
## Running the program
```
#To execute the program, run the following command:
python infraredSensor.py --sensor-type <sensor_type> --reading-frequency <reading_frequency> --min-value <min_value> --max-value <max_value>
```
**Note:** with the `real` sensor, the `min_value` and `max_value` values cannot be configured.
Arguments:
- `--sensor-type`: Specifies the type of sensor being used. It can be either `real` or `mockup`.
* `--reading-frequency`: Sets the frequency at which readings are taken, in seconds.
+ `--min-value`: Sets the minimum acceptable value for the sensor readings.
- `--max-value`: Sets the maximum acceptable value for the sensor readings.

## Basic usage
The sensor is controlled via nats menssages protocol: 

`nats pub <target_name> <message_txt>`

- The <target_name> is automatically generate: **sensor_instructions**
* The sensor supports three <message_txt> as instructions: **start**, **stop** and **exit**
1. `start`: Starts the sensor and therefore, the data display
2. `stop`: Stops the data display and waits
3. `exit`: Exits the nats server

### Example
```
# Starting the sensor:
nats pub sensor_instructions start
```
