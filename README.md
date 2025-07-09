# Python Network Simulator

This Python implementation of a network simulator demonstrates the functionality of different network layers with a complete protocol stack approach. It visually shows how data travels through each layer of the network model, demonstrating how protocols operate at each layer.

## Features

The simulator implements the full network protocol stack:

### Layer 5 (Application Layer)
- DNS for hostname-to-IP resolution
- Application data processing
- Email and search engine services simulation

### Layer 4 (Transport Layer)
- **Port Management**: Well-known ports (0-1023) and ephemeral ports (1024-65535)
- **Process Registration**: Process-to-process communication with port allocation
- **TCP Implementation**: 
  - Three-way handshake connection establishment
  - Sliding window flow control (Go-Back-N protocol)
  - Reliable data transmission with acknowledgments
  - Error detection and retransmission
  - Connection state management
- **UDP Implementation**:
  - Connectionless datagram transmission
  - Simple header format with port information
- **Flow Control**: Reusable sliding window implementation for both transport and data link layers

### Layer 3 (Network Layer)
- Router implementation with routing tables
- IP addressing and subnet management
- Multi-network routing with next-hop determination
- ARP for IP-to-MAC resolution

### Layer 2 (Data Link Layer)
- Switch implementation with MAC address learning
- Error detection using CRC-32
- Frame creation and processing
- Flow control protocols

### Layer 1 (Physical Layer)
- End devices creation
- Hub operation with broadcasting
- Physical signal transmission simulation

### Layer 5 (Application Layer)
- Email service implementation
- Search engine implementation
- DNS for hostname-to-IP resolution

## How to Use

### Running the Demo

The simulator provides several demo options through an easy-to-use script:

1. Using the batch file (Windows):
   ```
   run_demo.bat
   ```

2. Using the shell script (Linux/Mac):
   ```
   ./run_demo.sh
   ```

3. Directly from command line:
   ```bash
   # Run the comprehensive network demo (all layers)
   python run_network_tests.py comprehensive
   
   # Run the router operation demo (focuses on network layer)
   python run_network_tests.py router
   
   # Run the switch operation demo (focuses on data link layer)
   python run_network_tests.py switch
   ```

### Available Demonstrations

1. **Comprehensive Network Test**
   - Demonstrates the complete protocol stack
   - Shows data flow through all 5 layers
   - Includes inter-network routing
   - Demonstrates DNS and ARP protocols
   - Shows switch and hub operation

2. **Router Operation Test**
   - Focuses on network layer operations
   - Demonstrates routing table lookups
   - Shows packet forwarding between networks
   - Demonstrates TTL processing

3. **Switch Operation Test**
   - Focuses on data link layer operations
   - Demonstrates MAC address learning
   - Shows frame forwarding based on MAC addresses
   - Demonstrates broadcast and unicast handling
   ```

2. Follow the prompts to:
   - Create a network topology
   - Select sender and receiver devices
   - Test data transfer between devices
   - Test application layer services (email and search)

3. Alternatively, run the comprehensive network demo:
   ```
   python main.py --demo
   ```
   
   This will automatically run a pre-configured demonstration that shows:
   - A complex network topology with multiple networks
   - Routers with routing tables
   - Switches with MAC address tables
   - Hub broadcasting
   - ARP protocol for MAC address resolution
   - IP routing between networks
   - DNS for domain name resolution
   - CRC for error detection in Data Link layer
   
4. For Windows users, you can simply double-click on `run_demo.bat` in the main directory.
   For Linux/Mac users, you can run `./run_demo.sh` from the terminal.

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
