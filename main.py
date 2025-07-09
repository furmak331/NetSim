"""
Main entry point for the Network Simulator
"""

from network_simulator import NetworkSimulator
from cli_utils import CLIUtils

def show_welcome_message():
    """Display a welcome message with program information"""
    CLIUtils.print_header("NETWORK SIMULATOR")
    print("\nThis simulator demonstrates networking concepts including:")
    print("• Hub broadcasting and switch frame forwarding")
    print("• Router routing with RIP protocol")
    print("• Complete TCP/IP protocol stack")
    print("• CRC error detection and Go-Back-N flow control")
    print("• DNS resolution and application protocols")
    print("\nCreated for educational purposes")

def main():
    """Main entry point"""
    show_welcome_message()
    simulator = NetworkSimulator()
    simulator.run_simulator()

if __name__ == "__main__":
    main()
