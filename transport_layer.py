"""
Transport Layer implementation for Network Simulator
Implements TCP and UDP protocols with proper port management and flow control
"""

import random
import time
from enum import Enum
from checksum_for_datalink import ChecksumForDataLink

class ProtocolType(Enum):
    TCP = 6
    UDP = 17

class ConnectionState(Enum):
    CLOSED = "CLOSED"
    SYN_SENT = "SYN_SENT"
    SYN_RECEIVED = "SYN_RECEIVED"
    ESTABLISHED = "ESTABLISHED"
    FIN_WAIT_1 = "FIN_WAIT_1"
    FIN_WAIT_2 = "FIN_WAIT_2"
    CLOSE_WAIT = "CLOSE_WAIT"
    CLOSING = "CLOSING"
    LAST_ACK = "LAST_ACK"
    TIME_WAIT = "TIME_WAIT"

class TCPFlags:
    """TCP Flag constants"""
    SYN = 0x02
    ACK = 0x10
    FIN = 0x01
    RST = 0x04
    PSH = 0x08
    URG = 0x20

class PortManager:
    """Manages port allocation for processes"""
    
    # Well-known ports (0-1023)
    WELL_KNOWN_PORTS = {
        20: "FTP-DATA",
        21: "FTP-CONTROL",
        22: "SSH",
        23: "TELNET",
        25: "SMTP",
        53: "DNS",
        67: "DHCP-SERVER",
        68: "DHCP-CLIENT",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        993: "IMAPS",
        995: "POP3S"
    }
    
    def __init__(self):
        self.allocated_ports = set()
        self.ephemeral_range = (1024, 65535)
        self.process_port_map = {}  # Maps process_id to allocated ports
        
    def allocate_ephemeral_port(self, process_id):
        """
        Allocate an ephemeral port for a process
        
        Args:
            process_id (str): Process identifier
            
        Returns:
            int: Allocated port number, None if no ports available
        """
        for attempt in range(100):  # Try up to 100 times
            port = random.randint(*self.ephemeral_range)
            if port not in self.allocated_ports and port not in self.WELL_KNOWN_PORTS:
                self.allocated_ports.add(port)
                if process_id not in self.process_port_map:
                    self.process_port_map[process_id] = []
                self.process_port_map[process_id].append(port)
                print(f"[TRANSPORT] ▶ Allocated ephemeral port {port} to process {process_id}")
                return port
        
        print(f"[TRANSPORT] ❌ No available ephemeral ports for process {process_id}")
        return None
    
    def allocate_well_known_port(self, port, process_id):
        """
        Allocate a well-known port for a service
        
        Args:
            port (int): Well-known port number
            process_id (str): Process identifier
            
        Returns:
            bool: True if successful, False if port unavailable
        """
        if port in self.allocated_ports:
            print(f"[TRANSPORT] ❌ Port {port} already in use")
            return False
            
        if port not in self.WELL_KNOWN_PORTS:
            print(f"[TRANSPORT] ⚠ Port {port} is not a well-known port")
            
        self.allocated_ports.add(port)
        if process_id not in self.process_port_map:
            self.process_port_map[process_id] = []
        self.process_port_map[process_id].append(port)
        
        service_name = self.WELL_KNOWN_PORTS.get(port, "UNKNOWN")
        print(f"[TRANSPORT] ▶ Allocated well-known port {port} ({service_name}) to process {process_id}")
        return True
    
    def deallocate_port(self, port, process_id):
        """
        Deallocate a port from a process
        
        Args:
            port (int): Port number to deallocate
            process_id (str): Process identifier
        """
        if port in self.allocated_ports:
            self.allocated_ports.remove(port)
            if process_id in self.process_port_map and port in self.process_port_map[process_id]:
                self.process_port_map[process_id].remove(port)
                print(f"[TRANSPORT] ▶ Deallocated port {port} from process {process_id}")
    
    def get_process_ports(self, process_id):
        """Get all ports allocated to a process"""
        return self.process_port_map.get(process_id, [])
    
    def is_port_available(self, port):
        """Check if a port is available"""
        return port not in self.allocated_ports

