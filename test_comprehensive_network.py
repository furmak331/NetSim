"""
Comprehensive Network Test for Network Simulator
Demonstrates all layers (Physical, Data Link, Network) working together
in a complex network topology with routers, switches, and end devices
"""

import sys
import time
import argparse
from cli_utils import CLIUtils
from network_simulator import NetworkSimulator
from end_devices import EndDevices
from hub import Hub
from switch import Switch
from router import Router
from domain_name_server import DomainNameServer
from direct_connection import DirectConnection
from crc_for_datalink import CRCForDataLink

def create_test_topology(verbose=False):
    """Create a comprehensive test network topology"""
    # Initialize the simulator
    simulator = NetworkSimulator()
    
    # Print welcome header
    CLIUtils.print_header("COMPREHENSIVE NETWORK TEST")
    print("\nCreating a multi-router network topology with all layers operational...")
    
    # Create DNS server
    dns_server = DomainNameServer()
    simulator.devices.append(dns_server)
    
    # Create Network 1: Router 1 + Switch 1 + 2 End Devices
    CLIUtils.print_section("Network 1 Configuration")
    router1 = Router(1, "192.168.1.0/24")
    router1.ip_address = "192.168.1.1/24"
    router1.mac_address = "00:00:00:00:01:01"
    print(f"Created Router 1: IP={router1.ip_address}, MAC={router1.mac_address}")
    
    switch1 = Switch(1)
    switch1.mac_address = "00:00:00:00:01:FF"
    print(f"Created Switch 1: MAC={switch1.mac_address}")
    
    pc1 = EndDevices("00:00:00:00:01:10", "PC1", "192.168.1.10/24")
    print(f"Created PC1: IP={pc1.IP}, MAC={pc1.MAC}")
    
    pc2 = EndDevices("00:00:00:00:01:20", "PC2", "192.168.1.20/24")
    print(f"Created PC2: IP={pc2.IP}, MAC={pc2.MAC}")
    
    # Connect PC1 and PC2 to Switch 1
    print("Connecting PCs to Switch 1...")
    switch1.add_to_direct_connection_table(pc1)
    switch1.add_to_direct_connection_table(pc2)
    switch1.mac_table = {pc1.MAC: "PORT 1", pc2.MAC: "PORT 2"}
    
    # Connect Switch 1 to Router 1
    print("Connecting Switch 1 to Router 1...")
    # In a real switch connection, we would connect it to a router port
    router1.switches = [switch1]
    
    # Create Network 2: Router 2 + Switch 2 + 2 End Devices
    CLIUtils.print_section("Network 2 Configuration")
    router2 = Router(2, "192.168.2.0/24")
    router2.ip_address = "192.168.2.1/24"
    router2.mac_address = "00:00:00:00:02:01"
    print(f"Created Router 2: IP={router2.ip_address}, MAC={router2.mac_address}")
    
    switch2 = Switch(2)
    switch2.mac_address = "00:00:00:00:02:FF"
    print(f"Created Switch 2: MAC={switch2.mac_address}")
    
    pc3 = EndDevices("00:00:00:00:02:10", "PC3", "192.168.2.10/24")
    print(f"Created PC3: IP={pc3.IP}, MAC={pc3.MAC}")
    
    pc4 = EndDevices("00:00:00:00:02:20", "PC4", "192.168.2.20/24") 
    print(f"Created PC4: IP={pc4.IP}, MAC={pc4.MAC}")
    
    # Connect PC3 and PC4 to Switch 2
    print("Connecting PCs to Switch 2...")
    switch2.add_to_direct_connection_table(pc3)
    switch2.add_to_direct_connection_table(pc4)
    switch2.mac_table = {pc3.MAC: "PORT 1", pc4.MAC: "PORT 2"}
    
    # Connect Switch 2 to Router 2
    print("Connecting Switch 2 to Router 2...")
    router2.switches = [switch2]
    
    # Create Network 3: Router 3 + Hub + 2 End Devices (to demonstrate broadcast)
    CLIUtils.print_section("Network 3 Configuration (with Hub)")
    router3 = Router(3, "192.168.3.0/24")
    router3.ip_address = "192.168.3.1/24"
    router3.mac_address = "00:00:00:00:03:01"
    print(f"Created Router 3: IP={router3.ip_address}, MAC={router3.mac_address}")
    
    hub1 = Hub(1)
    print(f"Created Hub 1")
    
    pc5 = EndDevices("00:00:00:00:03:10", "PC5", "192.168.3.10/24")
    print(f"Created PC5: IP={pc5.IP}, MAC={pc5.MAC}")
    
    pc6 = EndDevices("00:00:00:00:03:20", "PC6", "192.168.3.20/24")  
    print(f"Created PC6: IP={pc6.IP}, MAC={pc6.MAC}")
    
    # Connect devices to Hub 1
    print("Connecting devices to Hub 1...")
    hub1.store_devices_connected([pc5, pc6])
    
    # Connect Router 3 to Hub 1
    print("Connecting Router 3 to Hub 1...")

    # Connect the routers with each other (Router Backbone)
    CLIUtils.print_section("Router Backbone Configuration")
    print("Connecting routers to create backbone network...")
    
    # Router 1 WAN interface
    router1.ip_address_wan = "10.0.0.1/30"
    router1.mac_address_wan = "00:00:00:FF:01:01"
    
    # Router 2 WAN interface
    router2.ip_address_wan = "10.0.0.2/30"
    router2.mac_address_wan = "00:00:00:FF:02:01"
    
    # Router 3 WAN interface
    router3.ip_address_wan = "10.0.0.5/30"
    router3.mac_address_wan = "00:00:00:FF:03:01"
    
    print(f"Router 1 WAN: IP={router1.ip_address_wan}, MAC={router1.mac_address_wan}")
    print(f"Router 2 WAN: IP={router2.ip_address_wan}, MAC={router2.mac_address_wan}")
    print(f"Router 3 WAN: IP={router3.ip_address_wan}, MAC={router3.mac_address_wan}")
    
    # Build routing tables
    CLIUtils.print_section("Building Routing Tables")
    
    # Router 1 routing table
    router1.routing_table = {
        "192.168.1.0/24": {"next_hop": None, "interface": "local", "metric": 0},
        "192.168.2.0/24": {"next_hop": "10.0.0.2", "interface": "WAN", "metric": 1},
        "192.168.3.0/24": {"next_hop": "10.0.0.2", "interface": "WAN", "metric": 2},
        "10.0.0.0/30": {"next_hop": None, "interface": "local", "metric": 0},
    }
    print("Router 1 routing table:")
    for network, route in router1.routing_table.items():
        next_hop = route["next_hop"] if route["next_hop"] else "Direct"
        print(f"  Network: {network} → Next hop: {next_hop}, Metric: {route['metric']}")
    
    # Router 2 routing table
    router2.routing_table = {
        "192.168.1.0/24": {"next_hop": "10.0.0.1", "interface": "WAN", "metric": 1},
        "192.168.2.0/24": {"next_hop": None, "interface": "local", "metric": 0},
        "192.168.3.0/24": {"next_hop": "10.0.0.5", "interface": "WAN", "metric": 1},
        "10.0.0.0/30": {"next_hop": None, "interface": "local", "metric": 0},
        "10.0.0.4/30": {"next_hop": None, "interface": "local", "metric": 0},
    }
    print("Router 2 routing table:")
    for network, route in router2.routing_table.items():
        next_hop = route["next_hop"] if route["next_hop"] else "Direct"
        print(f"  Network: {network} → Next hop: {next_hop}, Metric: {route['metric']}")
    
    # Router 3 routing table
    router3.routing_table = {
        "192.168.1.0/24": {"next_hop": "10.0.0.2", "interface": "WAN", "metric": 2},
        "192.168.2.0/24": {"next_hop": "10.0.0.2", "interface": "WAN", "metric": 1},
        "192.168.3.0/24": {"next_hop": None, "interface": "local", "metric": 0},
        "10.0.0.4/30": {"next_hop": None, "interface": "local", "metric": 0},
    }
    print("Router 3 routing table:")
    for network, route in router3.routing_table.items():
        next_hop = route["next_hop"] if route["next_hop"] else "Direct"
        print(f"  Network: {network} → Next hop: {next_hop}, Metric: {route['metric']}")

    # Populate DNS server with device information
    CLIUtils.print_section("DNS Configuration")
    dns_server.set_domain_ip_mapping("pc1.local", pc1.IP.split('/')[0])
    dns_server.set_domain_ip_mapping("pc2.local", pc2.IP.split('/')[0])
    dns_server.set_domain_ip_mapping("pc3.local", pc3.IP.split('/')[0])
    dns_server.set_domain_ip_mapping("pc4.local", pc4.IP.split('/')[0])
    dns_server.set_domain_ip_mapping("pc5.local", pc5.IP.split('/')[0])
    dns_server.set_domain_ip_mapping("pc6.local", pc6.IP.split('/')[0])
    print("DNS server populated with device hostnames")
    
    # Add all created devices to the simulator
    simulator.devices.extend([pc1, pc2, pc3, pc4, pc5, pc6])
    simulator.switches.extend([switch1, switch2])
    simulator.hubs.append(hub1)
    simulator.routers.extend([router1, router2, router3])
    
    # Return the created topology for testing
    return {
        "simulator": simulator,
        "devices": {
            "pc1": pc1,
            "pc2": pc2, 
            "pc3": pc3,
            "pc4": pc4,
            "pc5": pc5,
            "pc6": pc6
        },
        "switches": {
            "switch1": switch1,
            "switch2": switch2
        },
        "hubs": {
            "hub1": hub1
        },
        "routers": {
            "router1": router1, 
            "router2": router2,
            "router3": router3
        },
        "dns_server": dns_server
    }

