"""
Hub implementation for Network Simulator
Equivalent to Hub.java in the Java implementation
"""

class Hub:
    def __init__(self, hub_number):
        """
        Initialize hub with a hub number
        
        Args:
            hub_number (int): Hub identification number
        """
        self.sender_address = None
        self.receiver_address = None
        self.hub_number = hub_number
        self.data = None
        self.devices_connected = None
    
    def receive_data_from_sender(self, d):
        """
        Receive data from a sender
        
        Args:
            d (str): Data received from a sender device
        """
        self.data = d
        print(f"Hub {self.hub_number} received data from sender")
    
    def send_data_to_receiver(self, receiver_device):
        """
        Send data to a receiver device
        
        Args:
            receiver_device (EndDevices): The receiver device
        """
        self.receiver_address = receiver_device.get_mac()
        receiver_device.set_receiver_data(self.data)
        print(f"Hub {self.hub_number} sent data to receiver {receiver_device.get_device_name()}")
    
    def get_hub_number(self):
        """Get hub number"""
        return self.hub_number
    
    def get_receiver_address(self):
        """Get receiver address"""
        return self.receiver_address
    
    def get_sender_address(self):
        """Get sender address"""
        return self.sender_address
    
    def store_devices_connected(self, dev):
        """
        Store connected devices
        
        Args:
            dev (list): List of connected devices
        """
        self.devices_connected = dev
    
    def get_connected_devices(self):
        """Get connected devices"""
        return self.devices_connected
    
    def send_data_to_switch(self, switch_new, sender_hub, receiver_hub, sender, receiver):
        """
        Send data through a switch if needed
        
        Args:
            switch_new (Switch): Switch to use
            sender_hub (Hub): Sender's hub
            receiver_hub (Hub): Receiver's hub
            sender (EndDevices): Sender device
            receiver (EndDevices): Receiver device
        """
        # Perform broadcast to all devices in the sender hub
        broadcast_dev = sender_hub.get_connected_devices()
        flag = 0
        
        for i in range(len(broadcast_dev)):
            if broadcast_dev[i].get_mac() == receiver.get_mac():
                print(f"Data received by receiver {broadcast_dev[i].get_device_name()}")
                flag = 1
            else:
                print(f"Data discarded by device {broadcast_dev[i].get_device_name()}")
        
        if flag == 1:
            # Receiver is in the same hub, no need for switch
            print("Receiver in the same hub, no need to send data to switch")
            sender_hub.receive_data_from_sender(sender.data)
            sender_hub.send_data_to_receiver(receiver)
            print("Data transfer from hub by the receiver completed")
        else:
            # Receiver is in another hub, need to use switch
            print("Receiver in another hub, send data to switch")
            sender_hub.receive_data_from_sender(sender.get_data())
            print("Send data to switch")
            switch_new.send_data_via_hub(sender_hub, receiver_hub, sender, receiver)
    
    def send_ACK_or_NAK(self):
        """Send ACK or NAK (placeholder)"""
        pass
    
    def receive_ACK_or_NAK(self):
        """Receive ACK or NAK (placeholder)"""
        pass
