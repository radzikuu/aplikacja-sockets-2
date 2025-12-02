"""
udp_server.py - Serwer UDP
"""

import socket
import threading
import logging
from typing import Dict
from protocol import CustomProtocol

logger = logging.getLogger(__name__)


class UDPServer:
    """Serwer UDP"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5001, buffer_size: int = 65535):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.server_socket = None
        self.running = False
        self.lock = threading.Lock()
        self.stats = {
            'bytes_received': 0,
            'packets_received': 0,
            'packets_sent': 0
        }
    
    def start(self):
        """Uruchamia serwer UDP"""
        if self.running:
            logger.warning("Serwer UDP już uruchomiony")
            return False
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.running = True
            
            logger.info(f"UDP Serwer nasłuchuje na {self.host}:{self.port} (buffer: {self.buffer_size}B)")
            
            # Wątek nasłuchujący
            listen_thread = threading.Thread(target=self._listen, daemon=True)
            listen_thread.start()
            
            return True
        except Exception as e:
            logger.error(f"Błąd uruchamiania UDP serwera: {e}")
            return False
    
    def stop(self):
        """Zatrzymuje serwer UDP"""
        self.running = False
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("UDP Serwer zatrzymany")
    
    def _listen(self):
        """Wątek nasłuchujący UDP"""
        while self.running:
            try:
                data, client_addr = self.server_socket.recvfrom(self.buffer_size)
                
                # Parsuj ramkę
                result = CustomProtocol.parse_udp_frame(data)
                if result:
                    header, payload = result
                    with self.lock:
                        self.stats['bytes_received'] += len(payload)
                        self.stats['packets_received'] += 1
                    
                    logger.debug(f"UDP: Odebrano {len(payload)} B od {client_addr}")
                    logger.debug(f"Header: {header}")
                    
                    # Wyślij echo
                    response = CustomProtocol.build_udp_frame(
                        payload,
                        packet_type=CustomProtocol.TYPE_AUDIO
                    )
                    self.server_socket.sendto(response, client_addr)
                    
                    with self.lock:
                        self.stats['packets_sent'] += 1
                else:
                    logger.warning(f"Nieprawidłowa ramka UDP od {client_addr}")
            
            except Exception as e:
                if self.running:
                    logger.error(f"Błąd nasłuchiwania UDP: {e}")
    
    def get_stats(self) -> Dict:
        """Zwraca statystyki serwera"""
        with self.lock:
            return self.stats.copy()