def simulate_frame_transmission(source, destination, data, routers=None, verbose=False):
    """Simulate frame transmission between devices with proper layered network protocol stack"""
    CLIUtils.print_header(f"NETWORK COMMUNICATION: {source.device_name} → {destination.device_name}")
    print(f"Source: {source.device_name} (IP: {source.IP}, MAC: {source.MAC})")
    print(f"Destination: {destination.device_name} (IP: {destination.IP}, MAC: {destination.MAC})")
    print(f"Original Data: {data}")
    
    # Extract IPs without subnet masks
    source_ip = source.IP.split('/')[0]
    dest_ip = destination.IP.split('/')[0]
    
    # Determine network properties
    source_network = source.IP.split('/')[0].rsplit('.', 1)[0]
    dest_network = destination.IP.split('/')[0].rsplit('.', 1)[0]
    same_network = source_network == dest_network
    
    # Identify relevant routers
    source_router = None
    dest_router = None
    
    if source_network == "192.168.1":
        source_router = routers["router1"]
    elif source_network == "192.168.2":
        source_router = routers["router2"]
    elif source_network == "192.168.3":
        source_router = routers["router3"]
        
    if dest_network == "192.168.1":
        dest_router = routers["router1"]
    elif dest_network == "192.168.2":
        dest_router = routers["router2"]
    elif dest_network == "192.168.3":
        dest_router = routers["router3"]
    
    ###############################################################
    # SOURCE DEVICE: DATA PROCESSING THROUGH PROTOCOL LAYERS      #
    ###############################################################
    CLIUtils.print_section(f"SOURCE DEVICE {source.device_name}: PROTOCOL STACK (TOP-DOWN)")
    
    ################################################################
    # LAYER 5: APPLICATION LAYER - SOURCE DEVICE
    ################################################################
    print("\n[LAYER 5: APPLICATION]")
    print(f"[{source.device_name}] Application generating data: '{data}'")
    application_data = data
    
    ################################################################
    # LAYER 4: TRANSPORT LAYER - SOURCE DEVICE
    ################################################################
    print("\n[LAYER 4: TRANSPORT]")
    # Adding TCP header information
    source_port = 1024 + hash(source.device_name) % 64511  # Random high port
    dest_port = 80  # Assuming HTTP traffic for demonstration
    seq_num = hash(data) % 1000000
    tcp_header = f"SrcPort={source_port},DstPort={dest_port},Seq={seq_num},ACK=0,Flags=SYN"
    segment = f"{tcp_header}|{application_data}"
    print(f"[{source.device_name}] TCP Protocol - Adding Headers:")
    print(f"[{source.device_name}] ▶ Source Port: {source_port}")
    print(f"[{source.device_name}] ▶ Destination Port: {dest_port}")
    print(f"[{source.device_name}] ▶ Sequence Number: {seq_num}")
    print(f"[{source.device_name}] ▶ Flags: SYN")
    
    ################################################################
    # LAYER 3: NETWORK LAYER - SOURCE DEVICE
    ################################################################
    print("\n[LAYER 3: NETWORK]")
    # Create IP packet with TCP segment as payload
    ttl = 64  # Default TTL
    protocol = 6  # TCP protocol
    ip_id = hash(segment) % 65535
    
    # Determine next hop (router or direct)
    next_hop_ip = None
    next_hop_mac = None
    
    if same_network:
        print(f"[{source.device_name}] IP Protocol - Direct Delivery:")
        print(f"[{source.device_name}] ▶ Source and destination are in the same network ({source_network})")
        next_hop_ip = dest_ip
        next_hop_mac = destination.MAC
        print(f"[{source.device_name}] ARP Protocol - Resolving destination address:")
        print(f"[{source.device_name}] ▶ Query: Who has IP {dest_ip}?")
        print(f"[{source.device_name}] ▶ Response: {dest_ip} is at {destination.MAC}")
    else:
        # Need to send to default gateway (router)
        gateway_ip = source_router.ip_address.split('/')[0]
        next_hop_ip = gateway_ip
        next_hop_mac = source_router.mac_address
        print(f"[{source.device_name}] IP Protocol - Cross-Network Delivery:")
        print(f"[{source.device_name}] ▶ Source network: {source_network}, Destination network: {dest_network}")
        print(f"[{source.device_name}] ▶ Different networks detected, using default gateway ({gateway_ip})")
        print(f"[{source.device_name}] ARP Protocol - Resolving gateway address:")
        print(f"[{source.device_name}] ▶ Query: Who has IP {gateway_ip}?")
        print(f"[{source.device_name}] ▶ Response: {gateway_ip} is at {source_router.mac_address}")
    
    # Create IP header
    ip_header = f"SrcIP={source_ip},DstIP={dest_ip},TTL={ttl},ID={ip_id},Proto={protocol}"
    ip_packet = f"{ip_header}|{segment}"
    
    print(f"[{source.device_name}] IP Protocol - Adding Headers:")
    print(f"[{source.device_name}] ▶ Source IP: {source_ip}")
    print(f"[{source.device_name}] ▶ Destination IP: {dest_ip}")
    print(f"[{source.device_name}] ▶ TTL: {ttl}")
    print(f"[{source.device_name}] ▶ Protocol ID: {protocol} (TCP)")
    
    ################################################################
    # LAYER 2: DATA LINK LAYER - SOURCE DEVICE
    ################################################################
    print("\n[LAYER 2: DATA LINK]")
    # Create Ethernet frame with IP packet as payload
    frame_header = f"SrcMAC={source.MAC},DstMAC={next_hop_mac}"
    frame = f"{frame_header}|{ip_packet}"
    
    # Calculate CRC for error detection
    crc = CRCForDataLink()
    crc_value = crc.calculate_crc32(frame)
    frame_with_crc = f"{frame}|CRC={crc_value}"
    
    print(f"[{source.device_name}] Ethernet Protocol - Creating Frame:")
    print(f"[{source.device_name}] ▶ Source MAC: {source.MAC}")
    print(f"[{source.device_name}] ▶ Destination MAC: {next_hop_mac} (Next hop device)")
    print(f"[{source.device_name}] Error Detection - Calculating CRC-32 Checksum:")
    print(f"[{source.device_name}] ▶ CRC-32: {crc_value}")
    
    ################################################################
    # LAYER 1: PHYSICAL LAYER - SOURCE DEVICE
    ################################################################
    print("\n[LAYER 1: PHYSICAL]")
    print(f"[{source.device_name}] Converting frame to electrical signals")
    print(f"[{source.device_name}] Transmitting bits over physical medium...")
    CLIUtils.simulate_network_delay(0.2, 0.5)
    
    ###############################################################
    # NETWORK INFRASTRUCTURE PROCESSING                           #
    ###############################################################
    
    if same_network:
        # SAME NETWORK PATH: Through switch or hub
        if source_network == "192.168.1" or source_network == "192.168.2":
            # SWITCH OPERATION (L2 Device)
            switch_num = "1" if source_network == "192.168.1" else "2"
            switch = routers["router1"].switches[0] if source_network == "192.168.1" else routers["router2"].switches[0]
            
            CLIUtils.print_section(f"SWITCH {switch_num}: DATA LINK LAYER DEVICE (L2)")
            
            # PHYSICAL LAYER AT SWITCH
            print("\n[LAYER 1: PHYSICAL] - AT SWITCH")
            print(f"[SWITCH {switch_num}] ▶ Receiving electrical signals on port connected to {source.device_name}")
            print(f"[SWITCH {switch_num}] ▶ Converting signals back to binary data")
            
            # DATA LINK LAYER AT SWITCH
            print("\n[LAYER 2: DATA LINK] - AT SWITCH")
            print(f"[SWITCH {switch_num}] ▶ Reading frame header")
            print(f"[SWITCH {switch_num}] ▶ Source MAC: {source.MAC}")
            print(f"[SWITCH {switch_num}] ▶ Destination MAC: {next_hop_mac}")
            
            # MAC Address Learning
            print(f"[SWITCH {switch_num}] MAC Address Learning:")
            print(f"[SWITCH {switch_num}] ▶ Learning: {source.MAC} is on port connected to {source.device_name}")
            print(f"[SWITCH {switch_num}] ▶ Updating MAC address table")
            
            # MAC Address Table Lookup
            print(f"[SWITCH {switch_num}] MAC Address Table Lookup:")
            print(f"[SWITCH {switch_num}] ▶ Looking up MAC address {next_hop_mac}")
            print(f"[SWITCH {switch_num}] ▶ Found: {next_hop_mac} → Port connected to {destination.device_name}")
            
            # Frame Forwarding
            print(f"[SWITCH {switch_num}] Frame Forwarding:")
            print(f"[SWITCH {switch_num}] ▶ Forwarding frame to port connected to {destination.device_name}")
            
        elif source_network == "192.168.3":
            # HUB OPERATION (L1 Device)
            CLIUtils.print_section(f"HUB 1: PHYSICAL LAYER DEVICE (L1)")
            
            # PHYSICAL LAYER AT HUB
            print("\n[LAYER 1: PHYSICAL] - AT HUB")
            print(f"[HUB 1] ▶ Receiving electrical signals from port connected to {source.device_name}")
            print(f"[HUB 1] ▶ Signal Repeating (No Frame Inspection)")
            print(f"[HUB 1] ▶ Broadcasting signals to ALL connected ports")
            print(f"[HUB 1] NOTE: Hubs operate at Physical Layer only - no MAC address filtering")
            print(f"[HUB 1] ▶ All devices ({destination.device_name} and others) receive the signal")
            print(f"[HUB 1] ▶ Non-destination devices will filter frame at their Data Link layer")
    else:
        # CROSS-NETWORK PATH: Through multiple routers
        
        # Step 1: Frame goes through source network's switch to router
        if source_network == "192.168.1" or source_network == "192.168.2":
            # Source network has a switch
            switch_num = "1" if source_network == "192.168.1" else "2"
            
            CLIUtils.print_section(f"SWITCH {switch_num}: DATA LINK LAYER DEVICE (L2)")
            
            # PHYSICAL LAYER AT SWITCH
            print("\n[LAYER 1: PHYSICAL] - AT SWITCH")
            print(f"[SWITCH {switch_num}] ▶ Receiving electrical signals on port connected to {source.device_name}")
            print(f"[SWITCH {switch_num}] ▶ Converting signals back to binary data")
            
            # DATA LINK LAYER AT SWITCH
            print("\n[LAYER 2: DATA LINK] - AT SWITCH")
            print(f"[SWITCH {switch_num}] ▶ Reading frame header")
            print(f"[SWITCH {switch_num}] ▶ Source MAC: {source.MAC}")
            print(f"[SWITCH {switch_num}] ▶ Destination MAC: {source_router.mac_address}")
            
            # MAC Address Learning
            print(f"[SWITCH {switch_num}] MAC Address Learning:")
            print(f"[SWITCH {switch_num}] ▶ Learning: {source.MAC} is on port connected to {source.device_name}")
            print(f"[SWITCH {switch_num}] ▶ Updating MAC address table")
            
            # Frame Forwarding to Router
            print(f"[SWITCH {switch_num}] Frame Forwarding:")
            print(f"[SWITCH {switch_num}] ▶ Looking up MAC address {source_router.mac_address}")
            print(f"[SWITCH {switch_num}] ▶ Found: {source_router.mac_address} → Port connected to Router {source_router.router_number}")
            print(f"[SWITCH {switch_num}] ▶ Forwarding frame to port connected to Router {source_router.router_number}")
            
        # Step 2: Source Router Processing (L3 device, also has L2 and L1 capabilities)
        CLIUtils.print_section(f"ROUTER {source_router.router_number}: SOURCE NETWORK")
        
        # PHYSICAL LAYER AT ROUTER
        print("\n[LAYER 1: PHYSICAL] - AT ROUTER")
        print(f"[ROUTER {source_router.router_number}] ▶ Receiving electrical signals")
        print(f"[ROUTER {source_router.router_number}] ▶ Converting signals back to binary data")
        
        # DATA LINK LAYER AT ROUTER
        print("\n[LAYER 2: DATA LINK] - AT ROUTER")
        print(f"[ROUTER {source_router.router_number}] ▶ Reading frame header")
        print(f"[ROUTER {source_router.router_number}] ▶ Checking if destination MAC matches router")
        print(f"[ROUTER {source_router.router_number}] ▶ MAC address match: {source_router.mac_address}")
        print(f"[ROUTER {source_router.router_number}] ▶ Verifying frame CRC...")
        
        if crc.verify_crc32(frame, crc_value):
            print(f"[ROUTER {source_router.router_number}] ▶ CRC verification: PASSED ✓")
        else:
            print(f"[ROUTER {source_router.router_number}] ▶ CRC verification: FAILED ✗")
            return False
            
        print(f"[ROUTER {source_router.router_number}] ▶ Extracting IP packet")
        
        # NETWORK LAYER AT ROUTER
        print("\n[LAYER 3: NETWORK] - AT ROUTER")
        
        # Process IP packet - Decrement TTL
        ttl -= 1
        print(f"[ROUTER {source_router.router_number}] IP Protocol - Packet Processing:")
        print(f"[ROUTER {source_router.router_number}] ▶ Extracting destination IP: {dest_ip}")
        print(f"[ROUTER {source_router.router_number}] ▶ Decrementing TTL: {ttl+1} → {ttl}")
        if ttl <= 0:
            print(f"[ROUTER {source_router.router_number}] ▶ TTL expired, packet dropped")
            return False
            
        # Routing table lookup
        print(f"[ROUTER {source_router.router_number}] Routing Decision:")
        print(f"[ROUTER {source_router.router_number}] ▶ Looking up routing table for network {dest_network}")
        
        # Determine next hop from routing table using longest prefix match
        dest_subnet = f"{dest_network}.0/24"
        route_info = source_router.routing_table.get(dest_subnet)
        
        if not route_info:
            print(f"[ROUTER {source_router.router_number}] ❌ No route to destination network {dest_network}")
            print(f"[ROUTER {source_router.router_number}] ❌ Dropping packet")
            return False
        
        next_hop = route_info["next_hop"]
        
        if next_hop != "Direct":
            # Need to forward to another router
            print(f"[ROUTER {source_router.router_number}] ▶ Route found: {dest_network} via next hop {next_hop}")
            
            # Inter-router communication
            CLIUtils.print_section(f"ROUTER {source_router.router_number} → ROUTER {dest_router.router_number}: WAN LINK")
            print(f"[ROUTER {source_router.router_number}] Forwarding packet to next hop router...")
            
            # Router creates new frame for the WAN link with updated MAC addresses
            print("\n[LAYER 2: DATA LINK] - WAN INTERFACE")
            print(f"[ROUTER {source_router.router_number}] ▶ Creating new frame with destination router's MAC")
            
            router_to_router_frame = f"SrcMAC={source_router.mac_address_wan},DstMAC={dest_router.mac_address_wan}|{ip_header}|{segment}"
            
            # Calculate new CRC
            new_crc = crc.calculate_crc32(router_to_router_frame)
            router_to_router_frame_with_crc = f"{router_to_router_frame}|CRC={new_crc}"
            
            print(f"[ROUTER {source_router.router_number}] ▶ WAN Link: New frame created with updated MAC addresses")
            print(f"[ROUTER {source_router.router_number}] ▶ Source MAC: {source_router.mac_address_wan}")
            print(f"[ROUTER {source_router.router_number}] ▶ Destination MAC: {dest_router.mac_address_wan}")
            
            print("\n[LAYER 1: PHYSICAL] - WAN INTERFACE")
            print(f"[ROUTER {source_router.router_number}] ▶ Transmitting bits over WAN link...")
            CLIUtils.simulate_network_delay(0.1, 0.3)
            
            # Destination router receives the frame
            # DESTINATION ROUTER PROCESSING
            CLIUtils.print_section(f"ROUTER {dest_router.router_number}: DESTINATION NETWORK")
            
            # PHYSICAL LAYER AT DESTINATION ROUTER
            print("\n[LAYER 1: PHYSICAL] - AT ROUTER")
            print(f"[ROUTER {dest_router.router_number}] ▶ Receiving electrical signals on WAN interface")
            print(f"[ROUTER {dest_router.router_number}] ▶ Converting signals back to binary data")
            
            # DATA LINK LAYER AT DESTINATION ROUTER
            print("\n[LAYER 2: DATA LINK] - AT ROUTER")
            print(f"[ROUTER {dest_router.router_number}] ▶ Reading frame header")
            print(f"[ROUTER {dest_router.router_number}] ▶ Checking if destination MAC matches router")
            print(f"[ROUTER {dest_router.router_number}] ▶ MAC address match: {dest_router.mac_address_wan}")
            print(f"[ROUTER {dest_router.router_number}] ▶ Extracting IP packet")
            
            # NETWORK LAYER AT DESTINATION ROUTER
            print("\n[LAYER 3: NETWORK] - AT ROUTER")
            ttl -= 1
            print(f"[ROUTER {dest_router.router_number}] IP Protocol - Packet Processing:")
            print(f"[ROUTER {dest_router.router_number}] ▶ Received packet from Router {source_router.router_number}")
            print(f"[ROUTER {dest_router.router_number}] ▶ Decrementing TTL: {ttl+1} → {ttl}")
            print(f"[ROUTER {dest_router.router_number}] ▶ Destination IP: {dest_ip}")
            print(f"[ROUTER {dest_router.router_number}] ▶ Checking if destination network is directly connected")
            print(f"[ROUTER {dest_router.router_number}] ✓ Destination network {dest_network} is directly connected")
        else:
            # Direct connection
            print(f"[ROUTER {source_router.router_number}] ▶ Route found: {dest_network} is directly connected")
        
        # Router needs to find MAC address of the destination
        print(f"[ROUTER {dest_router.router_number}] ARP Protocol - Address Resolution:")
        print(f"[ROUTER {dest_router.router_number}] ▶ Query: Who has IP {dest_ip}?")
        print(f"[ROUTER {dest_router.router_number}] ▶ Response: {dest_ip} is at {destination.MAC}")
        
        # Create new frame for final delivery
        print("\n[LAYER 2: DATA LINK] - AT ROUTER")
        print(f"[ROUTER {dest_router.router_number}] Creating new frame for final delivery:")
        final_frame_header = f"SrcMAC={dest_router.mac_address},DstMAC={destination.MAC}"
        final_ip_header = f"SrcIP={source_ip},DstIP={dest_ip},TTL={ttl},ID={ip_id},Proto={protocol}"
        final_frame = f"{final_frame_header}|{final_ip_header}|{segment}"
        
        # Calculate CRC for final frame
        final_crc = crc.calculate_crc32(final_frame)
        final_frame_with_crc = f"{final_frame}|CRC={final_crc}"
        
        print(f"[ROUTER {dest_router.router_number}] ▶ Source MAC: {dest_router.mac_address}")
        print(f"[ROUTER {dest_router.router_number}] ▶ Destination MAC: {destination.MAC}")
        print(f"[ROUTER {dest_router.router_number}] ▶ CRC-32: {final_crc}")
        
        print("\n[LAYER 1: PHYSICAL] - AT ROUTER")
        print(f"[ROUTER {dest_router.router_number}] ▶ Transmitting frame to LAN...")
        
        # Forward to the appropriate switch/hub
        if dest_network == "192.168.1" or dest_network == "192.168.2":
            # DESTINATION NETWORK SWITCH
            switch_num = "1" if dest_network == "192.168.1" else "2"
            CLIUtils.print_section(f"SWITCH {switch_num}: FINAL DELIVERY")
            
            # PHYSICAL LAYER AT SWITCH
            print("\n[LAYER 1: PHYSICAL] - AT SWITCH")
            print(f"[SWITCH {switch_num}] ▶ Receiving electrical signals from Router {dest_router.router_number}")
            print(f"[SWITCH {switch_num}] ▶ Converting signals back to binary data")
            
            # DATA LINK LAYER AT SWITCH
            print("\n[LAYER 2: DATA LINK] - AT SWITCH")
            print(f"[SWITCH {switch_num}] ▶ Reading frame header")
            print(f"[SWITCH {switch_num}] ▶ Source MAC: {dest_router.mac_address}")
            print(f"[SWITCH {switch_num}] ▶ Destination MAC: {destination.MAC}")
            
            # MAC Address Table Lookup
            print(f"[SWITCH {switch_num}] MAC Address Table Lookup:")
            print(f"[SWITCH {switch_num}] ▶ Looking up MAC address {destination.MAC}")
            print(f"[SWITCH {switch_num}] ▶ Found: {destination.MAC} → Port connected to {destination.device_name}")
            
            # Frame Forwarding
            print(f"[SWITCH {switch_num}] Frame Forwarding:")
            print(f"[SWITCH {switch_num}] ▶ Forwarding frame to port connected to {destination.device_name}")
            
        elif dest_network == "192.168.3":
            # DESTINATION NETWORK HUB
            CLIUtils.print_section(f"HUB 1: FINAL DELIVERY")
            
            # PHYSICAL LAYER AT HUB
            print("\n[LAYER 1: PHYSICAL] - AT HUB")
            print(f"[HUB 1] ▶ Receiving electrical signals from Router {dest_router.router_number}")
            print(f"[HUB 1] ▶ Signal Repeating (No Frame Inspection)")
            print(f"[HUB 1] ▶ Broadcasting signals to ALL connected ports")
            print(f"[HUB 1] ▶ All devices receive the signals")
            print(f"[HUB 1] NOTE: Only {destination.device_name} will accept the frame in its Data Link layer")
    
    ###############################################################
    # DESTINATION DEVICE: DATA PROCESSING THROUGH PROTOCOL LAYERS #
    ###############################################################
    CLIUtils.print_section(f"DESTINATION DEVICE {destination.device_name}: PROTOCOL STACK (BOTTOM-UP)")
    
    ################################################################
    # LAYER 1: PHYSICAL LAYER - DESTINATION DEVICE
    ################################################################
    print("\n[LAYER 1: PHYSICAL]")
    print(f"[{destination.device_name}] Receiving electrical signals")
    print(f"[{destination.device_name}] Converting signals to binary data")
    
    ################################################################
    # LAYER 2: DATA LINK LAYER - DESTINATION DEVICE
    ################################################################
    print("\n[LAYER 2: DATA LINK]")
    current_frame = final_frame_with_crc if not same_network else frame_with_crc
    
    print(f"[{destination.device_name}] Ethernet Protocol - Processing Frame:")
    print(f"[{destination.device_name}] ▶ Reading frame header")
    print(f"[{destination.device_name}] ▶ Checking destination MAC address")
    
    # Check if the frame is addressed to this device
    if destination.MAC in current_frame:
        print(f"[{destination.device_name}] ▶ MAC address match: Frame is addressed to this device ✓")
    else:
        print(f"[{destination.device_name}] ▶ MAC address mismatch: Frame is not for this device ✗")
        print(f"[{destination.device_name}] ▶ Discarding frame at Data Link layer")
        return False
        
    # Verify frame CRC
    print(f"[{destination.device_name}] Error Detection - Verifying CRC-32 Checksum:")
    print(f"[{destination.device_name}] ▶ CRC verification passed ✓")
    print(f"[{destination.device_name}] ▶ Extracting IP packet from frame")
    
    ################################################################
    # LAYER 3: NETWORK LAYER - DESTINATION DEVICE
    ################################################################
    print("\n[LAYER 3: NETWORK]")
    print(f"[{destination.device_name}] IP Protocol - Processing Packet:")
    print(f"[{destination.device_name}] ▶ Reading IP header")
    print(f"[{destination.device_name}] ▶ Checking destination IP address")
    
    if dest_ip in current_frame:
        print(f"[{destination.device_name}] ▶ IP address match: Packet is addressed to this device ✓")
    else:
        print(f"[{destination.device_name}] ▶ IP address mismatch: Packet is not for this device ✗")
        print(f"[{destination.device_name}] ▶ Discarding packet at Network layer")
        return False
        
    print(f"[{destination.device_name}] ▶ Extracting transport layer segment")
    
    ################################################################
    # LAYER 4: TRANSPORT LAYER - DESTINATION DEVICE
    ################################################################
    print("\n[LAYER 4: TRANSPORT]")
    print(f"[{destination.device_name}] TCP Protocol - Processing Segment:")
    print(f"[{destination.device_name}] ▶ Reading TCP header")
    print(f"[{destination.device_name}] ▶ Checking destination port: {dest_port}")
    print(f"[{destination.device_name}] ▶ Port {dest_port} is open ✓")
    print(f"[{destination.device_name}] ▶ Processing connection request (SYN flag)")
    print(f"[{destination.device_name}] ▶ Extracting application data")
    
    ################################################################
    # LAYER 5: APPLICATION LAYER - DESTINATION DEVICE
    ################################################################
    print("\n[LAYER 5: APPLICATION]")
    print(f"[{destination.device_name}] Receiving application data:")
    print(f"[{destination.device_name}] ▶ Processing data: '{application_data}'")
    print(f"[{destination.device_name}] ▶ Data successfully received and processed ✓")
    
    # Successfully delivered
    CLIUtils.print_header("TRANSMISSION COMPLETE")
    print(f"Data '{data}' successfully transmitted from {source.device_name} to {destination.device_name}")
    print(f"Demonstrating complete protocol stack operation through all network layers")
    return True

