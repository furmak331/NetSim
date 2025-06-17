"""
End Devices implementation for Network Simulator
Equivalent to EndDevices.java in the Java implementation
"""

class EndDevices:
    def __init__(self, MAC, name, IP):
        """
        Initialize an end device with MAC address, name and IP
        
        Args:
            MAC (int): MAC address of the device
            name (str): Single character name of the device
            IP (str): IP address of the device
        """
        self.MAC = MAC
        self.device_name = name
        self.data = ""
        self.ACKorNAK = "ACK"
        self.IP = IP
        self.ARP_cache = {MAC: IP}  # Store own MAC and IP in ARP cache
    
    def send_ARP_request(self, receiver):
        """
        Send ARP request to a receiver device
        
        Args:
            receiver (EndDevices): The receiver device
        """
        self.ARP_cache[receiver.get_mac()] = receiver.IP
    
    def get_mac(self):
        """Get MAC address of this device"""
        return self.MAC
    
    def set_data(self, d):
        """Set data for this device"""
        self.data = d
    
    def get_data(self):
        """Get data from this device"""
        return self.data
    
    def set_receiver_data(self, d):
        """
        Set data for receiving, applying CRC check
        
        Args:
            d (str): Data to be received
        """
        from crc_for_datalink import CRCforDataLink
        import random
        self.data = CRCforDataLink().receiver_code(d, random.random())
    
    def send_data_and_address_to_hub(self, hub):
        """
        Send data and address to hub
        
        Args:
            hub (Hub): The hub to send data to
        """
        hub.sender_address = self.MAC
        hub.receive_data_from_sender(self.data)
        print("Data sent to hub")
    
    def send_data_to_receiver(self, receiver):
        """
        Send data directly to receiver
        
        Args:
            receiver (EndDevices): The receiver device
        """
        print("Data sent by sender")
        receiver.set_data(self.data)
        print("Data received by receiver")
    
    def get_device_name(self):
        """Get the name of this device"""
        return self.device_name
    
    def send_ACK_or_NAK(self, check_error, sender_device):
        """
        Send ACK or NAK based on error check
        
        Args:
            check_error (bool): Whether error was detected
            sender_device (EndDevices): The sender device
        """
        if check_error:
            sender_device.ACKorNAK = "NAK"
        else:
            sender_device.ACKorNAK = "ACK"
