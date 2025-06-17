"""
Router implementation for Network Simulator
Equivalent to Router.java in the Java implementation
"""

class Router:
    def __init__(self, number, NID):
        """
        Initialize router with a number and Network ID
        
        Args:
            number (int): Router identification number
            NID (str): Network ID
        """
        self.NID = NID
        self.data = None
        self.routing_table = {}  # HashMap<String, String[]> in Java
        self.router_number = number
        self.switches = []
    
    def get_data_from_sender_switch(self, data):
        """
        Get data from sender switch
        
        Args:
            data (str): Data from sender switch
        """
        self.data = data
    
    def send_data_to_receiver_switch(self):
        """
        Send data to receiver switch
        
        Returns:
            str: Data to be sent
        """
        return self.data
    
    def store_connected_switches(self, switches):
        """
        Store connected switches
        
        Args:
            switches (list): List of connected switches
        """
        self.switches = switches
    
    def get_connected_switches(self):
        """
        Get connected switches
        
        Returns:
            list: List of connected switches
        """
        return self.switches
