"""
Main entry point for the Network Simulator
"""

import argparse
import sys
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

def main():
    """Main entry point with command line argument processing"""
    parser = argparse.ArgumentParser(description="Network Simulator")
    parser.add_argument("--demo", action="store_true", help="Run the comprehensive network demo")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    if args.demo:
        # Run the comprehensive demo
        print("Running comprehensive network demo...")
        # We import here to avoid circular imports
        from test_comprehensive_network import main as run_demo
        run_demo()
    else:
        # Run the regular simulator
        show_welcome_message()
        simulator = NetworkSimulator()
        simulator.run_simulator()

if __name__ == "__main__":
    main()
