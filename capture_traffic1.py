import os
import scapy.all as scapy
from scapy.all import IP, TCP
from scapy.all import *
import pandas as pd
import time
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
import socket

def extract_features(packet):
    features = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'), 'srcIP': '',
        'destIP': '', 'protocol': '', 'srcPort': 0, 'destPort': 0, 'packetSize': 0, 'ttl': 0,
        'duration': 0, 'protocol_type': '', 'service': '', 'flag': '',
        'src_bytes': 0, 'dst_bytes': 0, 'land': 0, 'wrong_fragment': 0,
        'urgent': 0, 'hot': 0, 'num_failed_logins': 0, 'logged_in': 0,
        'num_compromised': 0, 'root_shell': 0, 'su_attempted': 0, 'num_root': 0,
        'num_file_creations': 0, 'num_shells': 0, 'num_access_files': 0,
        'num_outbound_cmds': 0, 'is_host_login': 0, 'is_guest_login': 0,
        'count': 0, 'srv_count': 0, 'serror_rate': 0, 'srv_serror_rate': 0,
        'rerror_rate': 0, 'srv_rerror_rate': 0, 'same_srv_rate': 0,
        'diff_srv_rate': 0, 'srv_diff_host_rate': 0, 'dst_host_count': 0,
        'dst_host_srv_count': 0, 'dst_host_same_srv_rate': 0,
        'dst_host_diff_srv_rate': 0, 'dst_host_same_src_port_rate': 0,
        'dst_host_srv_diff_host_rate': 0, 'dst_host_serror_rate': 0,
        'dst_host_srv_serror_rate': 0, 'dst_host_rerror_rate': 0,
        'dst_host_srv_rerror_rate': 0, 'details': " "
    }
    
    if packet.haslayer(scapy.IP):
        features['protocol_type'] = packet[scapy.IP].proto
        features['src_bytes'] = len(packet[scapy.IP])
        features['dst_bytes'] = len(packet[scapy.IP].payload)
    
    if packet.haslayer(scapy.TCP):
        features['service'] = packet[scapy.TCP].dport
        features['flag'] = packet[scapy.TCP].flags
    
    return features

captured_traffic = []

# Function to get the local device IP
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even even have to be reachable
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
    except:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

# Function to capture live network traffic and extract the features
def capture_traffic(target_ip=None):
    def packet_callback(packet):
        if packet.haslayer('IP'): # Check if the packet has an IP layer
            if target_ip:
                if packet[IP].src != target_ip and packet[IP].dst != target_ip:
                    return  # Skip packet if it doesn't match the target IP
            traffic_data = {
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "srcIP": packet[1].src,  # Source IP
                "destIP": packet[1].dst,  # Destination IP
                "protocol": packet[1].proto,  # Protocol (TCP, UDP, etc.)
                "srcPort": packet[2].sport if packet.haslayer('TCP') or packet.haslayer('UDP') else None,
                "destPort": packet[2].dport if packet.haslayer('TCP') or packet.haslayer('UDP') else None,
                "packetSize": len(packet),
                "ttl": packet[1].ttl,  # Time-To-Live
                'duration': 0,  # Duration can be derived if you track the session
                'protocol_type': packet[IP].proto,  # IP protocol type (e.g., TCP, UDP)
                'service': '',  # Inferred from ports (example: port 80 -> HTTP)
                'flag': packet.sprintf('%TCP.flags%'),  # TCP flags (SYN, ACK, etc.)
                'src_bytes': len(packet),  # Payload size
                'dst_bytes': len(packet),  # Payload size for response (if available)
                'land': 1 if packet[IP].src == packet[IP].dst else 0,  # Land attack check
                'wrong_fragment': 0,  # To check for wrong fragments (not implemented)
                'urgent': 1 if packet.haslayer('TCP') and packet[TCP].flags == 'U' else 0,  # Urgent flag
                'hot': 0,  # Custom heuristics based (not implemented)
                'num_failed_logins': 0,  # Can be derived from failed login traffic
                'logged_in': 0,  # Can be inferred from successful login traffic
                'num_compromised': 0,  # Detect compromised traffic (custom detection)
                'root_shell': 0,  # Can be inferred from specific traffic
                'su_attempted': 0,  # If SU command is detected
                'num_root': 0,  # Root-level processes detected
                'num_file_creations': 0,  # File creation event detection
                'num_shells': 0,  # Detect shell command invocations
                'num_access_files': 0,  # Files accessed detected
                'num_outbound_cmds': 0,  # Outbound commands detected
                'is_host_login': 0,  # Host login based on source IP
                'is_guest_login': 0,  # Guest login detection
                'count': 0,  # Total packet count (per session)
                'srv_count': 0,  # Server response packet count
                'serror_rate': 0,  # Calculate error rate (e.g., 4xx, 5xx errors)
                'srv_serror_rate': 0,  # Server error rate
                'rerror_rate': 0,  # Client-side error rate
                'srv_rerror_rate': 0,  # Server-side error rate for client
                'same_srv_rate': 0,  # Rate of connections to the same service
                'diff_srv_rate': 0,  # Rate of connections to different services
                'srv_diff_host_rate': 0,  # Rate of server connections to different hosts
                'dst_host_count': 0,  # Number of connections to destination host
                'dst_host_srv_count': 0,  # Number of connections to destination service
                'dst_host_same_srv_rate': 0,  # Connections to the same service at destination
                'dst_host_diff_srv_rate': 0,  # Connections to different services at destination
                'dst_host_same_src_port_rate': 0,  # Same source port rate to destination
                'dst_host_srv_diff_host_rate': 0,  # Different host rate for destination services
                'dst_host_serror_rate': 0,  # Destination error rate
                'dst_host_srv_serror_rate': 0,  # Server-side destination error rate
                'dst_host_rerror_rate': 0,  # Destination host client-side error rate
                'dst_host_srv_rerror_rate': 0,  # Destination server-side error rate
                "details": f"Captured {packet.summary()}"
            }

            # Append the captured data to the list
            captured_traffic.append(traffic_data)

    # Start sniffing network traffic
    sniff(prn=packet_callback, store=0, filter="ip")  # Filter for IP packets

def save_traffic_data():
    if not captured_traffic:
        return {"message": "No data to save!"}
    
    save_dir = "saved_data"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f"traffic_{timestamp}.csv"
    file_path = os.path.join(save_dir, file_name)
    
    df = pd.DataFrame(captured_traffic)
    df.to_csv(file_path, index=False)
    
    return {"message": f"Data saved as {file_name}"}

def run_flask_server():
    app = Flask(__name__)
    CORS(app)
    
    @app.route("/api/live-traffic", methods=["GET"])
    def live_traffic():
        target_ip = request.args.get('targetIp')  # Get the target IP from query parameter
        if target_ip:
            # Filter captured traffic for the given target IP
            filtered_traffic = [traffic for traffic in captured_traffic if traffic['src_ip'] == target_ip or traffic['dst_ip'] == target_ip]
            return jsonify(filtered_traffic[-1] if filtered_traffic else {"message": "No traffic captured for this IP"})
        else:
            return jsonify(captured_traffic[-1] if captured_traffic else {"message": "No traffic captured yet"})
        
    @app.route("/api/save-traffic", methods=["POST"])
    def save_traffic():
        result = save_traffic_data()
        return jsonify(result)
    
    app.run(debug=False, port=5003)

def start_traffic_monitoring():
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()
    
    target_ip = None
    capture_thread = threading.Thread(target=capture_traffic, args=(target_ip,), daemon=True)
    capture_thread.start()