class GoBackNFlowControl:
    """
    Go-Back-N Sliding Window Flow Control Protocol Implementation
    This is a proper implementation of Go-Back-N ARQ for transport layer
    """
    
    def __init__(self, window_size=4, timeout=2.0, max_retries=3):
        self.window_size = window_size
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Sender state variables
        self.send_base = 0  # Oldest unacknowledged sequence number
        self.next_seq_num = 0  # Next sequence number to be sent
        self.send_buffer = {}  # Buffer for sent but unacknowledged segments
        self.timer_start_time = None
        self.is_timer_running = False
        
        # Receiver state variables
        self.expected_seq_num = 0  # Next expected sequence number
        self.last_ack_sent = -1  # Last ACK sent
        
        # Statistics
        self.segments_sent = 0
        self.segments_retransmitted = 0
        self.segments_received = 0
        self.acks_sent = 0
        
        # Use checksum handler for error detection
        self.checksum_handler = ChecksumForDataLink()
        
    def is_in_window(self, seq_num):
        """Check if sequence number is within the current window"""
        return (self.send_base <= seq_num < self.send_base + self.window_size) or \
               (self.send_base > 1000 - self.window_size and 
                (seq_num >= self.send_base or seq_num < (self.send_base + self.window_size) % 1000))
    
    def can_send(self):
        """Check if we can send more segments within the window"""
        window_used = (self.next_seq_num - self.send_base) % 1000
        if window_used < 0:
            window_used += 1000
        return window_used < self.window_size
    
    def send_segment(self, data, seq_num=None):
        """
        Send a segment using Go-Back-N protocol
        
        Args:
            data (str): Data to send
            seq_num (int, optional): Sequence number (auto-assigned if None)
            
        Returns:
            tuple: (success, segment, seq_num)
        """
        if not self.can_send():
            print(f"[GO-BACK-N] ⚠ Cannot send - window full")
            print(f"[GO-BACK-N] ▶ Send base: {self.send_base}, Next seq: {self.next_seq_num}, Window size: {self.window_size}")
            return False, None, None
        
        # Use provided sequence number or assign next
        if seq_num is None:
            seq_num = self.next_seq_num
            
        # Create segment with checksum
        segment = self.checksum_handler.create_frame(data, seq_num)
        
        # Store in send buffer for potential retransmission
        self.send_buffer[seq_num] = {
            'segment': segment,
            'data': data,
            'timestamp': time.time(),
            'retransmit_count': 0
        }
        
        # Start timer if this is the first unacknowledged segment
        if not self.is_timer_running:
            self.start_timer()
            
        self.segments_sent += 1
        print(f"[GO-BACK-N] ▶ Sent segment {seq_num}: '{data[:20]}...' (Total sent: {self.segments_sent})")
        
        # Advance next sequence number if this was the expected next
        if seq_num == self.next_seq_num:
            self.next_seq_num = (self.next_seq_num + 1) % 1000
            
        return True, segment, seq_num
    
    def receive_segment(self, segment):
        """
        Process received segment using Go-Back-N protocol
        
        Args:
            segment (str): Received segment
            
        Returns:
            tuple: (is_valid, seq_num, data, ack_to_send)
        """
        # Verify segment integrity
        is_valid, seq_num, data = self.checksum_handler.verify_frame(segment)
        
        if not is_valid:
            print(f"[GO-BACK-N] ❌ Corrupted segment received - discarding")
            # Send duplicate ACK for last correctly received segment
            if self.last_ack_sent >= 0:
                ack_to_send = f"ACK{self.last_ack_sent}"
                self.acks_sent += 1
                return False, -1, None, ack_to_send
            return False, -1, None, None
        
        self.segments_received += 1
        print(f"[GO-BACK-N] ▶ Received segment {seq_num}: '{data[:20]}...' (Expected: {self.expected_seq_num})")
        
        if seq_num == self.expected_seq_num:
            # This is the expected segment - accept it
            print(f"[GO-BACK-N] ✓ Segment {seq_num} accepted (in order)")
            self.expected_seq_num = (self.expected_seq_num + 1) % 1000
            self.last_ack_sent = seq_num
            ack_to_send = f"ACK{seq_num}"
            self.acks_sent += 1
            print(f"[GO-BACK-N] ▶ Sending {ack_to_send}")
            return True, seq_num, data, ack_to_send
            
        else:
            # Out of order segment - discard and send duplicate ACK
            print(f"[GO-BACK-N] ❌ Out-of-order segment {seq_num} discarded")
            if self.last_ack_sent >= 0:
                ack_to_send = f"ACK{self.last_ack_sent}"
                self.acks_sent += 1
                print(f"[GO-BACK-N] ▶ Sending duplicate {ack_to_send}")
                return False, seq_num, data, ack_to_send
            return False, seq_num, data, None
    
    def process_ack(self, ack):
        """
        Process received ACK using Go-Back-N protocol
        
        Args:
            ack (str): ACK message (e.g., "ACK5")
            
        Returns:
            list: List of acknowledged sequence numbers
        """
        if not ack.startswith("ACK"):
            print(f"[GO-BACK-N] ⚠ Invalid ACK format: {ack}")
            return []
            
        try:
            ack_num = int(ack[3:])
            print(f"[GO-BACK-N] ▶ Processing {ack} (current send_base: {self.send_base})")
            
            # Go-Back-N uses cumulative ACKs
            acked_segments = []
            
            # Calculate which segments are acknowledged
            if ack_num >= self.send_base:
                # Normal case: no wrap-around
                for seq in range(self.send_base, ack_num + 1):
                    if seq in self.send_buffer:
                        acked_segments.append(seq)
            else:
                # Handle sequence number wrap-around
                for seq in range(self.send_base, 1000):
                    if seq in self.send_buffer:
                        acked_segments.append(seq)
                for seq in range(0, ack_num + 1):
                    if seq in self.send_buffer:
                        acked_segments.append(seq)
            
            # Remove acknowledged segments from buffer
            for seq in acked_segments:
                if seq in self.send_buffer:
                    del self.send_buffer[seq]
                    print(f"[GO-BACK-N] ✓ Segment {seq} acknowledged and removed from buffer")
            
            # Update send base to ack_num + 1
            self.send_base = (ack_num + 1) % 1000
            print(f"[GO-BACK-N] ▶ Updated send_base to {self.send_base}")
            
            # Restart timer if there are still unacknowledged segments
            if self.send_buffer:
                self.start_timer()
                print(f"[GO-BACK-N] ▶ Timer restarted - {len(self.send_buffer)} segments still unacknowledged")
            else:
                self.stop_timer()
                print(f"[GO-BACK-N] ✓ All segments acknowledged - timer stopped")
            
            return acked_segments
            
        except Exception as e:
            print(f"[GO-BACK-N] ⚠ Error processing ACK: {e}")
            return []
    
    def handle_timeout(self):
        """
        Handle timeout event - retransmit ALL unacknowledged segments (Go-Back-N behavior)
        
        Returns:
            list: List of segments to retransmit
        """
        if not self.send_buffer:
            return []
            
        print(f"[GO-BACK-N] ⚠ TIMEOUT! Retransmitting all unacknowledged segments")
        
        segments_to_retransmit = []
        current_time = time.time()
        
        # Sort segments by sequence number for retransmission
        sorted_segments = sorted(self.send_buffer.items())
        
        for seq_num, segment_info in sorted_segments:
            if segment_info['retransmit_count'] < self.max_retries:
                segments_to_retransmit.append((seq_num, segment_info['segment'], segment_info['data']))
                segment_info['retransmit_count'] += 1
                segment_info['timestamp'] = current_time
                self.segments_retransmitted += 1
                print(f"[GO-BACK-N] ▶ Retransmitting segment {seq_num} (attempt {segment_info['retransmit_count']})")
            else:
                print(f"[GO-BACK-N] ❌ Segment {seq_num} exceeded max retries - connection may be lost")
        
        # Restart timer
        self.start_timer()
        
        return segments_to_retransmit
    
    def start_timer(self):
        """Start the retransmission timer"""
        self.timer_start_time = time.time()
        self.is_timer_running = True
        
    def stop_timer(self):
        """Stop the retransmission timer"""
        self.is_timer_running = False
        self.timer_start_time = None
        
    def check_timeout(self):
        """Check if timeout has occurred"""
        if not self.is_timer_running or self.timer_start_time is None:
            return False
        return (time.time() - self.timer_start_time) >= self.timeout
    
    def get_window_status(self):
        """Get current window status for debugging"""
        return {
            'send_base': self.send_base,
            'next_seq_num': self.next_seq_num,
            'window_size': self.window_size,
            'unacknowledged_segments': list(self.send_buffer.keys()),
            'expected_seq_num': self.expected_seq_num,
            'last_ack_sent': self.last_ack_sent
        }

    def get_statistics(self):
        """Get protocol statistics"""
        return {
            'segments_sent': self.segments_sent,
            'segments_retransmitted': self.segments_retransmitted,
            'segments_received': self.segments_received,
            'acks_sent': self.acks_sent,
            'window_size': self.window_size,
            'current_send_base': self.send_base,
            'current_next_seq': self.next_seq_num,
            'unacknowledged_count': len(self.send_buffer),
            'expected_seq_num': self.expected_seq_num
        }

