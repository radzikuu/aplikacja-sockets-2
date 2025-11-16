from flask import Flask, render_template, request, jsonify
import socket
import threading
import time
import struct
import os
from protocol import CustomProtocol

app = Flask(__name__)

class ConnectionManager:
    """Zarządza połączeniami i ich statusem"""
    def __init__(self):
        self.connections = {}
        self.lock = threading.Lock()
    
    def add_connection(self, address, conn_type):
        with self.lock:
            self.connections[address] = {
                'type': conn_type,
                'active': True,
                'last_seen': time.time()
            }
    
    def remove_connection(self, address):
        with self.lock:
            if address in self.connections:
                self.connections[address]['active'] = False
    
    def get_active_connections(self):
        with self.lock:
            return [addr for addr, info in self.connections.items() 
                   if info['active']]

conn_manager = ConnectionManager()

class TCPServer:
    """Serwer TCP z własnym protokołem"""
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.sequence = 0
        self.running = False
        
    def start(self):
        """Uruchamia serwer TCP"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"TCP Server listening on {self.host}:{self.port}")
        
        while self.running:
            try:
                conn, addr = server_socket.accept()
                conn_manager.add_connection(str(addr), 'TCP')
                threading.Thread(target=self.handle_client, 
                               args=(conn, addr), daemon=True).start()
            except Exception as e:
                print(f"TCP Error: {e}")
    
    def handle_client(self, conn, addr):
        """Obsługuje klienta TCP z heartbeat"""
        print(f"TCP Connected: {addr}")
        try:
            while True:
                # Odbierz nagłówek
                header = conn.recv(CustomProtocol.HEADER_SIZE)
                if not header or len(header) < CustomProtocol.HEADER_SIZE:
                    break
                    
                _, frame_type, length, _, _ = struct.unpack(
                    CustomProtocol.HEADER_FORMAT, header
                )
                
                # Odbierz resztę ramki
                remaining = length + 16  # dane + checksum
                data_with_checksum = b''
                while len(data_with_checksum) < remaining:
                    chunk = conn.recv(remaining - len(data_with_checksum))
                    if not chunk:
                        break
                    data_with_checksum += chunk
                
                frame = header + data_with_checksum
                
                # Parsuj ramkę
                version, ftype, data, seq, ts = CustomProtocol.parse_frame(frame)
                
                if ftype == CustomProtocol.TYPE_HEARTBEAT:
                    # Odpowiedz na heartbeat
                    ack = CustomProtocol.create_frame(
                        b'ACK', CustomProtocol.TYPE_ACK, seq
                    )
                    conn.sendall(ack)
                    conn_manager.add_connection(str(addr), 'TCP')
                
                elif ftype == CustomProtocol.TYPE_DATA:
                    print(f"TCP Received from {addr}: {data.decode('utf-8', errors='ignore')}")
                    # Wyślij ACK
                    ack = CustomProtocol.create_frame(
                        b'ACK', CustomProtocol.TYPE_ACK, seq
                    )
                    conn.sendall(ack)
                
                elif ftype == CustomProtocol.TYPE_FILE:
                    filename = f"received_tcp_{addr[1]}.dat"
                    with open(filename, 'wb') as f:
                        f.write(data)
                    print(f"TCP File saved: {filename}")
                    
        except Exception as e:
            print(f"TCP Client error {addr}: {e}")
        finally:
            conn_manager.remove_connection(str(addr))
            conn.close()

class UDPServer:
    """Serwer UDP z własnym protokołem"""
    def __init__(self, host='0.0.0.0', port=5001):
        self.host = host
        self.port = port
        self.running = False
        
    def start(self):
        """Uruchamia serwer UDP"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((self.host, self.port))
        print(f"UDP Server listening on {self.host}:{self.port}")
        
        while self.running:
            try:
                frame, addr = server_socket.recvfrom(65535)
                conn_manager.add_connection(str(addr), 'UDP')
                
                # Parsuj ramkę
                version, ftype, data, seq, ts = CustomProtocol.parse_frame(frame)
                
                if ftype == CustomProtocol.TYPE_DATA:
                    print(f"UDP Received from {addr}: {data[:100]}")
                    # Wyślij ACK
                    ack = CustomProtocol.create_frame(
                        b'ACK', CustomProtocol.TYPE_ACK, seq
                    )
                    server_socket.sendto(ack, addr)
                
                elif ftype == CustomProtocol.TYPE_FILE:
                    filename = f"received_udp_{addr[1]}.mp3"
                    with open(filename, 'wb') as f:
                        f.write(data)
                    print(f"UDP File saved: {filename}")
                    
            except Exception as e:
                print(f"UDP Error: {e}")

