"""
Main entry point for the Network Simulator
"""

from network_simulator import NetworkSimulator

if __name__ == "__main__":
    print("Starting Network Simulator...")
    simulator = NetworkSimulator()
    simulator.run_simulator()