class ProcessCommunicationManager:
    """
    Manages process-to-process communication with proper addressing
    """
    
    def __init__(self):
        self.processes = {}  # Maps process_id to ProcessInfo
        self.active_connections = {}  # Maps connection_id to connection details
        self.message_queue = {}  # Per-process message queues
        
    def register_process(self, process_id, process_name, device_ip, protocol_type=ProtocolType.TCP):
        """
        Register a process for communication
        
        Args:
            process_id (str): Unique process identifier
            process_name (str): Human-readable process name
            device_ip (str): IP address of the device hosting the process
            protocol_type (ProtocolType): TCP or UDP
            
        Returns:
            dict: Process information
        """
        process_info = {
            'process_id': process_id,
            'process_name': process_name,
            'device_ip': device_ip,
            'protocol_type': protocol_type,
            'allocated_ports': [],
            'active_connections': [],
            'message_queue': [],
            'registration_time': time.time()
        }
        
        self.processes[process_id] = process_info
        self.message_queue[process_id] = []
        
        print(f"[PROCESS-COMM] ▶ Registered process '{process_name}' (ID: {process_id}) on {device_ip}")
        return process_info
    
    def establish_connection(self, client_process_id, server_process_id, service_port=None):
        """
        Establish connection between two processes
        
        Args:
            client_process_id (str): Client process ID
            server_process_id (str): Server process ID  
            service_port (int, optional): Specific service port
            
        Returns:
            str: Connection ID if successful, None otherwise
        """
        if client_process_id not in self.processes:
            print(f"[PROCESS-COMM] ❌ Client process {client_process_id} not registered")
            return None
            
        if server_process_id not in self.processes:
            print(f"[PROCESS-COMM] ❌ Server process {server_process_id} not registered")
            return None
        
        client_info = self.processes[client_process_id]
        server_info = self.processes[server_process_id]
        
        connection_id = f"{client_process_id}_to_{server_process_id}_{int(time.time())}"
        
        connection_info = {
            'connection_id': connection_id,
            'client_process': client_info,
            'server_process': server_info,
            'client_device_ip': client_info['device_ip'],
            'server_device_ip': server_info['device_ip'],
            'service_port': service_port or 80,
            'established_time': time.time(),
            'state': 'ESTABLISHING'
        }
        
        self.active_connections[connection_id] = connection_info
        
        # Add to process connection lists
        client_info['active_connections'].append(connection_id)
        server_info['active_connections'].append(connection_id)
        
        print(f"[PROCESS-COMM] ▶ Establishing connection: {client_info['process_name']} → {server_info['process_name']}")
        print(f"[PROCESS-COMM] ▶ Connection ID: {connection_id}")
        print(f"[PROCESS-COMM] ▶ Route: {client_info['device_ip']} → {server_info['device_ip']}:{connection_info['service_port']}")
        
        return connection_id
    
    def send_message(self, sender_process_id, receiver_process_id, message, connection_id=None):
        """
        Send message from one process to another
        
        Args:
            sender_process_id (str): Sender process ID
            receiver_process_id (str): Receiver process ID
            message (str): Message to send
            connection_id (str, optional): Existing connection ID
            
        Returns:
            bool: Success status
        """
        if sender_process_id not in self.processes:
            print(f"[PROCESS-COMM] ❌ Sender process {sender_process_id} not registered")
            return False
            
        if receiver_process_id not in self.processes:
            print(f"[PROCESS-COMM] ❌ Receiver process {receiver_process_id} not registered")
            return False
        
        sender_info = self.processes[sender_process_id]
        receiver_info = self.processes[receiver_process_id]
        
        message_info = {
            'message_id': f"msg_{int(time.time() * 1000)}",
            'sender_process': sender_info,
            'receiver_process': receiver_info,
            'message': message,
            'timestamp': time.time(),
            'connection_id': connection_id
        }
        
        # Add to receiver's message queue
        self.message_queue[receiver_process_id].append(message_info)
        
        print(f"[PROCESS-COMM] ▶ Message sent: {sender_info['process_name']} → {receiver_info['process_name']}")
        print(f"[PROCESS-COMM] ▶ Message: '{message[:50]}...' (ID: {message_info['message_id']})")
        
        return True
    
    def receive_message(self, process_id):
        """
        Receive message for a process
        
        Args:
            process_id (str): Process ID
            
        Returns:
            dict: Message info or None if no messages
        """
        if process_id not in self.message_queue:
            return None
            
        if not self.message_queue[process_id]:
            return None
            
        message = self.message_queue[process_id].pop(0)
        print(f"[PROCESS-COMM] ▶ Message delivered to {self.processes[process_id]['process_name']}")
        return message
    
    def get_process_info(self, process_id):
        """Get information about a registered process"""
        return self.processes.get(process_id)
    
    def list_active_processes(self):
        """List all active processes"""
        print(f"[PROCESS-COMM] === ACTIVE PROCESSES ===")
        for process_id, info in self.processes.items():
            print(f"[PROCESS-COMM] ▶ {info['process_name']} (ID: {process_id})")
            print(f"[PROCESS-COMM]   Device: {info['device_ip']}")
            print(f"[PROCESS-COMM]   Protocol: {info['protocol_type'].name}")
            print(f"[PROCESS-COMM]   Ports: {info['allocated_ports']}")
            print(f"[PROCESS-COMM]   Connections: {len(info['active_connections'])}")
            print(f"[PROCESS-COMM]   Pending messages: {len(self.message_queue.get(process_id, []))}")

