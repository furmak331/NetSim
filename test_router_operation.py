"""
Router testing functionality for network simulator
"""

def get_subnet_mask(prefix_length):
    """
    Convert prefix length to subnet mask
    
    Args:
        prefix_length: CIDR prefix length (0-32)
        
    Returns:
        str: Subnet mask in dotted decimal notation
    """
    # Convert prefix to binary string of 32 bits (1s followed by 0s)
    binary = ('1' * prefix_length).ljust(32, '0')
    
    # Split into octets and convert to decimal
    octets = [binary[i:i+8] for i in range(0, 32, 8)]
    decimal_octets = [int(octet, 2) for octet in octets]
    
    # Format as dotted decimal
    return '.'.join(str(octet) for octet in decimal_octets)

def test_router_packet_forwarding(sender_device, receiver_device, sender_router, receiver_router):
    """
    Test packet forwarding functionality of routers between networks
    
    Args:
        sender_device: The device sending data
        receiver_device: The device receiving data
        sender_router: The router in the sender's network
        receiver_router: The router in the receiver's network
    """
    # Router packet forwarding demonstration
    print("\n=== ROUTER PACKET FORWARDING DEMONSTRATION ===")
    print("\nThis demonstration shows how routers forward packets between different networks.")
    print("It includes routing table lookup, TTL processing, and network layer operations.")
    
    print("\n--- PHASE 1: EXAMINING ROUTING TABLES ---")
    print(f"Source device: {sender_device.get_device_name()} (IP: {sender_device.IP})")
    print(f"Destination device: {receiver_device.get_device_name()} (IP: {receiver_device.IP})")
    
    # Show routing tables
    sender_router.display_routing_table()
    
    if sender_router != receiver_router:
        receiver_router.display_routing_table()
    
    # Get data from user
    data = input("\nEnter data to send: ")
    
    # Set data in sender device
    sender_device.set_data(data)
    
    # Packet forwarding visualization
    print("\n--- PHASE 2: NETWORK LAYER PACKET FORWARDING ---")
    print(f"\n[DEVICE {sender_device.get_device_name()}] ▶ Creating IP packet")
    print(f"[DEVICE {sender_device.get_device_name()}] ▶ Source IP: {sender_device.IP}")
    print(f"[DEVICE {sender_device.get_device_name()}] ▶ Destination IP: {receiver_device.IP}")
    print(f"[DEVICE {sender_device.get_device_name()}] ▶ TTL: 64")
    print(f"[DEVICE {sender_device.get_device_name()}] ▶ Protocol: TCP")
    print(f"[DEVICE {sender_device.get_device_name()}] ▶ Data: \"{data}\"")
    
    # Packet reaches the sender's router
    print(f"\n[DEVICE {sender_device.get_device_name()}] ▶ Sending packet to default gateway (Router {sender_router.router_number})")
    print(f"[ROUTER {sender_router.router_number}] ▶ Received packet from {sender_device.IP}")
    
    # Router processes packet
    print(f"\n[ROUTER {sender_router.router_number}] === IP PACKET PROCESSING ===")
    print(f"[ROUTER {sender_router.router_number}] ▶ Checking destination IP: {receiver_device.IP}")
    
    # Determine if packet is for local network or needs routing
    source_network = sender_device.IP.split('.')[0] + ".0.0.0"
    dest_network = receiver_device.IP.split('.')[0] + ".0.0.0"
    
    if dest_network == sender_router.NID:
        print(f"[ROUTER {sender_router.router_number}] ✓ Destination is on the local network")
        print(f"[ROUTER {sender_router.router_number}] ▶ Delivering directly to {receiver_device.IP}")
        
        # Forward the packet to the receiver device
        receiver_device.set_data(sender_device.get_data())
        print(f"[DEVICE {receiver_device.get_device_name()}] ✓ Received packet from {sender_device.IP}")
        print(f"[DEVICE {receiver_device.get_device_name()}] ▶ Data: \"{receiver_device.get_data()}\"")
    else:
        # Route between networks through sender router
        print(f"[ROUTER {sender_router.router_number}] ▶ Destination is on a different network")
        print(f"[ROUTER {sender_router.router_number}] ▶ Consulting routing table...")
        
        # Perform routing table lookup
        success, next_hop = sender_router.route_packet(sender_device.IP, receiver_device.IP, data)
        
        if not success:
            print(f"[ROUTER {sender_router.router_number}] ❌ Routing failed, packet dropped")
            return
            
        if next_hop == receiver_router.router_number:
            # Direct connection between routers
            print(f"[ROUTER {sender_router.router_number}] ▶ Forwarding to Router {next_hop}")
            print(f"[ROUTER {next_hop}] ▶ Received packet from Router {sender_router.router_number}")
            
            # Receiver router processes packet
            print(f"\n[ROUTER {receiver_router.router_number}] === IP PACKET PROCESSING ===")
            print(f"[ROUTER {receiver_router.router_number}] ▶ Checking destination IP: {receiver_device.IP}")
            print(f"[ROUTER {receiver_router.router_number}] ✓ Destination is on the local network")
            print(f"[ROUTER {receiver_router.router_number}] ▶ Delivering to {receiver_device.IP}")
            
            # Forward the packet to the receiver device
            receiver_device.set_data(sender_device.get_data())
            print(f"[DEVICE {receiver_device.get_device_name()}] ✓ Received packet from {sender_device.IP}")
            print(f"[DEVICE {receiver_device.get_device_name()}] ▶ Data: \"{receiver_device.get_data()}\"")
        else:
            # Multi-hop routing (not implemented in this simple demo)
            print(f"[ROUTER {sender_router.router_number}] ▶ Multi-hop routing required")
            print(f"[ROUTER {sender_router.router_number}] ▶ Forwarding to intermediate Router {next_hop}")
            print("\nMulti-hop routing simulation not implemented in this demo.")
    
    print("\n=== ROUTER PACKET FORWARDING COMPLETED ===")

def test_router_subnetting(router):
    """
    Test router subnet operations
    
    Args:
        router: The router to test
    """
    print("\n=== ROUTER SUBNETTING DEMONSTRATION ===")
    print("This demonstration shows how routers handle subnets within a network")
    
    network_id = router.NID
    print(f"Router network ID: {network_id}")
    
    # Ask for subnet information
    print("\n--- SUBNET CONFIGURATION ---")
    prefix = int(input("Enter subnet prefix length (e.g., 24 for /24): "))
    num_subnets = 2 ** (32 - prefix)
    
    print(f"Network prefix /{prefix} allows for {num_subnets} subnets")
    
    # Display subnet information
    print("\n--- SUBNET INFORMATION ---")
    print(f"Network Address: {network_id}")
    print(f"Subnet Mask: {get_subnet_mask(prefix)}")
    print(f"Number of usable hosts per subnet: {2 ** (32 - prefix) - 2}")