class Client:
    """Klient z auto-reconnect"""
    def __init__(self, host, port, protocol='TCP'):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.socket = None
        self.connected = False
        self.sequence = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
    def connect(self):
        """Łączy z serwerem"""
        try:
            if self.protocol == 'TCP':
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(5)  # 5 sekund timeout
                self.socket.connect((self.host, self.port))
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            self.connected = True
            self.reconnect_attempts = 0
            print(f"Connected to {self.host}:{self.port} via {self.protocol}")
            
            # Uruchom heartbeat w osobnym wątku
            if self.protocol == 'TCP':
                threading.Thread(target=self.heartbeat, daemon=True).start()
            
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def heartbeat(self):
        """Wysyła heartbeat co 5 sekund"""
        while self.connected:
            try:
                frame = CustomProtocol.create_frame(
                    b'HEARTBEAT', 
                    CustomProtocol.TYPE_HEARTBEAT, 
                    self.sequence
                )
                self.socket.sendall(frame)
                self.sequence += 1
                time.sleep(5)
            except:
                self.connected = False
                self.auto_reconnect()
    
    def auto_reconnect(self):
        """Automatyczne ponowne łączenie"""
        while self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            print(f"Reconnect attempt {self.reconnect_attempts}...")
            time.sleep(2 ** self.reconnect_attempts)  # Exponential backoff
            
            if self.connect():
                return True
        
        print("Max reconnect attempts reached")
        return False
    
    def send_data(self, data, frame_type):
        """Wysyła dane przez socket"""
        if not self.connected and not self.connect():
            return False
        
        try:
            frame = CustomProtocol.create_frame(data, frame_type, self.sequence)
            self.sequence += 1
            
            if self.protocol == 'TCP':
                self.socket.sendall(frame)
            else:
                self.socket.sendto(frame, (self.host, self.port))
            
            print(f"Data sent via {self.protocol}")
            return True
        except Exception as e:
            print(f"Send error: {e}")
            self.connected = False
            if self.protocol == 'TCP':
                return self.auto_reconnect()
            return False
    
    def send_text(self, text):
        """Wysyła tekst przez socket"""
        return self.send_data(text.encode('utf-8'), CustomProtocol.TYPE_DATA)
    
    def send_file(self, filepath, frame_type):
        """Wysyła plik przez socket"""
        if not self.connected and not self.connect():
            return False
        
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            return self.send_data(data, frame_type)
        except Exception as e:
            print(f"File send error: {e}")
            return False

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/discover', methods=['GET'])
def discover_hosts():
    """Odkrywa aktywne hosty w sieci"""
    active = conn_manager.get_active_connections()
    return jsonify({'hosts': active})

@app.route('/api/send', methods=['POST'])
def send_data():
    """Wysyła dane do hosta"""
    try:
        host = request.form.get('host')
        port = int(request.form.get('port'))
        protocol = request.form.get('protocol', 'TCP')
        
        print(f"Sending to {host}:{port} via {protocol}")
        
        client = Client(host, port, protocol)
        
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            filepath = f"/tmp/{file.filename}"
            file.save(filepath)
            
            frame_type = (CustomProtocol.TYPE_FILE if protocol == 'UDP' 
                         else CustomProtocol.TYPE_DATA)
            success = client.send_file(filepath, frame_type)
            os.remove(filepath)
        else:
            text = request.form.get('text', '')
            if not text:
                return jsonify({'success': False, 'error': 'No text provided'}), 400
            success = client.send_text(text)
        
        return jsonify({'success': success})
    except Exception as e:
        print(f"Error in send_data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def connection_status():
    """Sprawdza status połączeń"""
    return jsonify({
        'connections': conn_manager.connections
    })

if __name__ == '__main__':
    # Uruchom serwery TCP i UDP w osobnych wątkach
    tcp_server = TCPServer()
    udp_server = UDPServer()
    
    threading.Thread(target=tcp_server.start, daemon=True).start()
    threading.Thread(target=udp_server.start, daemon=True).start()
    
    # Uruchom Flask
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