class SlidingWindowFlowControl:
    """
    Sliding Window Flow Control implementation for Transport Layer
    Reuses and extends the Data Link layer Go-Back-N implementation
    """
    
    def __init__(self, window_size=4, timeout=2.0, max_retries=3):
        self.window_size = window_size
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Sender state
        self.send_base = 0  # Oldest unacknowledged sequence number
        self.next_seq_num = 0  # Next sequence number to use
        self.send_buffer = {}  # Buffer for unacknowledged segments
        self.timer_running = False
        self.retransmission_count = 0
        
        # Receiver state
        self.expected_seq_num = 0  # Next expected sequence number
        self.receive_buffer = {}  # Buffer for received segments
        self.last_ack_sent = -1  # Last ACK sent
        
        # Use checksum handler for error detection
        self.checksum_handler = ChecksumForDataLink()
        
    def can_send(self):
        """Check if we can send more segments within the window"""
        return (self.next_seq_num - self.send_base) < self.window_size
    
    def send_segment(self, data, seq_num=None):
        """
        Send a segment with flow control
        
        Args:
            data (str): Data to send
            seq_num (int, optional): Sequence number (auto-assigned if None)
            
        Returns:
            tuple: (success, segment, seq_num)
        """
        if not self.can_send():
            print(f"[TRANSPORT] ⚠ Cannot send - window full (base={self.send_base}, next={self.next_seq_num}, size={self.window_size})")
            return False, None, None
        
        if seq_num is None:
            seq_num = self.next_seq_num
            
        # Create segment using checksum handler
        segment = self.checksum_handler.create_frame(data, seq_num)
        
        # Store in send buffer
        self.send_buffer[seq_num] = {
            'segment': segment,
            'data': data,
            'timestamp': time.time(),
            'retransmit_count': 0
        }
        
        print(f"[TRANSPORT] ▶ Sending segment {seq_num}: {data}")
        print(f"[TRANSPORT] ▶ Window: base={self.send_base}, next={self.next_seq_num+1}, size={self.window_size}")
        
        # Advance next sequence number
        if seq_num == self.next_seq_num:
            self.next_seq_num = (self.next_seq_num + 1) % 1000  # Use larger sequence space for transport
            
        # Start timer if not running
        if not self.timer_running:
            self.timer_running = True
            
        return True, segment, seq_num
    
    def receive_segment(self, segment):
        """
        Process received segment with flow control
        
        Args:
            segment (str): Received segment
            
        Returns:
            tuple: (is_valid, seq_num, data, ack_to_send)
        """
        # Verify segment using checksum handler
        is_valid, seq_num, data = self.checksum_handler.verify_frame(segment)
        
        if not is_valid:
            print(f"[TRANSPORT] ❌ Invalid segment received")
            # Send duplicate ACK for last correctly received segment
            ack_to_send = f"ACK{self.last_ack_sent}" if self.last_ack_sent >= 0 else None
            return False, -1, None, ack_to_send
        
        print(f"[TRANSPORT] ▶ Received segment {seq_num}: {data}")
        
        if seq_num == self.expected_seq_num:
            # Expected segment - accept it
            print(f"[TRANSPORT] ✓ Segment {seq_num} is in order")
            self.receive_buffer[seq_num] = data
            self.last_ack_sent = seq_num
            self.expected_seq_num = (self.expected_seq_num + 1) % 1000
            
            # Check if we can deliver more segments from buffer
            while self.expected_seq_num in self.receive_buffer:
                delivered_seq = self.expected_seq_num
                print(f"[TRANSPORT] ✓ Delivering buffered segment {delivered_seq}")
                self.expected_seq_num = (self.expected_seq_num + 1) % 1000
            
            ack_to_send = f"ACK{self.last_ack_sent}"
            print(f"[TRANSPORT] ▶ Sending {ack_to_send}")
            return True, seq_num, data, ack_to_send
        
        elif seq_num < self.expected_seq_num:
            # Duplicate segment - send ACK again
            print(f"[TRANSPORT] ⚠ Duplicate segment {seq_num} (expected {self.expected_seq_num})")
            ack_to_send = f"ACK{seq_num}"
            print(f"[TRANSPORT] ▶ Sending duplicate {ack_to_send}")
            return True, seq_num, data, ack_to_send
        
        else:
            # Out-of-order segment - buffer it but don't ACK
            print(f"[TRANSPORT] ⚠ Out-of-order segment {seq_num} (expected {self.expected_seq_num})")
            self.receive_buffer[seq_num] = data
            # Send ACK for last in-order segment
            ack_to_send = f"ACK{self.last_ack_sent}" if self.last_ack_sent >= 0 else None
            return True, seq_num, data, ack_to_send
    
    def process_ack(self, ack):
        """
        Process received ACK
        
        Args:
            ack (str): ACK message (e.g., "ACK5")
            
        Returns:
            list: List of acknowledged sequence numbers
        """
        if not ack.startswith("ACK"):
            print(f"[TRANSPORT] ⚠ Invalid ACK format: {ack}")
            return []
            
        try:
            ack_num = int(ack[3:])
            acked_segments = []
            
            print(f"[TRANSPORT] ▶ Received {ack} (send_base={self.send_base})")
            
            # Cumulative ACK - remove all segments up to ack_num
            segments_to_remove = []
            for seq in self.send_buffer:
                if seq <= ack_num and (ack_num - seq < 500 or seq - ack_num > 500):  # Handle wrap-around
                    segments_to_remove.append(seq)
                    acked_segments.append(seq)
            
            for seq in segments_to_remove:
                del self.send_buffer[seq]
                print(f"[TRANSPORT] ✓ Segment {seq} acknowledged and removed from buffer")
            
            # Update send base
            if acked_segments:
                self.send_base = max(acked_segments) + 1
                print(f"[TRANSPORT] ▶ Updated send_base to {self.send_base}")
                
                # Stop timer if no more unacknowledged segments
                if not self.send_buffer:
                    self.timer_running = False
                    print(f"[TRANSPORT] ▶ All segments acknowledged, stopping timer")
            
            return acked_segments
            
        except Exception as e:
            print(f"[TRANSPORT] ⚠ Error processing ACK: {e}")
            return []
    
    def handle_timeout(self):
        """
        Handle timeout event - retransmit unacknowledged segments
        
        Returns:
            list: List of segments to retransmit
        """
        if not self.send_buffer:
            return []
            
        print(f"[TRANSPORT] ⚠ Timeout occurred - retransmitting unacknowledged segments")
        
        segments_to_retransmit = []
        current_time = time.time()
        
        for seq_num in sorted(self.send_buffer.keys()):
            segment_info = self.send_buffer[seq_num]
            if current_time - segment_info['timestamp'] >= self.timeout:
                if segment_info['retransmit_count'] < self.max_retries:
                    segments_to_retransmit.append((seq_num, segment_info['segment'], segment_info['data']))
                    segment_info['retransmit_count'] += 1
                    segment_info['timestamp'] = current_time
                    print(f"[TRANSPORT] ▶ Retransmitting segment {seq_num} (attempt {segment_info['retransmit_count']})")
                else:
                    print(f"[TRANSPORT] ❌ Segment {seq_num} exceeded max retries, dropping")
                    del self.send_buffer[seq_num]
        
        return segments_to_retransmit
    
    def get_window_status(self):
        """Get current window status for debugging"""
        return {
            'send_base': self.send_base,
            'next_seq_num': self.next_seq_num,
            'window_size': self.window_size,
            'unacknowledged_segments': list(self.send_buffer.keys()),
            'expected_seq_num': self.expected_seq_num,
            'last_ack_sent': self.last_ack_sent
        }
    
    def get_statistics(self):
        """Get protocol statistics"""
        segments_sent = sum(1 for info in self.send_buffer.values() if info['retransmit_count'] >= 0)
        segments_retransmitted = sum(info['retransmit_count'] for info in self.send_buffer.values())
        
        return {
            'segments_sent': segments_sent + (self.next_seq_num - len(self.send_buffer)),
            'segments_retransmitted': segments_retransmitted,
            'segments_received': 0,  # This would be tracked by receiver
            'acks_sent': 0,  # This would be tracked by receiver  
            'window_size': self.window_size,
            'current_send_base': self.send_base,
            'current_next_seq': self.next_seq_num,
            'unacknowledged_count': len(self.send_buffer),
            'expected_seq_num': self.expected_seq_num
        }

