"""
CLI Utilities for Network Simulator
Provides better CLI interaction and visualization
"""

import time
import random

class CLIUtils:
    @staticmethod
    def print_header(header_text):
        """
        Print a formatted header
        
        Args:
            header_text (str): Header text to display
        """
        line_width = 60
        print("\n" + "=" * line_width)
        print(f"{header_text.center(line_width)}")
        print("=" * line_width)
    
    @staticmethod
    def print_section(section_text):
        """
        Print a formatted section header
        
        Args:
            section_text (str): Section text to display
        """
        
    @staticmethod
    def print_subsection(text):
        """Print a subsection with simple formatting"""
        print(f"\n--- {text} ---")
        
    @staticmethod
    def progress_bar(duration=1.0, prefix="Processing", length=30):
        """Show a progress bar for the specified duration"""
        print(f"{prefix}: ", end="", flush=True)
        for i in range(length + 1):
            time.sleep(duration / length)
            progress = i / length
            bar = "█" * i + " " * (length - i)
            percent = int(progress * 100)
            print(f"\r{prefix}: [{bar}] {percent}%", end="", flush=True)
        print()
    
    @staticmethod
    def print_progress(description, success=True):
        """
        Print a progress message with status indicator
        
        Args:
            description (str): Progress description
            success (bool): Whether the operation was successful
        """
        indicator = "✓" if success else "✗"
        print(f"[{indicator}] {description}")
    
    @staticmethod
    def simulate_network_delay(min_time=0.1, max_time=0.5):
        """
        Simulate network delay
        
        Args:
            min_time (float): Minimum delay time
            max_time (float): Maximum delay time
        """
        delay = random.uniform(min_time, max_time)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def print_transmission_animation(source, destination, length=30):
        """
        Display a simple animation for data transmission
        
        Args:
            source (str): Source name
            destination (str): Destination name
            length (int): Animation length
        """
        print(f"\nTransmitting data from {source} to {destination}:")
        print(f"{source} ", end="")
        
        for i in range(length):
            if i == length - 1:
                print(">", end="")
            else:
                print(".", end="")
            time.sleep(0.03)
        
        print(f" {destination}")
    
    @staticmethod
    def print_device_table(devices):
        """
        Print a formatted table of devices
        
        Args:
            devices (list): List of EndDevices objects
        """
        if not devices:
            print("No devices found.")
            return
            
        print("\n=== DEVICE INFORMATION ===")
        print(f"{'Device Name':<12} {'MAC Address':<15} {'IP Address':<15}")
        print(f"{'-'*12:<12} {'-'*15:<15} {'-'*15:<15}")
        
        for device in devices:
            print(f"{device.get_device_name():<12} {device.get_mac():<15} {device.IP:<15}")
    
    @staticmethod
    def print_network_topology(routers, switches, hubs, devices):
        """
        Print a simple text representation of the network topology
        
        Args:
            routers (list): List of Router objects
            switches (list): List of Switch objects
            hubs (list): List of Hub objects
            devices (list): List of EndDevices objects
        """
        CLIUtils.print_header("NETWORK TOPOLOGY")
        
        print(f"Total Routers: {len(routers)}")
        print(f"Total Switches: {len(switches)}")
        print(f"Total Hubs: {len(hubs)}")
        print(f"Total End Devices: {len(devices)}")
        
        # Print router -> switch -> hub -> device hierarchy
        for r_idx, router in enumerate(routers):
            print(f"\nRouter {r_idx} ({router.get_ip()})")
            
            # Find switches connected to this router
            router_switches = [s for s in switches if s in router.get_switches()]
            
            for s_idx, switch in enumerate(router_switches):
                print(f"  ├── Switch {switch.switch_number}")
                
                # Find hubs connected to this switch
                for h_idx, hub in enumerate(hubs):
                    # This is a simplified check - in a real implementation we'd need proper
                    # tracking of hub-switch connections
                    if hub in switch.hubs:
                        is_last_hub = h_idx == len(switch.hubs) - 1
                        hub_prefix = "  │   └── " if is_last_hub else "  │   ├── "
                        print(f"  │   {hub_prefix}Hub {hub.get_hub_number()}")
                        
                        # Find devices connected to this hub
                        hub_devices = hub.get_connected_devices()
                        if hub_devices:
                            for d_idx, device in enumerate(hub_devices):
                                is_last_device = d_idx == len(hub_devices) - 1
                                device_prefix = "      " if is_last_hub else "  │   "
                                device_branch = "└── " if is_last_device else "├── "
                                print(f"  │   {device_prefix}{device_branch}Device {device.get_device_name()} ({device.get_mac()}, {device.IP})")
    
    @staticmethod
    def get_user_choice(prompt, options):
        """
        Get a valid user choice from options
        
        Args:
            prompt (str): Prompt to display
            options (list): List of valid options
            
        Returns:
            str: User's choice
        """
        while True:
            choice = input(prompt)
            if choice in options:
                return choice
            print(f"Invalid choice. Please choose from {options}")
    
    @staticmethod
    def clear_screen():
        """Clear the terminal screen"""
        print("\033c", end="")  # ANSI escape sequence to clear screen
