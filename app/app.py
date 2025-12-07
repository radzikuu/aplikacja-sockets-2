"""
app.py - Flask backend do obsługi API i WebUI
"""

from flask import Flask, render_template, request, jsonify
import logging
import threading
from tcp_server import TCPServer
from udp_server import UDPServer
from tcp_client import TCPClient
from udp_client import UDPClient
from load_tester import LoadTester
from host_discovery import HostDiscovery

# Konfiguracja loggingu
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicjalizacja Flask
app = Flask(__name__)

# Globalne obiekty
tcp_server = None
udp_server = None
tcp_client = None
udp_client = None
load_tester = None
host_discovery = HostDiscovery()

# Config
CONFIG = {
    'tcp_server_host': '0.0.0.0',
    # TCP server must not collide with Flask port (5000). Use 6000 by default.
    'tcp_server_port': 6000,
    'tcp_server_max_clients': 10,
    'udp_server_host': '0.0.0.0',
    'udp_server_port': 5001,
    'udp_server_buffer': 65535,
    'tcp_client_host': 'localhost',
    # TCP client default should match the TCP server default when running locally
    'tcp_client_port': 6000,
    'tcp_client_auto_reconnect': True,
}

# ==================== STATIC ROUTES ====================

@app.route('/')
def index():
    """Główna strona"""
    return render_template('index.html')

# ==================== TCP SERVER API ====================

@app.route('/api/tcp-server/start', methods=['POST'])
def start_tcp_server():
    global tcp_server
    
    data = request.json
    host = data.get('host', CONFIG['tcp_server_host'])
    port = int(data.get('port', CONFIG['tcp_server_port']))
    max_clients = int(data.get('max_clients', CONFIG['tcp_server_max_clients']))
    
    if tcp_server and tcp_server.running:
        return jsonify({'success': False, 'message': 'TCP Server już uruchomiony'}), 400
    
    tcp_server = TCPServer(host, port, max_clients)
    success = tcp_server.start()
    
    if success:
        return jsonify({'success': True, 'message': f'TCP Server uruchomiony na {host}:{port}'})
    else:
        return jsonify({'success': False, 'message': 'Błąd uruchamiania TCP Server'}), 500

@app.route('/api/tcp-server/stop', methods=['POST'])
def stop_tcp_server():
    global tcp_server
    
    if tcp_server:
        tcp_server.stop()
    
    return jsonify({'success': True, 'message': 'TCP Server zatrzymany'})

@app.route('/api/tcp-server/stats', methods=['GET'])
def tcp_server_stats():
    if tcp_server:
        return jsonify(tcp_server.get_stats())
    return jsonify({})

# ==================== UDP SERVER API ====================

@app.route('/api/udp-server/start', methods=['POST'])
def start_udp_server():
    global udp_server
    
    data = request.json
    host = data.get('host', CONFIG['udp_server_host'])
    port = int(data.get('port', CONFIG['udp_server_port']))
    buffer_size = int(data.get('buffer_size', CONFIG['udp_server_buffer']))
    
    if udp_server and udp_server.running:
        return jsonify({'success': False, 'message': 'UDP Server już uruchomiony'}), 400
    
    udp_server = UDPServer(host, port, buffer_size)
    success = udp_server.start()
    
    if success:
        return jsonify({'success': True, 'message': f'UDP Server uruchomiony na {host}:{port}'})
    else:
        return jsonify({'success': False, 'message': 'Błąd uruchamiania UDP Server'}), 500

@app.route('/api/udp-server/stop', methods=['POST'])
def stop_udp_server():
    global udp_server
    
    if udp_server:
        udp_server.stop()
    
    return jsonify({'success': True, 'message': 'UDP Server zatrzymany'})

@app.route('/api/udp-server/stats', methods=['GET'])
def udp_server_stats():
    if udp_server:
        return jsonify(udp_server.get_stats())
    return jsonify({})

# ==================== TCP CLIENT API ====================

@app.route('/api/tcp-client/connect', methods=['POST'])
def tcp_client_connect():
    global tcp_client
    
    data = request.json
    host = data.get('host', CONFIG['tcp_client_host'])
    port = int(data.get('port', CONFIG['tcp_client_port']))
    auto_reconnect = data.get('auto_reconnect', CONFIG['tcp_client_auto_reconnect'])
    
    tcp_client = TCPClient(host, port, auto_reconnect)
    success = tcp_client.connect()
    
    if success:
        return jsonify({'success': True, 'message': f'Połączono z {host}:{port}'})
    else:
        return jsonify({'success': False, 'message': 'Błąd połączenia'}), 500

@app.route('/api/tcp-client/send', methods=['POST'])
def tcp_client_send():
    global tcp_client
    
    if not tcp_client:
        return jsonify({'success': False, 'message': 'Brak połączenia'}), 400
    
    data = request.json
    message = data.get('message', '')
    
    success = tcp_client.send_message(message)
    
    if success:
        return jsonify({'success': True, 'message': 'Wysłano'})
    else:
        return jsonify({'success': False, 'message': 'Błąd wysyłania'}), 500

