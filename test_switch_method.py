    def test_switch_operation(self):
        """Test switch operation and MAC address learning"""
        print("\n--- SWITCH OPERATION TEST ---")
        
        # Check if we have any switches with directly connected devices
        switches_with_devices = []
        for switch in self.switches:
            if len(switch.connected_direct) >= 2:
                switches_with_devices.append(switch)
        
        if not switches_with_devices:
            print("No switches with at least two directly connected devices available.")
            
            # Ask if user wants to create a switch with directly connected devices
            create_new = input("Do you want to create a switch with devices for testing? (y/n): ").lower() == 'y'
            if create_new:
                # Create a switch
                switch = Switch(len(self.switches))
                self.switches.append(switch)
                print(f"Created Switch {switch.switch_number}")
                
                # Create devices
                devices = []
                for i in range(2):  # Create at least 2 devices
                    device_name = chr(65 + len(self.devices))
                    mac_address = len(self.devices) + 1
                    ip_address = f"192.168.{switch.switch_number+1}.{i+1}"
                    
                    device = EndDevices(mac_address, device_name, ip_address)
                    devices.append(device)
                    self.devices.append(device)
                    print(f"Created device {device_name} with IP {ip_address} and MAC {mac_address}")
                    
                    # Connect device to switch
                    switch.add_to_direct_connection_table(device)
                
                # Store direct connections in the switch
                switch.store_directly_connected_devices(devices)
                
                # Use this switch for testing
                switches_with_devices = [switch]
            else:
                print("Returning to main menu.")
                return
        
        # Let user select a switch
        if len(switches_with_devices) > 1:
            print("Available switches with directly connected devices:")
            for i, switch in enumerate(switches_with_devices):
                print(f"{i+1}. Switch {switch.switch_number} with {len(switch.connected_direct)} connected devices")
            
            selection = int(input("Select a switch for testing (number): ")) - 1
            switch = switches_with_devices[selection]
        else:
            switch = switches_with_devices[0]
            print(f"Using Switch {switch.switch_number} for testing.")
        
        # Show devices connected to this switch
        print(f"\nDevices connected to Switch {switch.switch_number}:")
        for i, device in enumerate(switch.connected_direct):
            print(f"{i+1}. Device {device.get_device_name()}: MAC={device.get_mac()}, IP={device.IP}")
        
        # Let user select sender and receiver
        sender_index = int(input("Select sender device (number): ")) - 1
        sender_device = switch.connected_direct[sender_index]
        
        receiver_index = int(input("Select receiver device (number): ")) - 1
        receiver_device = switch.connected_direct[receiver_index]
        
        # Import and use the test_switch_operation module
        from test_switch_operation import test_switch_mac_learning
        
        # Run the test
        test_switch_mac_learning(sender_device, receiver_device, switch)
