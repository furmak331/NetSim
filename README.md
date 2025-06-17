# Python Network Simulator

This is a Python implementation of a network simulator that demonstrates the functionality of different network layers.

## Features

The simulator implements:

### Layer 1 (Physical Layer)
- End devices creation
- Hub creation and data broadcasting
- Physical connections between devices

### Layer 2 (Data Link Layer)
- Switch implementation with address learning
- Error control using CRC
- Flow control protocols

### Layer 3 (Network Layer)
- Router implementation
- IP addressing (IPv4)
- ARP for MAC address resolution

### Layer 4 (Transport Layer) 
- Port assignment for processes
- Flow control

### Layer 5 (Application Layer)
- Email service implementation
- Search engine implementation

## How to Use

1. Run the simulator:
   ```
   python main.py
   ```

2. Follow the prompts to:
   - Create a network topology
   - Select sender and receiver devices
   - Test data transfer between devices
   - Test application layer services (email and search)

## Testing Scenarios

1. **Physical Layer Test**: Create two end devices with a direct connection.
2. **Data Link Layer Test**: Create a switch with multiple connected end devices.
3. **Hub and Switch Test**: Create two hubs connected by a switch with multiple end devices.
4. **Application Layer Test**: Use the email and search engine services.

## Code Structure

- `main.py`: Entry point for the simulator
- `network_simulator.py`: Main simulator logic
- `end_devices.py`: End devices implementation
- `hub.py`: Hub implementation
- `switch.py`: Switch implementation
- `router.py`: Router implementation
- `crc_for_datalink.py`: CRC for error detection
- `domain_name_server.py`: DNS implementation
- `email_service.py`: Email service implementation
- `search_service.py`: Search engine implementation
- `search_engine_server.py`: Search engine server implementation
