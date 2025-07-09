"""
Network Topology Manager for TCP/IP Network Simulator
Manages network devices, connections, and routing in a realistic way
"""

import random
from enum import Enum

class DeviceType(Enum):
    END_DEVICE = "END_DEVICE"
    SWITCH = "SWITCH"
    ROUTER = "ROUTER"
    HUB = "HUB"

class NetworkInterface:
    """Represents a network interface on a device"""
    
    def __init__(self, interface_name, ip_address=None, mac_address=None):
        self.interface_name = interface_name
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.is_up = True
        self.connected_to = None  # Reference to connected device/port
        
    def connect_to(self, other_interface):
        """Connect this interface to another interface"""
        self.connected_to = other_interface
        other_interface.connected_to = self

class NetworkDevice:
    """Base class for all network devices"""
    
    def __init__(self, device_id, device_type, device_name=None):
        self.device_id = device_id
        self.device_type = device_type
        self.device_name = device_name or device_id
        self.interfaces = {}
        self.routing_table = {}
        self.is_active = True
        
    def add_interface(self, interface_name, ip_address=None, mac_address=None):
        """Add a network interface to this device"""
        interface = NetworkInterface(interface_name, ip_address, mac_address)
        self.interfaces[interface_name] = interface
        return interface
        
    def connect_to_device(self, other_device, local_interface, remote_interface):
        """Connect this device to another device"""
        if local_interface in self.interfaces and remote_interface in other_device.interfaces:
            self.interfaces[local_interface].connect_to(other_device.interfaces[remote_interface])
            return True
        return False
        
    def process_packet(self, packet, receiving_interface):
        """Process a packet received on an interface - to be overridden by subclasses"""
        pass

class EndDevice(NetworkDevice):
    """End device like PC, server, etc."""
    
    def __init__(self, device_id, device_name, ip_address, mac_address):
        super().__init__(device_id, DeviceType.END_DEVICE, device_name)
        self.ip_address = ip_address
        self.mac_address = mac_address
        
        # Add default interface
        self.add_interface("eth0", ip_address, mac_address)
        
        # Default gateway
        self.default_gateway = None
        
    def set_default_gateway(self, gateway_ip):
        """Set the default gateway for this device"""
        self.default_gateway = gateway_ip
        
    def process_packet(self, packet, receiving_interface):
        """Process packet at end device"""
        if packet.dest_ip == self.ip_address:
            print(f"[{self.device_name}] ✓ Packet received and accepted")
            return True
        else:
            print(f"[{self.device_name}] ▶ Packet not for this device, dropping")
            return False

class Switch(NetworkDevice):
    """Layer 2 switch with MAC address learning"""
    
    def __init__(self, device_id, device_name=None):
        super().__init__(device_id, DeviceType.SWITCH, device_name)
        self.mac_address_table = {}  # MAC -> interface mapping
        self.port_count = 24  # Default 24 ports
        
        # Add switch ports
        for i in range(1, self.port_count + 1):
            self.add_interface(f"port{i}")
            
    def learn_mac_address(self, mac_address, interface_name):
        """Learn MAC address on an interface"""
        if mac_address not in self.mac_address_table:
            self.mac_address_table[mac_address] = interface_name
            print(f"[{self.device_name}] ▶ Learned MAC {mac_address} on {interface_name}")
        
    def lookup_mac_address(self, mac_address):
        """Look up which interface a MAC address is on"""
        return self.mac_address_table.get(mac_address)
        
    def process_packet(self, packet, receiving_interface):
        """Process packet at switch (Layer 2)"""
        # Learn source MAC
        if packet.source_mac:
            self.learn_mac_address(packet.source_mac, receiving_interface)
            
        # Look up destination MAC
        if packet.dest_mac:
            out_interface = self.lookup_mac_address(packet.dest_mac)
            if out_interface and out_interface != receiving_interface:
                print(f"[{self.device_name}] ▶ Forwarding to {out_interface}")
                return self.forward_packet(packet, out_interface)
            else:
                print(f"[{self.device_name}] ▶ Flooding to all ports (unknown destination)")
                return self.flood_packet(packet, receiving_interface)
        
        return False
        
    def forward_packet(self, packet, out_interface):
        """Forward packet to specific interface"""
        if out_interface in self.interfaces:
            connected_interface = self.interfaces[out_interface].connected_to
            if connected_interface:
                print(f"[{self.device_name}] ▶ Packet forwarded via {out_interface}")
                return True
        return False
        
    def flood_packet(self, packet, receiving_interface):
        """Flood packet to all interfaces except receiving one"""
        forwarded = False
        for interface_name, interface in self.interfaces.items():
            if interface_name != receiving_interface and interface.connected_to:
                print(f"[{self.device_name}] ▶ Flooding to {interface_name}")
                forwarded = True
        return forwarded

