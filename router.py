"""
Router implementation for Network Simulator
Equivalent to Router.java in the Java implementation
"""
import random
import time
from switch import Switch

class Router(Switch):
    def __init__(self, number, NID):
        super().__init__(number)
        self.NID = NID
        self.data = None
        self.routing_table = {}  # Maps destination network to next hop router
        self.router_number = number
        self.switches = []
        
        # Router interface attributes
        self.ip_address = None
        self.mac_address = None
        self.ip_address_wan = None
        self.mac_address_wan = None
        
        # Router state variables
        self.queue = []  # Packet queue
        self.max_queue_size = 10  # Maximum packets in queue
        self.processing = False  # Whether router is currently processing a packet
        
        # Statistics
        self.packets_processed = 0
        self.packets_dropped = 0
        self.current_load = 0  # 0-100% load
        self.arp_requests = {}  # ARP requests (IP -> requesting device)
    
    def get_data_from_sender_switch(self, data):
        """
        Get data from sender switch
        
        Args:
            data (str): Data from sender switch
        """
        self.data = data
        print(f"[ROUTER {self.router_number}] ▶ Received data from sender switch")
    
    def send_data_to_receiver_switch(self):
        """
        Send data to receiver switch
        
        Returns:
            str: Data to be sent
        """
        print(f"[ROUTER {self.router_number}] ▶ Forwarding data to receiver switch")
        return self.data
    
    def store_connected_switches(self, switches):
        """
        Store connected switches
        
        Args:
            switches (list): List of connected switches
        """
        self.switches = switches
        print(f"[ROUTER {self.router_number}] ▶ Connected to {len(switches)} switches")
    
    def get_connected_switches(self):
        """
        Get connected switches
        
        Returns:
            list: List of connected switches
        """
        return self.switches
    
    def build_routing_table(self, all_routers):
        """
        Build routing table based on all routers in the network
        
        Args:
            all_routers (list): List of all routers in the network
        """
        print(f"[ROUTER {self.router_number}] === BUILDING ROUTING TABLE ===")
        for router in all_routers:
            if router.router_number != self.router_number:
                # For demonstration, we assume a simple routing where we know direct paths
                # In a real network, this would use a protocol like RIP, OSPF, etc.
                self.routing_table[router.NID] = {
                    "next_hop": router.router_number,
                    "metric": 1,  # Direct connection for simplicity
                    "interface": f"interface {router.router_number}"
                }
                print(f"[ROUTER {self.router_number}] ▶ Route to {router.NID}: via Router {router.router_number}")
    
    def route_packet(self, source_ip, dest_ip, data):
        """
        Route a packet from source IP to destination IP
        
        Args:
            source_ip (str): Source IP address
            dest_ip (str): Destination IP address
            data (str): Packet data
            
        Returns:
            tuple: (success, next_router_number)
        """
        print(f"[ROUTER {self.router_number}] === NETWORK LAYER: IP ROUTING ===")
        print(f"[ROUTER {self.router_number}] ▶ Routing packet from {source_ip} to {dest_ip}")
        
        # Extract destination network
        dest_network = dest_ip.split('.')[0] + ".0.0.0"  # Simple way to get network ID
        
        # Check if packet is for our network
        if dest_ip.startswith(self.NID.split('.')[0]):
            print(f"[ROUTER {self.router_number}] ✓ Destination {dest_ip} is in our network ({self.NID})")
            return True, self.router_number
        
        # Check routing table for path to destination
        if dest_network in self.routing_table:
            next_hop = self.routing_table[dest_network]["next_hop"]
            print(f"[ROUTER {self.router_number}] ▶ Found route to {dest_network} via Router {next_hop}")
            
            # Simulate router processing
            processing_delay = random.uniform(0.1, 0.3)  # 100-300 ms delay
            print(f"[ROUTER {self.router_number}] ▶ Processing packet (delay: {processing_delay:.3f}s)")
            time.sleep(processing_delay)
            
            # Calculate Time-To-Live (TTL)
            ttl = 64  # Starting TTL value
            ttl -= 1  # Decrement TTL
            
            # Check if TTL expired
            if ttl <= 0:
                print(f"[ROUTER {self.router_number}] ❌ TTL expired, packet dropped")
                self.packets_dropped += 1
                return False, None
            
            print(f"[ROUTER {self.router_number}] ✓ Forwarding to Router {next_hop}")
            self.packets_processed += 1
            return True, next_hop
        else:
            print(f"[ROUTER {self.router_number}] ❌ No route to {dest_network}, packet dropped")
            self.packets_dropped += 1
            return False, None
            
    def display_routing_table(self):
        """Display the current routing table"""
        print(f"\n[ROUTER {self.router_number}] === ROUTING TABLE ===")
        print(f"[ROUTER {self.router_number}] Network ID       | Next Hop        | Metric | Interface")
        print(f"[ROUTER {self.router_number}] ----------------- | --------------- | ------ | ---------------")
        
        # Display direct network
        print(f"[ROUTER {self.router_number}] {self.NID:<17} | Connected       | 0      | local")
        
        # Display routes to other networks
        for network, route in self.routing_table.items():
            print(f"[ROUTER {self.router_number}] {network:<17} | Router {route['next_hop']:<9} | {route['metric']:6d} | {route['interface']}")
            
    def simulate_congestion(self, congestion_level=0.5):
        """
        Simulate router congestion for educational demonstration
        
        Args:
            congestion_level (float): Level of congestion from 0.0-1.0
            
        Returns:
            bool: True if congestion is manageable, False if packet should be dropped
        """
        # Update current load
        self.current_load = int(congestion_level * 100)
        
        # Determine if packet needs to be dropped due to congestion
        if congestion_level > 0.8:  # 80% congestion threshold
            # High congestion - might drop packets
            drop_probability = (congestion_level - 0.8) * 2  # 0-40% drop chance
            if random.random() < drop_probability:
                print(f"[ROUTER {self.router_number}] ❌ High congestion ({self.current_load}%), packet dropped")
                self.packets_dropped += 1
                return False
                
        if congestion_level > 0.4:
            print(f"[ROUTER {self.router_number}] ⚠ Router congestion: {self.current_load}%, added latency")
            # Add latency proportional to congestion
            time.sleep(congestion_level * 0.2)
        
        return True
    
    def broadcast_arp(self, sender_device, target_ip):
        """
        Broadcast ARP request to all ports (excluding the one the request came from)
        This implements the proper ARP behavior for routers (Layer 3)
        
        Args:
            sender_device (EndDevices): The device sending the ARP request
            target_ip (str): The IP address being queried
            
        Returns:
            EndDevices or None: The device with matching IP if found, otherwise None
        """
        print(f"\n[ROUTER {self.router_number}] === ARP BROADCAST ===")
        print(f"[ROUTER {self.router_number}] ▶ ARP request from {sender_device.get_device_name()} (MAC: {sender_device.get_mac()})")
        print(f"[ROUTER {self.router_number}] ▶ Looking for device with IP: {target_ip}")
        self.arp_requests[target_ip] = sender_device
        
        # Learn the sender's MAC address
        if sender_device in self.connected_direct:
            port_num = self.connected_direct.index(sender_device) + 1
            self.mac_table[sender_device.get_mac()] = f"PORT {port_num}"
            print(f"[ROUTER {self.router_number}] ⓘ MAC Table Updated: {sender_device.get_mac()} → PORT {port_num}")
        
        # Check directly connected devices first
        sender_port = None
        if sender_device in self.connected_direct:
            sender_port = self.connected_direct.index(sender_device) + 1
        for i, device in enumerate(self.connected_direct):
            port_num = i + 1
            if port_num == sender_port:
                continue  # Skip the source port
            if device.IP == target_ip:
                print(f"[ROUTER {self.router_number}] ✓ Found matching device: {device.get_device_name()} on PORT {port_num}")
                self.mac_table[device.get_mac()] = f"PORT {port_num}"
                return device
            else:
                print(f"[ROUTER {self.router_number}] ▶ Sending ARP request to device on PORT {port_num}")
        
        # If not found in direct connections, try via connected hubs
        for i, hub in enumerate(self.hubs):
            port_num = len(self.connected_direct) + i + 1
            print(f"[ROUTER {self.router_number}] ▶ Forwarding ARP request to Hub {hub.get_hub_number()} on PORT {port_num}")
            devices = hub.get_connected_devices()
            for device in devices:
                if device.IP == target_ip:
                    print(f"[ROUTER {self.router_number}] ✓ Found matching device: {device.get_device_name()} via Hub {hub.get_hub_number()}")
                    self.connected_via_hub[device.get_mac()] = hub
                    return device
        
        print(f"[ROUTER {self.router_number}] ❌ No device with IP {target_ip} found")
        return None
    
    def get_ip(self):
        """
        Get router IP address
        
        Returns:
            str: Router IP address
        """
        return self.ip_address or f"{self.router_number}.0.0.1"
    
    def get_mac(self):
        """
        Get router MAC address
        
        Returns:
            str: Router MAC address
        """
        return self.mac_address or f"00:00:00:R{self.router_number}:00:01"
