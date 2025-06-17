"""
Switch implementation for Network Simulator
Equivalent to Switch.java in the Java implementation
"""

class Switch:
    def __init__(self, num):
        """
        Initialize switch with a number
        
        Args:
            num (int): Switch identification number
        """
        self.switch_number = num
        self.hubs = []
        self.devices_directly_connected = None
        self.connected_direct = []
        self.connected_via_hub = {}  # Maps MAC address to Hub for faster lookup
        self.data = None
        print(f"[SWITCH {num}] ▶ Switch initialized")
    
    def get_data(self, data):
        """
        Get data for this switch
        
        Args:
            data (str): Data to store
        """
        self.data = data
        print(f"[SWITCH {self.switch_number}] ▶ Received data for forwarding")
    
    def store_directly_connected_devices(self, devices):
        """
        Store directly connected devices
        
        Args:
            devices (list): List of directly connected devices
        """
        self.devices_directly_connected = devices
        print(f"[SWITCH {self.switch_number}] ▶ Added {len(devices)} directly connected devices")
    
    def store_connected_hubs(self, hubs):
        """
        Store connected hubs
        
        Args:
            hubs (list): List of connected hubs
        """
        self.hubs = hubs
        hub_numbers = [hub.get_hub_number() for hub in hubs]
        print(f"[SWITCH {self.switch_number}] ▶ Connected to Hubs: {hub_numbers}")
    
    def add_to_direct_connection_table(self, device):
        """
        Add device to direct connection table
        
        Args:
            device (EndDevices): Device to add
        """
        self.connected_direct.append(device)
        print(f"[SWITCH {self.switch_number}] ▶ Added device {device.get_device_name()} (MAC: {device.get_mac()}) to direct connections")
    
    def add_to_hub_connected_table(self, hub, device):
        """
        Add device to hub connection table
        
        Args:
            hub (Hub): Hub the device is connected to
            device (EndDevices): Device to add
        """
        # Use MAC address as the key for faster lookups
        self.connected_via_hub[device.get_mac()] = hub
        print(f"[SWITCH {self.switch_number}] ⓘ MAC Table Update: {device.get_mac()} → Hub {hub.get_hub_number()}")
    
    def display_mac_table(self):
        """Display the current MAC address table"""
        print(f"\n[SWITCH {self.switch_number}] === MAC ADDRESS TABLE ===")
        if not self.connected_via_hub:
            print(f"[SWITCH {self.switch_number}] Table is empty.")
        else:
            print(f"[SWITCH {self.switch_number}] {'MAC Address':<15} | {'Connected to Hub'}")
            print(f"[SWITCH {self.switch_number}] {'-'*15} | {'-'*15}")
            for mac, hub in self.connected_via_hub.items():
                print(f"[SWITCH {self.switch_number}] {mac:<15} | Hub {hub.get_hub_number()}")
    
    def send_direct_data(self, sender_device, receiver_device):
        """
        Send data directly between devices
        
        Args:
            sender_device (EndDevices): Sender device
            receiver_device (EndDevices): Receiver device
        """
        data = sender_device.get_data()
        print(f"\n[SWITCH {self.switch_number}] === DIRECT SWITCHING ===")
        print(f"[SWITCH {self.switch_number}] ▶ Source: {sender_device.get_device_name()} (MAC: {sender_device.get_mac()})")
        print(f"[SWITCH {self.switch_number}] ▶ Destination: {receiver_device.get_device_name()} (MAC: {receiver_device.get_mac()})")
        
        # Unlike a hub, a switch only forwards to the specific destination
        print(f"[SWITCH {self.switch_number}] ▶ Forwarding frame directly to destination")
        receiver_device.set_receiver_data(data)
        print(f"[SWITCH {self.switch_number}] ✓ Frame forwarded to destination")
    
    def send_data_via_hub(self, sender_hub, receiver_hub, sender, receiver):
        """
        Send data between hubs via switch
        
        Args:
            sender_hub (Hub): Sender's hub
            receiver_hub (Hub): Receiver's hub
            sender (EndDevices): Sender device
            receiver (EndDevices): Receiver device
        """
        print(f"\n[SWITCH {self.switch_number}] === INTER-HUB SWITCHING ===")
        print(f"[SWITCH {self.switch_number}] ▶ Source: Hub {sender_hub.get_hub_number()}")
        print(f"[SWITCH {self.switch_number}] ▶ Source device: {sender.get_device_name()} (MAC: {sender.get_mac()})")
        print(f"[SWITCH {self.switch_number}] ▶ Destination device: {receiver.get_device_name()} (MAC: {receiver.get_mac()})")
        
        # Learn sender's MAC address and hub (building MAC address table)
        self.add_to_hub_connected_table(sender_hub, sender)
        
        # Check if the switch knows which hub the receiver is connected to
        receiver_hub_from_table = self.connected_via_hub.get(receiver.get_mac())
        
        if receiver_hub_from_table is not None:
            print(f"[SWITCH {self.switch_number}] ✓ MAC table lookup successful: {receiver.get_mac()} → Hub {receiver_hub_from_table.get_hub_number()}")
            
            # Verify if our knowledge is correct
            if receiver_hub_from_table.get_hub_number() != receiver_hub.get_hub_number():
                print(f"[SWITCH {self.switch_number}] ⚠ MAC table outdated! Updating: {receiver.get_mac()} is now at Hub {receiver_hub.get_hub_number()}")
                self.add_to_hub_connected_table(receiver_hub, receiver)
        else:
            print(f"[SWITCH {self.switch_number}] ⓘ MAC {receiver.get_mac()} not in table, learning it's at Hub {receiver_hub.get_hub_number()}")
            self.add_to_hub_connected_table(receiver_hub, receiver)
            
        # Display the current MAC table
        self.display_mac_table()
        
        # Forward data to the receiver's hub
        print(f"[SWITCH {self.switch_number}] ▶ Forwarding frame from Hub {sender_hub.get_hub_number()} to Hub {receiver_hub.get_hub_number()}")
        receiver_hub.receive_data_from_sender(sender_hub.data)
        print(f"[SWITCH {self.switch_number}] ✓ Frame forwarded to Hub {receiver_hub.get_hub_number()}")
        
        # The receiver hub will broadcast to its connected devices
        # When a hub receives data, it broadcasts to all connected devices
        receiver_hub.send_data_to_receiver(receiver)
        print(f"[SWITCH {self.switch_number}] ✓ Transfer complete")
    
    def send_ACK_or_NAK(self):
        """Send ACK or NAK (placeholder)"""
        pass