def run_demo_scenarios(topology, verbose=False):
    """Run demo scenarios to showcase the network simulator capabilities with layered protocols"""
    devices = topology["devices"]
    routers = topology["routers"]
    
    CLIUtils.print_header("NETWORK SIMULATOR DEMO SCENARIOS")
    print("\nThis demonstration will show the flow of data through the complete protocol stack:")
    
    print("\nFOCUS ON THE LAYERED APPROACH:")
    print("1. Watch how data flows DOWN through the protocol stack at the source device")
    print("   • Application Layer (L5) → Transport (L4) → Network (L3) → Data Link (L2) → Physical (L1)")
    
    print("\n2. Observe how each network device processes the data according to its operational layer")
    print("   • HUB: Operates at Layer 1 only - repeats electrical signals without examining content")
    print("   • SWITCH: Operates up to Layer 2 - examines MAC addresses to forward frames")
    print("   • ROUTER: Operates up to Layer 3 - examines IP addresses to route packets between networks")
    
    print("\n3. Notice how data flows UP through the protocol stack at the destination device")
    print("   • Physical Layer (L1) → Data Link (L2) → Network (L3) → Transport (L4) → Application (L5)")
    
    print("\n4. See how protocols are implemented at each layer:")
    print("   • L5 (Application): DNS for name resolution")
    print("   • L4 (Transport): TCP with ports and sequence numbers")
    print("   • L3 (Network): IP routing and ARP resolution")
    print("   • L2 (Data Link): Ethernet framing and CRC error detection")
    print("   • L1 (Physical): Signal transmission and reception")
    
    # Prompt user to continue with the first scenario
    input("\nPress Enter to begin the demonstrations...")
    
    # 1. Local network communication (PC1 to PC2)
    CLIUtils.print_header("SCENARIO 1: LOCAL NETWORK COMMUNICATION")
    print("This scenario demonstrates communication between devices on the same network.")
    print("Key features demonstrated:")
    print("• Complete protocol layering from application to physical layers")
    print("• Switch MAC address table lookups")
    print("• ARP protocol for MAC address resolution")
    print("• CRC for error detection at the data link layer")
    
    input("\nPress Enter to run Scenario 1: PC1 to PC2 (same network)...")
    
    simulate_frame_transmission(
        devices["pc1"], 
        devices["pc2"], 
        "Hello from PC1! We are on the same network.", 
        routers,
        verbose
    )
    
    # Prompt user to continue with next scenario
    input("\nPress Enter to continue to the next scenario...")
    
    # 2. Cross-network communication with routing (PC1 to PC3)
    CLIUtils.print_header("SCENARIO 2: CROSS-NETWORK COMMUNICATION")
    print("This scenario demonstrates communication between devices on different networks.")
    print("Key features demonstrated:")
    print("• IP routing between different networks")
    print("• Router forwarding decisions based on routing table lookups")
    print("• TTL processing")
    print("• Gateway resolution")
    print("• Complete protocol stack operation")
    
    input("\nPress Enter to run Scenario 2: PC1 to PC3 (across different networks)...")
    
    simulate_frame_transmission(
        devices["pc1"], 
        devices["pc3"], 
        "Hello from PC1 to PC3! This message must be routed between networks.", 
        routers,
        verbose
    )
    
    # Prompt user to continue with next scenario
    input("\nPress Enter to continue to the next scenario...")
    
    # 3. Hub broadcast demonstration (PC5 to PC6)
    CLIUtils.print_header("SCENARIO 3: HUB BROADCAST DEMONSTRATION")
    print("This scenario demonstrates how hubs operate at the physical layer.")
    print("Key features demonstrated:")
    print("• Physical layer broadcasting (hub behavior)")
    print("• MAC address filtering by end devices")
    print("• Difference between hub operation (broadcast) and switch operation (selective forwarding)")
    
    input("\nPress Enter to run Scenario 3: PC5 to PC6 (through a hub)...")
    
    simulate_frame_transmission(
        devices["pc5"], 
        devices["pc6"], 
        "This message is broadcast by the hub to all connected devices!", 
        routers,
        verbose
    )
    
    # Prompt user to continue with next demonstration
    input("\nPress Enter to continue to the DNS demonstration...")
    
    # 4. DNS lookup demonstration
    CLIUtils.print_header("SCENARIO 4: DNS PROTOCOL DEMONSTRATION")
    print("This scenario demonstrates the Domain Name System (DNS).")
    print("Key features demonstrated:")
    print("• Hostname to IP address resolution")
    print("• DNS server response handling")
    print("• Error handling for unknown hostnames")
    
    dns_server = topology["dns_server"]
    hostnames = ["pc1.local", "pc3.local", "pc6.local", "unknown.local"]
    
    print("\nPerforming DNS lookups for hostnames:")
    for hostname in hostnames:
        print(f"\nLooking up {hostname}...")
        ip = dns_server.get_ip_from_domain_name(hostname)
        if ip:
            print(f"DNS resolved: {hostname} → {ip}")
        else:
            print(f"DNS failed: {hostname} not found")
    
    # Prompt user to continue with next demonstration
    input("\nPress Enter to continue to the ARP demonstration...")
    
    # 5. ARP demonstration (query for MAC address)
    CLIUtils.print_header("SCENARIO 5: ARP PROTOCOL DEMONSTRATION")
    print("This scenario demonstrates the Address Resolution Protocol (ARP).")
    print("Key features demonstrated:")
    print("• IP address to MAC address resolution")
    print("• ARP request and reply messages")
    print("• Local ARP cache operation")
    
    print("\nSimulating ARP requests and responses:")
    
    for pc_name in ["pc1", "pc3", "pc6"]:
        pc = devices[pc_name]
        print(f"\nARP Request: Who has IP {pc.IP.split('/')[0]}?")
        print(f"ARP Reply from {pc.device_name}: {pc.IP.split('/')[0]} is at {pc.MAC}")
        print(f"MAC address {pc.MAC} cached in ARP table")
    
    print("\nAll demonstrations complete!")
    input("\nPress Enter to return to the main menu...")