class Router(NetworkDevice):
    """Layer 3 router with IP routing"""
    
    def __init__(self, device_id, device_name=None):
        super().__init__(device_id, DeviceType.ROUTER, device_name)
        self.connected_networks = set()
        self.interface_count = 4  # Default 4 interfaces
        
    def add_network_interface(self, interface_name, ip_address, network_address):
        """Add a network interface with IP address"""
        mac_address = self.generate_mac_address()
        interface = self.add_interface(interface_name, ip_address, mac_address)
        self.connected_networks.add(network_address)
        
        # Add directly connected route
        self.routing_table[network_address] = {
            "next_hop": "direct",
            "interface": interface_name,
            "metric": 0
        }
        
        print(f"[{self.device_name}] ▶ Added interface {interface_name} ({ip_address}) for network {network_address}")
        return interface
        
    def add_static_route(self, network, next_hop, interface, metric=1):
        """Add a static route to the routing table"""
        self.routing_table[network] = {
            "next_hop": next_hop,
            "interface": interface,
            "metric": metric
        }
        print(f"[{self.device_name}] ▶ Added route: {network} via {next_hop} (metric {metric})")
        
    def lookup_route(self, dest_ip):
        """Look up route for destination IP"""
        # Convert IP to network (assuming /24 networks)
        dest_network = ".".join(dest_ip.split(".")[:3]) + ".0/24"
        
        # Check for exact match
        if dest_network in self.routing_table:
            return self.routing_table[dest_network]
            
        # Check for default route
        if "0.0.0.0/0" in self.routing_table:
            return self.routing_table["0.0.0.0/0"]
            
        return None
        
    def process_packet(self, packet, receiving_interface):
        """Process packet at router (Layer 3)"""
        # Decrement TTL
        if hasattr(packet, 'ttl'):
            packet.ttl -= 1
            if packet.ttl <= 0:
                print(f"[{self.device_name}] ▶ TTL expired, dropping packet")
                return False
                
        # Look up route
        route = self.lookup_route(packet.dest_ip)
        if not route:
            print(f"[{self.device_name}] ▶ No route to {packet.dest_ip}, dropping packet")
            return False
            
        print(f"[{self.device_name}] ▶ Routing {packet.dest_ip} via {route['next_hop']} on {route['interface']}")
        
        # Forward packet
        return self.forward_packet(packet, route['interface'])
        
    def forward_packet(self, packet, out_interface):
        """Forward packet to specific interface"""
        if out_interface in self.interfaces:
            connected_interface = self.interfaces[out_interface].connected_to
            if connected_interface:
                print(f"[{self.device_name}] ▶ Packet forwarded via {out_interface}")
                return True
        return False
        
    def generate_mac_address(self):
        """Generate a random MAC address for router interface"""
        return f"00:1A:2B:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}:{random.randint(0, 255):02X}"

