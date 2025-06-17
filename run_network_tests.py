"""
Network simulator test runner
Provides a command-line interface for running different network tests
"""

import argparse
import sys
from cli_utils import CLIUtils
from test_comprehensive_network import main as run_comprehensive_test

# Import other test modules differently since they don't have main functions
import test_router_operation
import test_switch_operation

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Network Simulator Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available tests:
  comprehensive - Full network simulation with all layers and protocols
  router        - Router-specific operations and packet forwarding
  switch        - Switch-specific operations and MAC learning
        """
    )
    
    parser.add_argument("test", 
                      nargs="?",
                      default="comprehensive",
                      choices=["comprehensive", "router", "switch"],
                      help="The test to run (default: comprehensive)")
    
    parser.add_argument("-v", "--verbose", 
                      action="store_true", 
                      help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Run the selected test
    if args.test == "comprehensive":
        CLIUtils.print_header("RUNNING COMPREHENSIVE NETWORK TEST")
        run_comprehensive_test()
    elif args.test == "router":
        CLIUtils.print_header("RUNNING ROUTER OPERATION TEST")
        print("Router operation test is currently disabled")
        # We would need to implement a main function for router_operation or call specific test functions
    elif args.test == "switch":
        CLIUtils.print_header("RUNNING SWITCH OPERATION TEST")
        print("Switch operation test is currently disabled")
        # We would need to implement a main function for switch_operation or call specific test functions
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
