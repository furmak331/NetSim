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
        self.connected_via_hub = {}  # Maps EndDevices to Hub
        self.data = None
    
    def get_data(self, data):
        """
        Get data for this switch
        
        Args:
            data (str): Data to store
        """
        self.data = data
    
    def store_directly_connected_devices(self, devices):
        """
        Store directly connected devices
        
        Args:
            devices (list): List of directly connected devices
        """
        self.devices_directly_connected = devices
    
    def store_connected_hubs(self, hubs):
        """
        Store connected hubs
        
        Args:
            hubs (list): List of connected hubs
        """
        self.hubs = hubs
    
    def add_to_direct_connection_table(self, device):
        """
        Add device to direct connection table
        
        Args:
            device (EndDevices): Device to add
        """
        self.connected_direct.append(device)
    
    def add_to_hub_connected_table(self, hub, device):
        """
        Add device to hub connection table
        
        Args:
            hub (Hub): Hub the device is connected to
            device (EndDevices): Device to add
        """
        self.connected_via_hub[device] = hub
    
    def send_direct_data(self, sender_device, receiver_device):
        """
        Send data directly between devices
        
        Args:
            sender_device (EndDevices): Sender device
            receiver_device (EndDevices): Receiver device
        """
        data = sender_device.get_data()
        print("Data received by the switch")
        print("Data sent to the receiver")
        receiver_device.set_receiver_data(data)
        print("Data received by the receiver")
    
    def send_data_via_hub(self, sender_hub, receiver_hub, sender, receiver):
        """
        Send data between hubs
        
        Args:
            sender_hub (Hub): Sender's hub
            receiver_hub (Hub): Receiver's hub
            sender (EndDevices): Sender device
            receiver (EndDevices): Receiver device
        """
        # Learn sender's MAC address and hub
        self.add_to_hub_connected_table(sender_hub, sender)
        print("Sender added to the switch table")
        
        # Forward data to receiver's hub
        receiver_hub.receive_data_from_sender(sender_hub.data)
        print("Data sent to the receiver hub")
        
        # Have the receiver hub deliver to the device
        receiver_hub.send_data_to_receiver(receiver)
        print("Data received by the receiver")
    
    def send_ACK_or_NAK(self):
        """Send ACK or NAK (placeholder)"""
        pass