class Hub(NetworkDevice):
    """Layer 1 hub that repeats all signals"""
    
    def __init__(self, device_id, device_name=None):
        super().__init__(device_id, DeviceType.HUB, device_name)
        self.port_count = 8  # Default 8 ports
        
        # Add hub ports
        for i in range(1, self.port_count + 1):
            self.add_interface(f"port{i}")
            
    def process_packet(self, packet, receiving_interface):
        """Process packet at hub (Layer 1) - broadcast to all ports"""
        print(f"[{self.device_name}] ▶ Repeating signal to all ports")
        
        # Broadcast to all ports except receiving one
        for interface_name, interface in self.interfaces.items():
            if interface_name != receiving_interface and interface.connected_to:
                print(f"[{self.device_name}] ▶ Repeating to {interface_name}")
                
        return True

class NetworkTopologyManager:
    """Manages the complete network topology"""
    
    def __init__(self):
        self.devices = {}
        self.networks = {}
        self.connections = []
        
    def add_device(self, device):
        """Add a device to the topology"""
        self.devices[device.device_id] = device
        print(f"[TOPOLOGY] ▶ Added {device.device_type.value}: {device.device_name}")
        
    def create_network(self, network_id, network_address, description=""):
        """Create a network segment"""
        self.networks[network_id] = {
            "address": network_address,
            "description": description,
            "devices": []
        }
        print(f"[TOPOLOGY] ▶ Created network {network_id}: {network_address}")
        
    def connect_devices(self, device1_id, interface1, device2_id, interface2):
        """Connect two devices together"""
        if device1_id in self.devices and device2_id in self.devices:
            device1 = self.devices[device1_id]
            device2 = self.devices[device2_id]
            
            success = device1.connect_to_device(device2, interface1, interface2)
            if success:
                connection = {
                    "device1": device1_id,
                    "interface1": interface1,
                    "device2": device2_id,
                    "interface2": interface2
                }
                self.connections.append(connection)
                print(f"[TOPOLOGY] ▶ Connected {device1_id}:{interface1} <-> {device2_id}:{interface2}")
                return True
                
        return False
        
    def find_path(self, source_device_id, dest_device_id):
        """Find path between two devices using simple BFS"""
        if source_device_id == dest_device_id:
            return [source_device_id]
            
        visited = set()
        queue = [(source_device_id, [source_device_id])]
        
        while queue:
            current_device, path = queue.pop(0)
            
            if current_device in visited:
                continue
                
            visited.add(current_device)
            
            if current_device == dest_device_id:
                return path
                
            # Find connected devices
            for connection in self.connections:
                next_device = None
                if connection["device1"] == current_device:
                    next_device = connection["device2"]
                elif connection["device2"] == current_device:
                    next_device = connection["device1"]
                    
                if next_device and next_device not in visited:
                    queue.append((next_device, path + [next_device]))
                    
        return None  # No path found
        
    def get_device_by_ip(self, ip_address):
        """Find device by IP address"""
        for device in self.devices.values():
            if hasattr(device, 'ip_address') and device.ip_address == ip_address:
                return device
        return None
        
    def simulate_packet_flow(self, source_ip, dest_ip, packet_data):
        """Simulate packet flow through the network"""
        print(f"\n[TOPOLOGY] === PACKET FLOW SIMULATION ===")
        print(f"[TOPOLOGY] ▶ Source: {source_ip}")
        print(f"[TOPOLOGY] ▶ Destination: {dest_ip}")
        
        # Find source and destination devices
        source_device = self.get_device_by_ip(source_ip)
        dest_device = self.get_device_by_ip(dest_ip)
        
        if not source_device or not dest_device:
            print(f"[TOPOLOGY] ❌ Cannot find source or destination device")
            return False
            
        # Find path
        path = self.find_path(source_device.device_id, dest_device.device_id)
        if not path:
            print(f"[TOPOLOGY] ❌ No path found between devices")
            return False
            
        print(f"[TOPOLOGY] ▶ Path found: {' -> '.join(path)}")
        
        # Simulate packet processing at each device
        for i, device_id in enumerate(path):
            device = self.devices[device_id]
            print(f"\n[TOPOLOGY] ▶ Processing at {device.device_name}")
            
            # Create a mock packet for simulation
            class MockPacket:
                def __init__(self, source_ip, dest_ip, data):
                    self.source_ip = source_ip
                    self.dest_ip = dest_ip
                    self.data = data
                    self.ttl = 64
                    self.source_mac = None
                    self.dest_mac = None
                    
            mock_packet = MockPacket(source_ip, dest_ip, packet_data)
            
            # Process packet based on device type
            if device.device_type == DeviceType.END_DEVICE:
                if i == 0:  # Source device
                    print(f"[{device.device_name}] ▶ Originating packet")
                elif i == len(path) - 1:  # Destination device
                    success = device.process_packet(mock_packet, "eth0")
                    if success:
                        print(f"[{device.device_name}] ✓ Packet delivered")
                        return True
                    else:
                        print(f"[{device.device_name}] ❌ Packet rejected")
                        return False
            else:
                # Network device (switch, router, hub)
                receiving_interface = "port1"  # Simplified
                device.process_packet(mock_packet, receiving_interface)
                
        return True
        
    def display_topology(self):
        """Display the current network topology"""
        print(f"\n[TOPOLOGY] === NETWORK TOPOLOGY ===")
        
        print(f"\nDevices:")
        for device_id, device in self.devices.items():
            print(f"  {device_id}: {device.device_type.value} - {device.device_name}")
            if hasattr(device, 'ip_address'):
                print(f"    IP: {device.ip_address}")
            if hasattr(device, 'mac_address'):
                print(f"    MAC: {device.mac_address}")
                
        print(f"\nConnections:")
        for connection in self.connections:
            print(f"  {connection['device1']}:{connection['interface1']} <-> {connection['device2']}:{connection['interface2']}")
            
        print(f"\nNetworks:")
        for network_id, network in self.networks.items():
            print(f"  {network_id}: {network['address']} - {network['description']}")

