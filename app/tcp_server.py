"""
tcp_server.py - Wielowątkowy serwer TCP
"""

import socket
import threading
import logging
from typing import Dict, List
from protocol import CustomProtocol

logger = logging.getLogger(__name__)


class TCPServer:
    """Wielowątkowy serwer TCP"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000, max_clients: int = 10):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.server_socket = None
        self.running = False
        self.clients: List[socket.socket] = []
        self.lock = threading.Lock()
        self.stats = {
            'bytes_received': 0,
            'packets_received': 0,
            'clients_connected': 0
        }
    
    def start(self):
        """Uruchamia serwer TCP"""
        if self.running:
            logger.warning("Serwer TCP już uruchomiony")
            return False
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_clients)
            self.running = True
            
            logger.info(f"TCP Serwer nasłuchuje na {self.host}:{self.port}")
            
            # Wątek akceptujący połączenia
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            return True
        except Exception as e:
            logger.error(f"Błąd uruchamiania TCP serwera: {e}")
            return False
    
    def stop(self):
        """Zatrzymuje serwer TCP"""
        self.running = False
        
        with self.lock:
            for client in self.clients:
                try:
                    client.close()
                except:
                    pass
            self.clients.clear()
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("TCP Serwer zatrzymany")
    
    def _accept_connections(self):
        """Wątek akceptujący nowe połączenia"""
        while self.running:
            try:
                client_socket, client_addr = self.server_socket.accept()
                
                with self.lock:
                    if len(self.clients) < self.max_clients:
                        self.clients.append(client_socket)
                        self.stats['clients_connected'] = len(self.clients)
                        logger.info(f"Nowe połączenie TCP z {client_addr}")
                        
                        # Utwórz wątek do obsługi klienta
                        client_thread = threading.Thread(
                            target=self._handle_client,
                            args=(client_socket, client_addr),
                            daemon=True
                        )
                        client_thread.start()
                    else:
                        client_socket.close()
                        logger.warning(f"Odrzucono połączenie z {client_addr} - max klientów")
            
            except Exception as e:
                if self.running:
                    logger.error(f"Błąd akceptowania połączenia: {e}")
    
    def _handle_client(self, client_socket: socket.socket, client_addr: tuple):
        """Obsługuje jednego klienta TCP"""
        try:
            client_socket.settimeout(30)
            
            while self.running:
                try:
                    # Odbierz dane
                    data = client_socket.recv(65535)
                    
                    if not data:
                        break
                    
                    # Parsuj ramkę
                    result = CustomProtocol.parse_tcp_frame(data)
                    if result:
                        header, payload = result
                        self.stats['bytes_received'] += len(payload)
                        self.stats['packets_received'] += 1
                        
                        logger.debug(f"TCP: Odebrano {len(payload)} B od {client_addr}")
                        logger.debug(f"Header: {header}")
                        
                        # Wyślij echo
                        response = CustomProtocol.build_tcp_frame(
                            payload,
                            packet_type=CustomProtocol.TYPE_DATA
                        )
                        client_socket.send(response)
                    else:
                        logger.warning(f"Nieprawidłowa ramka od {client_addr}")
                
                except socket.timeout:
                    logger.warning(f"Timeout dla klienta {client_addr}")
                    break
                except Exception as e:
                    logger.error(f"Błąd obsługi klienta {client_addr}: {e}")
                    break
        
        finally:
            with self.lock:
                try:
                    self.clients.remove(client_socket)
                except:
                    pass
                self.stats['clients_connected'] = len(self.clients)
            
            client_socket.close()
            logger.info(f"Rozłączono {client_addr}")
    
    def get_stats(self) -> Dict:
        """Zwraca statystyki serwera"""
        with self.lock:
            return self.stats.copy()