class TCPConnection:
    """TCP Connection management"""
    
    def __init__(self, local_port, remote_port, remote_ip, process_id):
        self.local_port = local_port
        self.remote_port = remote_port
        self.remote_ip = remote_ip
        self.process_id = process_id
        self.state = ConnectionState.CLOSED
        self.flow_control = GoBackNFlowControl(window_size=4)  # Use Go-Back-N instead
        
        # TCP-specific sequence numbers
        self.initial_seq_num = random.randint(0, 4294967295)  # 32-bit sequence number
        self.seq_num = self.initial_seq_num
        self.ack_num = 0
        
    def create_tcp_header(self, flags, data_length=0):
        """
        Create TCP header
        
        Args:
            flags (int): TCP flags
            data_length (int): Length of data
            
        Returns:
            str: TCP header string
        """
        # Simplified TCP header representation
        header = (f"SrcPort={self.local_port},"
                 f"DstPort={self.remote_port},"
                 f"Seq={self.seq_num},"
                 f"Ack={self.ack_num},"
                 f"Flags={flags},"
                 f"Window={self.flow_control.window_size},"
                 f"DataLen={data_length}")
        return header
    
    def send_syn(self):
        """Initiate TCP connection (SYN)"""
        self.state = ConnectionState.SYN_SENT
        header = self.create_tcp_header(TCPFlags.SYN)
        segment = f"{header}|"  # No data in SYN
        self.seq_num += 1  # SYN consumes one sequence number
        
        print(f"[TCP] ▶ Sending SYN to {self.remote_ip}:{self.remote_port}")
        print(f"[TCP] ▶ State: {self.state.value}")
        return segment
    
    def process_syn(self, received_segment):
        """Process received SYN"""
        self.state = ConnectionState.SYN_RECEIVED
        # Extract sequence number from received SYN
        # In real implementation, would parse the header
        self.ack_num = self.seq_num + 1  # Acknowledge the SYN
        
        header = self.create_tcp_header(TCPFlags.SYN | TCPFlags.ACK)
        segment = f"{header}|"  # No data in SYN-ACK
        self.seq_num += 1  # SYN consumes one sequence number
        
        print(f"[TCP] ▶ Received SYN, sending SYN-ACK")
        print(f"[TCP] ▶ State: {self.state.value}")
        return segment
    
    def process_syn_ack(self, received_segment):
        """Process received SYN-ACK"""
        self.state = ConnectionState.ESTABLISHED
        self.ack_num += 1  # Acknowledge the SYN-ACK
        
        header = self.create_tcp_header(TCPFlags.ACK)
        segment = f"{header}|"  # No data in ACK
        
        print(f"[TCP] ▶ Received SYN-ACK, sending ACK")
        print(f"[TCP] ▶ Connection established!")
        print(f"[TCP] ▶ State: {self.state.value}")
        return segment
    
    def send_data(self, data):
        """
        Send data over established TCP connection
        
        Args:
            data (str): Data to send
            
        Returns:
            tuple: (success, segments)
        """
        if self.state != ConnectionState.ESTABLISHED:
            print(f"[TCP] ❌ Cannot send data - connection not established (state: {self.state.value})")
            return False, []
        
        # Split data into segments if too large
        max_segment_size = 20  # Simplified MSS
        segments = []
        
        for i in range(0, len(data), max_segment_size):
            segment_data = data[i:i+max_segment_size]
            
            # Use flow control to send
            success, segment, seq_num = self.flow_control.send_segment(segment_data)
            if success:
                # Add TCP header
                header = self.create_tcp_header(TCPFlags.PSH | TCPFlags.ACK, len(segment_data))
                tcp_segment = f"{header}|{segment}"
                segments.append(tcp_segment)
                self.seq_num += len(segment_data)
            else:
                print(f"[TCP] ⚠ Flow control prevented sending segment")
                break
        
        return len(segments) > 0, segments

