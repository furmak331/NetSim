"""
Switch testing functionality for network simulator
"""

def test_switch_mac_learning(sender_device, receiver_device, switch):
    """
    Test MAC address learning functionality of a switch
    
    Args:
        sender_device: The device sending data
        receiver_device: The device receiving data
        switch: The switch connecting the devices
    """
    # First transmission - Switch should learn MAC addresses
    print("\n=== SWITCH MAC ADDRESS LEARNING DEMONSTRATION ===")
    print("\nThis demonstration shows how switches learn MAC addresses and improve efficiency.")
    print("When a switch first receives a frame for an unknown destination, it floods the frame to all ports.")
    print("As the switch learns MAC addresses, it builds a MAC address table and can forward directly.")
    
    print("\n--- PHASE 1: FIRST TRANSMISSION (LEARNING PHASE) ---")
    print(f"Sending data from Device {sender_device.get_device_name()} to Device {receiver_device.get_device_name()}")
    
    # Get data from user
    data = input("Enter data to send for first transmission: ")
    
    # Set data in sender device
    sender_device.set_data(data)
    
    # Show initial MAC table status before sending
    print("\nInitial MAC address table state:")
    switch.display_mac_table()
    
    # In the first transmission, the switch doesn't know where the receiver is
    # It will have to broadcast the frame to all ports (flood) and learn from response
    print(f"\n[SWITCH {switch.switch_number}] === MAC ADDRESS LEARNING PROCESS ===")
    print(f"[SWITCH {switch.switch_number}] ▶ Frame arrives at switch from Device {sender_device.get_device_name()}")
    print(f"[SWITCH {switch.switch_number}] ⓘ Learning source MAC address: {sender_device.get_mac()} on Port 1")
    print(f"[SWITCH {switch.switch_number}] ⚠ Destination MAC address {receiver_device.get_mac()} not found in table")
    print(f"[SWITCH {switch.switch_number}] ▶ FLOODING frame to all ports (first-time broadcast)")
    
    # Add the sender to MAC table
    if hasattr(switch, 'mac_table'):
        switch.mac_table[sender_device.get_mac()] = "PORT 1"
    
    # Simulate flooding to all ports
    print("\n[SWITCH FLOODING]:")
    for i, device in enumerate(switch.connected_direct):
        if device != sender_device:
            port_num = i + 1
            print(f"[SWITCH {switch.switch_number}] ▶ Forwarding to PORT {port_num} (Device {device.get_device_name()})")
    
    # Send to the actual receiver
    switch.send_direct_data(sender_device, receiver_device)
    
    # When receiver responds, switch learns its location
    print(f"\n[DEVICE {receiver_device.get_device_name()}] ▶ Sending response to {sender_device.get_device_name()}")
    print(f"[SWITCH {switch.switch_number}] ⓘ Learning source MAC address: {receiver_device.get_mac()} on Port 2")
    
    # Now add the receiver to the MAC table
    if hasattr(switch, 'mac_table'):
        port_num = switch.connected_direct.index(receiver_device) + 1
        switch.mac_table[receiver_device.get_mac()] = f"PORT {port_num}"
    
    # Show updated MAC table
    print("\nMAC address table after first transmission:")
    switch.display_mac_table()
    
    # Second transmission - Switch should use MAC table for direct forwarding
    print("\n--- PHASE 2: SECOND TRANSMISSION (DIRECT FORWARDING) ---")
    
    # Get new data
    data = input("Enter data to send for second transmission: ")
    
    # Set data in sender device
    sender_device.set_data(data)
    
    # Now the switch knows both MAC addresses and can do direct forwarding
    port_num = switch.connected_direct.index(receiver_device) + 1
    print(f"\n[SWITCH {switch.switch_number}] === DIRECT FORWARDING ===")
    print(f"[SWITCH {switch.switch_number}] ▶ Frame arrives at switch from Device {sender_device.get_device_name()}")
    print(f"[SWITCH {switch.switch_number}] ✓ Source MAC {sender_device.get_mac()} found in table (PORT 1)")
    print(f"[SWITCH {switch.switch_number}] ✓ Destination MAC {receiver_device.get_mac()} found in table (PORT {port_num})")
    print(f"[SWITCH {switch.switch_number}] ▶ DIRECT FORWARDING: Sending frame only to PORT {port_num}")
    
    # Forward directly to destination
    switch.send_direct_data(sender_device, receiver_device)
    
    # Add a third device to demonstrate MAC table growth
    add_third_device = input("\nDo you want to add a third device to demonstrate more MAC learning? (y/n): ").lower() == 'y'
    
    if add_third_device and len(switch.connected_direct) >= 3:
        # Get third device (different from sender and receiver)
        potential_devices = [d for d in switch.connected_direct if d != sender_device and d != receiver_device]
        
        if potential_devices:
            third_device = potential_devices[0]
            print(f"\n--- PHASE 3: THIRD DEVICE COMMUNICATION ---")
            print(f"Device {third_device.get_device_name()} will now send data to Device {sender_device.get_device_name()}")
            
            # Get new data
            data = input(f"Enter data for Device {third_device.get_device_name()} to send: ")
            
            # Set data in third device
            third_device.set_data(data)
            
            # Third device is not in MAC table yet
            port_num = switch.connected_direct.index(third_device) + 1
            print(f"\n[SWITCH {switch.switch_number}] === MAC TABLE GROWS ===")
            print(f"[SWITCH {switch.switch_number}] ▶ Frame arrives from new Device {third_device.get_device_name()}")
            print(f"[SWITCH {switch.switch_number}] ⓘ Learning new source MAC: {third_device.get_mac()} on PORT {port_num}")
            print(f"[SWITCH {switch.switch_number}] ✓ Destination MAC {sender_device.get_mac()} found in table")
            print(f"[SWITCH {switch.switch_number}] ▶ DIRECT FORWARDING: Sending frame only to destination port")
            
            # Add third device to MAC table
            if hasattr(switch, 'mac_table'):
                switch.mac_table[third_device.get_mac()] = f"PORT {port_num}"
            
            # Forward to the first device
            switch.send_direct_data(third_device, sender_device)
            
            # Show final MAC table
            print("\nFinal MAC address table with three devices:")
            switch.display_mac_table()
    
    print("\n=== SWITCH OPERATION COMPLETED SUCCESSFULLY ===")
