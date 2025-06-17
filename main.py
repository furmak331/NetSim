"""
Main entry point for the Network Simulator
"""

from network_simulator import NetworkSimulator
from cli_utils import CLIUtils

def show_welcome_message():
    """Display a welcome message with program information"""
    CLIUtils.print_header("NETWORK SIMULATOR")
    print("\nThis simulator demonstrates networking concepts including:")
    print("• Hub broadcasting")
    print("• Switch frame forwarding")
    print("• Router routing")
    print("• CRC error detection")
    print("• DNS resolution")
    print("• Physical and Data Link layer operations")
    print("\nCreated for educational purposes")

if __name__ == "__main__":
    # Show welcome message
    show_welcome_message()
    
    # Initialize the network simulator
    simulator = NetworkSimulator()
    
    # Run the simulator with enhanced CLI
    simulator.run_simulator()