@app.route('/api/tcp-client/disconnect', methods=['POST'])
def tcp_client_disconnect():
    global tcp_client
    
    if tcp_client:
        tcp_client.disconnect()
    
    return jsonify({'success': True, 'message': 'Rozłączono'})

@app.route('/api/tcp-client/stats', methods=['GET'])
def tcp_client_stats():
    if tcp_client:
        return jsonify(tcp_client.get_stats())
    return jsonify({})

# ==================== UDP CLIENT API ====================

@app.route('/api/udp-client/send', methods=['POST'])
def udp_client_send():
    global udp_client
    
    data = request.json
    host = data.get('host', CONFIG['tcp_client_host'])
    port = int(data.get('port', 5001))
    message = data.get('message', '')
    mode = data.get('mode', 'unicast')
    
    if not udp_client or udp_client.host != host or udp_client.port != port:
        udp_client = UDPClient(host, port)
    # Choose unicast or multicast send
    try:
        message_bytes = message.encode('utf-8')
        if mode == 'multicast':
            success = udp_client.send_multicast(message_bytes)
        else:
            success = udp_client.send_message(message)
    except Exception as e:
        success = False
    
    if success:
        return jsonify({'success': True, 'message': 'Wysłano', 'stats': udp_client.get_stats()})
    else:
        return jsonify({'success': False, 'message': 'Błąd wysyłania'}), 500

@app.route('/api/udp-client/send-file', methods=['POST'])
def udp_client_send_file():
    global udp_client
    
    data = request.json
    host = data.get('host', CONFIG['tcp_client_host'])
    port = int(data.get('port', 5001))
    file_base64 = data.get('file_data', '')
    mode = data.get('mode', 'unicast')
    
    if not udp_client or udp_client.host != host or udp_client.port != port:
        udp_client = UDPClient(host, port)
    
    import base64
    try:
        file_data = base64.b64decode(file_base64)
        if mode == 'multicast':
            success = udp_client.send_multicast(file_data)
        else:
            success = udp_client.send_binary(file_data)
        
        if success:
            return jsonify({'success': True, 'message': 'Plik wysłany', 'stats': udp_client.get_stats()})
        else:
            return jsonify({'success': False, 'message': 'Błąd wysyłania pliku'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Błąd: {str(e)}'}), 500

# ==================== LOAD TESTER API ====================

@app.route('/api/load-tester/start', methods=['POST'])
def start_load_test():
    global load_tester
    
    data = request.json
    host = data.get('host', 'localhost')
    port = int(data.get('port', 5000))
    mode = data.get('mode', 'normal')
    num_threads = int(data.get('num_threads', 5))
    packets_per_thread = int(data.get('packets_per_thread', 10))
    packet_size = int(data.get('packet_size', 1024))
    packet_delay = int(data.get('packet_delay', 10))
    
    if not load_tester:
        load_tester = LoadTester(host, port)
    
    success = load_tester.start_test(mode, num_threads, packets_per_thread, packet_size, packet_delay)
    
    if success:
        return jsonify({'success': True, 'message': f'Test {mode} uruchomiony'})
    else:
        return jsonify({'success': False, 'message': 'Błąd uruchamiania testu'}), 500

@app.route('/api/load-tester/stop', methods=['POST'])
def stop_load_test():
    global load_tester
    
    if load_tester:
        load_tester.stop_test()
    
    return jsonify({'success': True, 'message': 'Test zatrzymany'})

@app.route('/api/load-tester/stats', methods=['GET'])
def load_tester_stats():
    if load_tester:
        return jsonify(load_tester.get_stats())
    return jsonify({})

# ==================== HOST DISCOVERY API ====================

@app.route('/api/discovery/scan', methods=['POST'])
def scan_network():
    data = request.json
    cidr = data.get('cidr', '172.17.0.0/16')
    
    hosts = host_discovery.scan_network(cidr)
    return jsonify({'success': True, 'hosts': hosts})

@app.route('/api/discovery/hosts', methods=['GET'])
def get_discovered_hosts():
    hosts = host_discovery.get_discovered_hosts()
    return jsonify({'hosts': hosts})

@app.route('/api/discovery/add-manual', methods=['POST'])
def add_manual_host():
    data = request.json
    ip = data.get('ip')
    name = data.get('name', ip)
    
    success = host_discovery.add_manual_host(ip, name)
    
    if success:
        return jsonify({'success': True, 'message': f'Host {name} dodany'})
    else:
        return jsonify({'success': False, 'message': 'Host już istnieje'}), 400

@app.route('/api/discovery/check-status/<ip>', methods=['GET'])
def check_host_status(ip):
    status = host_discovery.check_host_status(ip)
    return jsonify({'online': status})

# ==================== MAIN ====================

if __name__ == '__main__':
    logger.info("Uruchamianie Network Protocol Suite")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)