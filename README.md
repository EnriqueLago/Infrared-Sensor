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
## Basic usage
The sensor is controlled via nats menssages protocol: 

`nats pub <target_name> <message>`

- The <target_name> is automatically generate: **sensor_instructions**
* The sensor supports three <message> as instructions: **start**, **stop** and **exit**
1. start: Starts the sensor and therefore, the data display
2. stop: Stops the data display and waits
3. exit: Exits the nats server

### Example
```
# Starting de sensor:
nats pub sensor_instructions start
```