class UDPSocket:
    """UDP Socket implementation"""
    
    def __init__(self, local_port, process_id):
        self.local_port = local_port
        self.process_id = process_id
        
    def create_udp_header(self, remote_port, data_length):
        """
        Create UDP header
        
        Args:
            remote_port (int): Destination port
            data_length (int): Length of data
            
        Returns:
            str: UDP header string
        """
        # Simplified UDP header
        header = (f"SrcPort={self.local_port},"
                 f"DstPort={remote_port},"
                 f"Length={data_length + 8},"  # 8 bytes for UDP header
                 f"Checksum=0")  # Simplified - no checksum calculation
        return header
    
    def send_datagram(self, data, remote_ip, remote_port):
        """
        Send UDP datagram
        
        Args:
            data (str): Data to send
            remote_ip (str): Destination IP
            remote_port (int): Destination port
            
        Returns:
            str: UDP datagram
        """
        header = self.create_udp_header(remote_port, len(data))
        datagram = f"{header}|{data}"
        
        print(f"[UDP] ▶ Sending datagram to {remote_ip}:{remote_port}")
        print(f"[UDP] ▶ Data: {data}")
        return datagram

class TransportLayer:
    """
    Enhanced Transport Layer class with proper process management and Go-Back-N flow control
    """
    
    def __init__(self):
        self.port_manager = PortManager()
        self.tcp_connections = {}  # Maps (local_port, remote_ip, remote_port) to TCPConnection
        self.udp_sockets = {}  # Maps local_port to UDPSocket
        self.process_registry = {}  # Maps process_id to protocol info
        self.process_comm_manager = ProcessCommunicationManager()  # New process communication manager
        
    def register_process(self, process_id, protocol_type, well_known_port=None, process_name=None, device_ip=None):
        """
        Enhanced process registration with communication management
        
        Args:
            process_id (str): Process identifier
            protocol_type (ProtocolType): TCP or UDP
            well_known_port (int, optional): Well-known port for services
            process_name (str, optional): Human-readable process name
            device_ip (str, optional): IP address of hosting device
            
        Returns:
            int: Allocated port number
        """
        # Allocate port
        if well_known_port:
            success = self.port_manager.allocate_well_known_port(well_known_port, process_id)
            if not success:
                return None
            allocated_port = well_known_port
        else:
            allocated_port = self.port_manager.allocate_ephemeral_port(process_id)
            if not allocated_port:
                return None
        
        # Register in process registry
        self.process_registry[process_id] = {
            'protocol': protocol_type,
            'port': allocated_port,
            'process_name': process_name or process_id,
            'device_ip': device_ip
        }
        
        # Register in communication manager
        if device_ip:
            self.process_comm_manager.register_process(
                process_id, 
                process_name or process_id, 
                device_ip, 
                protocol_type
            )
            self.process_comm_manager.processes[process_id]['allocated_ports'].append(allocated_port)
        
        print(f"[TRANSPORT] ▶ Enhanced registration: {process_name or process_id} ({protocol_type.name}) on port {allocated_port}")
        return allocated_port
    
    def create_tcp_connection(self, process_id, remote_ip, remote_port):
        """
        Create TCP connection (client-side)
        
        Args:
            process_id (str): Process identifier
            remote_ip (str): Remote IP address
            remote_port (int): Remote port
            
        Returns:
            TCPConnection: TCP connection object
        """
        if process_id not in self.process_registry:
            print(f"[TRANSPORT] ❌ Process {process_id} not registered")
            return None
            
        process_info = self.process_registry[process_id]
        if process_info['protocol'] != ProtocolType.TCP:
            print(f"[TRANSPORT] ❌ Process {process_id} not registered for TCP")
            return None
        
        local_port = process_info['port']
        connection_key = (local_port, remote_ip, remote_port)
        
        if connection_key in self.tcp_connections:
            print(f"[TRANSPORT] ⚠ Connection already exists")
            return self.tcp_connections[connection_key]
        
        connection = TCPConnection(local_port, remote_port, remote_ip, process_id)
        self.tcp_connections[connection_key] = connection
        
        print(f"[TRANSPORT] ▶ Created TCP connection: {local_port} → {remote_ip}:{remote_port}")
        return connection
    
    def create_udp_socket(self, process_id):
        """
        Create UDP socket
        
        Args:
            process_id (str): Process identifier
            
        Returns:
            UDPSocket: UDP socket object
        """
        if process_id not in self.process_registry:
            print(f"[TRANSPORT] ❌ Process {process_id} not registered")
            return None
            
        process_info = self.process_registry[process_id]
        if process_info['protocol'] != ProtocolType.UDP:
            print(f"[TRANSPORT] ❌ Process {process_id} not registered for UDP")
            return None
        
        local_port = process_info['port']
        
        if local_port in self.udp_sockets:
            print(f"[TRANSPORT] ⚠ UDP socket already exists on port {local_port}")
            return self.udp_sockets[local_port]
        
        socket = UDPSocket(local_port, process_id)
        self.udp_sockets[local_port] = socket
        
        print(f"[TRANSPORT] ▶ Created UDP socket on port {local_port}")
        return socket
    
    def establish_tcp_connection(self, client_process_id, server_ip, server_port):
        """
        Perform TCP three-way handshake
        
        Args:
            client_process_id (str): Client process ID
            server_ip (str): Server IP address
            server_port (int): Server port
            
        Returns:
            bool: True if connection established successfully
        """
        print(f"[TRANSPORT] === TCP THREE-WAY HANDSHAKE ===")
        
        # Create client connection
        connection = self.create_tcp_connection(client_process_id, server_ip, server_port)
        if not connection:
            return False
        
        # Step 1: Client sends SYN
        syn_segment = connection.send_syn()
        print(f"[TRANSPORT] ▶ Step 1: Client → Server SYN")
        
        # Simulate network delay
        time.sleep(0.1)
        
        # Step 2: Server responds with SYN-ACK (simulated)
        print(f"[TRANSPORT] ▶ Step 2: Server → Client SYN-ACK")
        syn_ack_segment = connection.process_syn(syn_segment)
        
        # Simulate network delay
        time.sleep(0.1)
        
        # Step 3: Client sends ACK
        print(f"[TRANSPORT] ▶ Step 3: Client → Server ACK")
        ack_segment = connection.process_syn_ack(syn_ack_segment)
        
        print(f"[TRANSPORT] ✓ TCP connection established successfully")
        return True
    
    def send_tcp_data(self, process_id, remote_ip, remote_port, data):
        """
        Send data over TCP connection
        
        Args:
            process_id (str): Process identifier
            remote_ip (str): Remote IP
            remote_port (int): Remote port
            data (str): Data to send
            
        Returns:
            tuple: (success, segments)
        """
        if process_id not in self.process_registry:
            print(f"[TRANSPORT] ❌ Process {process_id} not registered")
            return False, []
        
        local_port = self.process_registry[process_id]['port']
        connection_key = (local_port, remote_ip, remote_port)
        
        if connection_key not in self.tcp_connections:
            print(f"[TRANSPORT] ❌ No TCP connection found for {connection_key}")
            return False, []
        
        connection = self.tcp_connections[connection_key]
        success, segments = connection.send_data(data)
        
        if success:
            print(f"[TRANSPORT] ✓ Sent {len(segments)} TCP segments")
            for i, segment in enumerate(segments):
                print(f"[TRANSPORT] ▶ Segment {i+1}: {segment[:50]}...")
        
        return success, segments
    
    def send_udp_data(self, process_id, remote_ip, remote_port, data):
        """
        Send data via UDP
        
        Args:
            process_id (str): Process identifier
            remote_ip (str): Remote IP
            remote_port (int): Remote port
            data (str): Data to send
            
        Returns:
            str: UDP datagram
        """
        if process_id not in self.process_registry:
            print(f"[TRANSPORT] ❌ Process {process_id} not registered")
            return None
        
        local_port = self.process_registry[process_id]['port']
        
        if local_port not in self.udp_sockets:
            socket = self.create_udp_socket(process_id)
            if not socket:
                return None
        else:
            socket = self.udp_sockets[local_port]
        
        datagram = socket.send_datagram(data, remote_ip, remote_port)
        print(f"[TRANSPORT] ✓ Sent UDP datagram")
        return datagram
    
    def display_port_allocation(self):
        """Display current port allocation status"""
        print(f"\n[TRANSPORT] === PORT ALLOCATION STATUS ===")
        print(f"[TRANSPORT] ▶ Total allocated ports: {len(self.port_manager.allocated_ports)}")
        
        for process_id, ports in self.port_manager.process_port_map.items():
            protocol = self.process_registry.get(process_id, {}).get('protocol', 'UNKNOWN')
            protocol_name = protocol.name if hasattr(protocol, 'name') else str(protocol)
            print(f"[TRANSPORT] ▶ Process {process_id} ({protocol_name}): ports {ports}")
        
        print(f"[TRANSPORT] ▶ Active TCP connections: {len(self.tcp_connections)}")
        print(f"[TRANSPORT] ▶ Active UDP sockets: {len(self.udp_sockets)}")
    
    def cleanup_process(self, process_id):
        """
        Clean up resources for a process
        
        Args:
            process_id (str): Process identifier
        """
        if process_id not in self.process_registry:
            return
        
        # Deallocate ports
        ports = self.port_manager.get_process_ports(process_id)
        for port in ports:
            self.port_manager.deallocate_port(port, process_id)
        
        # Close TCP connections
        connections_to_remove = []
        for conn_key, connection in self.tcp_connections.items():
            if connection.process_id == process_id:
                connections_to_remove.append(conn_key)
        
        for conn_key in connections_to_remove:
            del self.tcp_connections[conn_key]
        
        # Remove UDP sockets
        process_port = self.process_registry[process_id]['port']
        if process_port in self.udp_sockets:
            del self.udp_sockets[process_port]
        
        # Remove from registry
        del self.process_registry[process_id]
        
        print(f"[TRANSPORT] ▶ Cleaned up resources for process {process_id}")
    
    def establish_process_connection(self, client_process_id, server_process_id, service_port=None):
        """
        Establish connection between two processes
        
        Args:
            client_process_id (str): Client process ID
            server_process_id (str): Server process ID
            service_port (int, optional): Service port
            
        Returns:
            str: Connection ID if successful
        """
        connection_id = self.process_comm_manager.establish_connection(
            client_process_id, server_process_id, service_port
        )
        
        if connection_id:
            # Also create TCP connection if using TCP
            client_info = self.process_registry.get(client_process_id)
            server_info = self.process_registry.get(server_process_id)
            
            if client_info and server_info and client_info['protocol'] == ProtocolType.TCP:
                server_device_ip = server_info.get('device_ip')
                if server_device_ip:
                    tcp_connection = self.create_tcp_connection(
                        client_process_id, 
                        server_device_ip, 
                        service_port or 80
                    )
                    if tcp_connection:
                        print(f"[TRANSPORT] ✓ TCP connection layer established for process connection")
        
        return connection_id
    
    def send_process_message(self, sender_process_id, receiver_process_id, message, use_flow_control=True):
        """
        Send message between processes with optional flow control
        
        Args:
            sender_process_id (str): Sender process ID
            receiver_process_id (str): Receiver process ID
            message (str): Message to send
            use_flow_control (bool): Whether to use Go-Back-N flow control
            
        Returns:
            bool: Success status
        """
        # Register message in communication manager
        success = self.process_comm_manager.send_message(
            sender_process_id, receiver_process_id, message
        )
        
        if success and use_flow_control:
            # Also demonstrate Go-Back-N flow control
            sender_info = self.process_registry.get(sender_process_id)
            if sender_info and sender_info['protocol'] == ProtocolType.TCP:
                print(f"[TRANSPORT] ▶ Using Go-Back-N flow control for reliable delivery")
                
                # Find existing TCP connection
                connection_key = None
                for key, conn in self.tcp_connections.items():
                    if conn.process_id == sender_process_id:
                        connection_key = key
                        break
                
                if connection_key:
                    connection = self.tcp_connections[connection_key]
                    # Simulate sending with Go-Back-N
                    flow_success, segments = connection.send_data(message)
                    if flow_success:
                        print(f"[TRANSPORT] ✓ Message sent with Go-Back-N reliability guarantees")
                        # Show flow control statistics
                        stats = connection.flow_control.get_statistics()
                        print(f"[TRANSPORT] ▶ Flow control stats: {stats}")
        
        return success
    
    def receive_process_message(self, process_id):
        """
        Receive message for a process
        
        Args:
            process_id (str): Process ID
            
        Returns:
            dict: Message information or None
        """
        return self.process_comm_manager.receive_message(process_id)
    
    def demonstrate_go_back_n(self, connection_id, test_data_list, simulate_errors=True):
        """
        Demonstrate Go-Back-N protocol with multiple segments
        
        Args:
            connection_id (str): TCP connection identifier  
            test_data_list (list): List of data segments to send
            simulate_errors (bool): Whether to simulate transmission errors
            
        Returns:
            dict: Demonstration results
        """
        print(f"\n[GO-BACK-N DEMO] === DEMONSTRATING GO-BACK-N PROTOCOL ===")
        
        # Find the TCP connection
        tcp_connection = None
        for conn in self.tcp_connections.values():
            if hasattr(conn, 'connection_id') and conn.connection_id == connection_id:
                tcp_connection = conn
                break
        
        if not tcp_connection:
            # Create a demo connection
            tcp_connection = TCPConnection(12345, 80, "192.168.1.10", "demo_process")
            tcp_connection.state = ConnectionState.ESTABLISHED
        
        flow_control = tcp_connection.flow_control
        results = {
            'segments_sent': 0,
            'segments_acknowledged': 0,
            'retransmissions': 0,
            'final_statistics': {}
        }
        
        print(f"[GO-BACK-N DEMO] Window size: {flow_control.window_size}")
        print(f"[GO-BACK-N DEMO] Timeout: {flow_control.timeout}s")
        
        # Send all segments
        for i, data in enumerate(test_data_list):
            success, segment, seq_num = flow_control.send_segment(data)
            if success:
                results['segments_sent'] += 1
                print(f"[GO-BACK-N DEMO] Sent: {data}")
                
                # Simulate some ACKs (not all to demonstrate retransmission)
                if not simulate_errors or i % 3 != 1:  # Skip every 3rd ACK to simulate loss
                    # Simulate ACK reception
                    ack = f"ACK{seq_num}"
                    acked_segments = flow_control.process_ack(ack)
                    results['segments_acknowledged'] += len(acked_segments)
            else:
                print(f"[GO-BACK-N DEMO] Cannot send: {data} (window full)")
        
        # Simulate timeout and retransmission
        if simulate_errors:
            print(f"[GO-BACK-N DEMO] Simulating timeout...")
            flow_control.timer_start_time = time.time() - flow_control.timeout - 1  # Force timeout
            if flow_control.check_timeout():
                retransmit_list = flow_control.handle_timeout()
                results['retransmissions'] = len(retransmit_list)
                print(f"[GO-BACK-N DEMO] Retransmitted {len(retransmit_list)} segments")
        
        # Get final statistics
        results['final_statistics'] = flow_control.get_statistics()
        
        print(f"[GO-BACK-N DEMO] === DEMONSTRATION COMPLETE ===")
        print(f"[GO-BACK-N DEMO] Results: {results}")
        
        return results
    
    def display_enhanced_status(self):
        """Display comprehensive transport layer status"""
        print(f"\n[TRANSPORT] === ENHANCED TRANSPORT LAYER STATUS ===")
        
        # Port allocation status
        self.display_port_allocation()
        
        # Process communication status
        self.process_comm_manager.list_active_processes()
        
        # Connection status
        print(f"[TRANSPORT] === CONNECTION STATUS ===")
        print(f"[TRANSPORT] ▶ Active TCP connections: {len(self.tcp_connections)}")
        for conn_key, connection in self.tcp_connections.items():
            print(f"[TRANSPORT]   {conn_key}: State={connection.state.value}")
            if hasattr(connection.flow_control, 'get_statistics'):
                stats = connection.flow_control.get_statistics()
                print(f"[TRANSPORT]   Flow Control: {stats}")
        
        print(f"[TRANSPORT] ▶ Active UDP sockets: {len(self.udp_sockets)}")
        
        # Active connections from communication manager
        print(f"[TRANSPORT] ▶ Process connections: {len(self.process_comm_manager.active_connections)}")
        for conn_id, conn_info in self.process_comm_manager.active_connections.items():
            client_name = conn_info['client_process']['process_name']
            server_name = conn_info['server_process']['process_name']
            print(f"[TRANSPORT]   {conn_id}: {client_name} → {server_name}")
    
    def register_device(self, device_name, device_ip, device_mac):
        """
        Register a device with the transport layer
        
        Args:
            device_name (str): Device name
            device_ip (str): Device IP address
            device_mac (str): Device MAC address
        """
        if not hasattr(self, 'registered_devices'):
            self.registered_devices = {}
        
        self.registered_devices[device_name] = {
            'ip': device_ip,
            'mac': device_mac,
            'processes': []
        }
        
        print(f"[TRANSPORT] ▶ Registered device: {device_name} (IP: {device_ip}, MAC: {device_mac})")
    
    def get_process_by_port(self, port):
        """
        Get process information by port number
        
        Args:
            port (int): Port number
            
        Returns:
            dict: Process information or None if not found
        """
        for process_id, process_info in self.process_registry.items():
            if process_info['port'] == port:
                return {
                    'process_id': process_id,
                    'process_name': process_info.get('process_name', process_id),
                    'protocol': process_info['protocol'],
                    'device_ip': process_info.get('device_ip')
                }
        return None