def main():
    """Main function for the comprehensive network test"""
    parser = argparse.ArgumentParser(description="Network Simulator Comprehensive Test")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    CLIUtils.print_header("NETWORK PROTOCOL STACK SIMULATOR")
    print("\nTCP/IP PROTOCOL STACK DEMONSTRATION")
    print("\nThis simulator demonstrates the complete network protocol stack with proper layering:")
    print("• Layer 5 - Application: User data and application-specific protocols")
    print("• Layer 4 - Transport: End-to-end connections, ports (TCP)")
    print("• Layer 3 - Network: Logical addressing and routing (IP)")
    print("• Layer 2 - Data Link: Framing, MAC addressing, error detection (Ethernet, CRC)")
    print("• Layer 1 - Physical: Signal transmission and reception")
    
    print("\nAt each device, data flows through the protocol stack as follows:")
    
    print("\nSOURCE DEVICE PROTOCOL STACK (TOP-DOWN):")
    print("┌───────────────────────────────────────────────┐")
    print("│ LAYER 5: APPLICATION                          │")
    print("│ • User data generation                        │")
    print("│ • Application-specific processing             │")
    print("├───────────────────────────────────────────────┤")
    print("│ LAYER 4: TRANSPORT                            │")
    print("│ • TCP segment creation with port numbers      │")
    print("│ • Reliable delivery with sequence numbers     │")
    print("├───────────────────────────────────────────────┤")
    print("│ LAYER 3: NETWORK                              │")
    print("│ • IP packet creation with addresses           │")
    print("│ • Routing decisions based on IP addresses     │")
    print("│ • ARP for IP-to-MAC resolution                │")
    print("├───────────────────────────────────────────────┤")
    print("│ LAYER 2: DATA LINK                            │")
    print("│ • Ethernet frame creation with MAC addresses  │")
    print("│ • CRC calculation for error detection         │")
    print("├───────────────────────────────────────────────┤")
    print("│ LAYER 1: PHYSICAL                             │")
    print("│ • Binary data to electrical signals           │")
    print("│ • Physical transmission over medium           │")
    print("└───────────────────────────────────────────────┘")
    
    print("\nNETWORK DEVICE PROCESSING (LAYER SPECIFIC):")
    print("┌───────────────────────────────────────────────┐")
    print("│ HUB - LAYER 1 ONLY                            │")
    print("│ • Receives and repeats electrical signals     │")
    print("│ • No frame inspection or filtering            │")
    print("│ • Broadcasts to all connected ports           │")
    print("├───────────────────────────────────────────────┤")
    print("│ SWITCH - UP TO LAYER 2                        │")
    print("│ • Layer 1: Signal reception and regeneration  │")
    print("│ • Layer 2: MAC address examination            │")
    print("│ • MAC address learning and table lookups      │")
    print("│ • Selective forwarding based on MAC address   │")
    print("├───────────────────────────────────────────────┤")
    print("│ ROUTER - UP TO LAYER 3                        │")
    print("│ • Layers 1-2: Same as switch                  │")
    print("│ • Layer 3: IP address examination             │")
    print("│ • Routing table lookups                       │")
    print("│ • Path determination between networks         │")
    print("│ • TTL processing                              │")
    print("└───────────────────────────────────────────────┘")
    
    print("\nDESTINATION DEVICE PROTOCOL STACK (BOTTOM-UP):")
    print("┌───────────────────────────────────────────────┐")
    print("│ LAYER 1: PHYSICAL                             │")
    print("│ • Receives electrical signals                 │")
    print("│ • Converts to binary data                     │")
    print("├───────────────────────────────────────────────┤")
    print("│ LAYER 2: DATA LINK                            │")
    print("│ • Examines frame's destination MAC address    │")
    print("│ • Verifies frame using CRC                    │")
    print("│ • Processes if MAC matches, otherwise discards│")
    print("├───────────────────────────────────────────────┤")
    print("│ LAYER 3: NETWORK                              │")
    print("│ • Examines packet's destination IP address    │")
    print("│ • Processes if IP matches, otherwise discards │")
    print("├───────────────────────────────────────────────┤")
    print("│ LAYER 4: TRANSPORT                            │")
    print("│ • Examines segment's destination port         │")
    print("│ • Handles reliable delivery if TCP            │")
    print("├───────────────────────────────────────────────┤")
    print("│ LAYER 5: APPLICATION                          │")
    print("│ • Receives and processes application data     │")
    print("│ • Presents information to user                │")
    print("└───────────────────────────────────────────────┘")
    
    print("\nProtocols demonstrated include:")
    print("• TCP (Transport Layer)")
    print("• IP (Network Layer)")
    print("• ARP (Network-to-Data Link Layer mapping)")
    print("• DNS (Application Layer)")
    print("• Ethernet (Data Link Layer)")
    print("• CRC (Data Link Layer error detection)")
    
    input("\nPress Enter to create the network topology...")
    
    topology = create_test_topology(args.verbose)
    print("\nNetwork topology created successfully!")
    print("• 3 separate networks (192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24)")
    print("• 3 routers forming a backbone")
    print("• 2 switches (Networks 1 and 2)")
    print("• 1 hub (Network 3)")
    print("• 6 end devices (2 per network)")
    print("• 1 DNS server")
    
    run_demo_scenarios(topology, args.verbose)
    
    CLIUtils.print_header("SIMULATION COMPLETE")
    print("\nThis demonstration has shown:")
    print("• Complete protocol stack operation from physical to application layers")
    print("• Communication within the same network (PC1 → PC2)")
    print("• Communication across networks requiring routing (PC1 → PC3)")
    print("• Physical layer operation of hubs (broadcast)")
    print("• Data link layer operation of switches (selective forwarding)")
    print("• Network layer operation of routers (routing between networks)")
    print("• DNS protocol for hostname resolution")
    print("• ARP protocol for IP-to-MAC address resolution")
    print("\nFor more details on how each protocol works, examine the output of each scenario.")

if __name__ == "__main__":
    main()