def create_sample_topology():
    """Create a sample network topology for testing"""
    topology = NetworkTopologyManager()
    
    # Create devices
    pc1 = EndDevice("pc1", "PC1", "192.168.1.10", "00:11:22:33:44:10")
    pc2 = EndDevice("pc2", "PC2", "192.168.1.20", "00:11:22:33:44:20")
    server = EndDevice("server", "Server", "192.168.2.10", "00:11:22:33:44:30")
    
    switch1 = Switch("sw1", "Switch1")
    router1 = Router("r1", "Router1")
    
    # Add devices to topology
    topology.add_device(pc1)
    topology.add_device(pc2)
    topology.add_device(server)
    topology.add_device(switch1)
    topology.add_device(router1)
    
    # Configure router interfaces
    router1.add_network_interface("eth0", "192.168.1.1", "192.168.1.0/24")
    router1.add_network_interface("eth1", "192.168.2.1", "192.168.2.0/24")
    
    # Set default gateways
    pc1.set_default_gateway("192.168.1.1")
    pc2.set_default_gateway("192.168.1.1")
    server.set_default_gateway("192.168.2.1")
    
    # Create networks
    topology.create_network("net1", "192.168.1.0/24", "LAN Network 1")
    topology.create_network("net2", "192.168.2.0/24", "LAN Network 2")
    
    # Connect devices
    topology.connect_devices("pc1", "eth0", "sw1", "port1")
    topology.connect_devices("pc2", "eth0", "sw1", "port2")
    topology.connect_devices("sw1", "port3", "r1", "eth0")
    topology.connect_devices("r1", "eth1", "server", "eth0")
    
    return topology

def test_topology():
    """Test the network topology"""
    topology = create_sample_topology()
    topology.display_topology()
    
    # Test packet flow
    print("\n" + "="*60)
    print("TESTING PACKET FLOW")
    print("="*60)
    
    # Same network communication
    print("\n--- Same Network Communication ---")
    topology.simulate_packet_flow("192.168.1.10", "192.168.1.20", "Hello PC2!")
    
    # Cross network communication
    print("\n--- Cross Network Communication ---")
    topology.simulate_packet_flow("192.168.1.10", "192.168.2.10", "Hello Server!")

if __name__ == "__main__":
    test_topology()
