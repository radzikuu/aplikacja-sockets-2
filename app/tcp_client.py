"""
tcp_client.py - Klient TCP
"""

import socket
import threading
import logging
import time
from typing import Dict, Optional
from protocol import CustomProtocol

logger = logging.getLogger(__name__)


class TCPClient:
    """Klient TCP z automatycznym reconnectem"""
    
    def __init__(self, host: str = 'localhost', port: int = 5000, auto_reconnect: bool = True):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.auto_reconnect = auto_reconnect
        self.lock = threading.Lock()
        self.stats = {
            'bytes_sent': 0,
            'bytes_received': 0,
            'packets_sent': 0,
            'packets_received': 0,
            'connection_attempts': 0,
            'last_connection_time': None
        }
        self.receive_thread = None
        self.reconnect_interval = 5  # sekund
    
    def connect(self) -> bool:
        """Łączy się z serwerem"""
        with self.lock:
            if self.connected:
                logger.warning("Już połączony")
                return True
            
            self.stats['connection_attempts'] += 1
            
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(10)
                self.socket.connect((self.host, self.port))
                self.connected = True
                self.stats['last_connection_time'] = time.time()
                
                logger.info(f"Połączono z {self.host}:{self.port}")
                
                # Uruchom wątek odbierania
                self.receive_thread = threading.Thread(
                    target=self._receive_loop,
                    daemon=True
                )
                self.receive_thread.start()
                
                return True
            except Exception as e:
                logger.error(f"Błąd połączenia: {e}")
                self.connected = False
                return False
    
    def disconnect(self):
        """Rozłącza się"""
        with self.lock:
            self.connected = False
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
            logger.info("Rozłączono")
    
    def send_message(self, message: str) -> bool:
        """Wysyła wiadomość tekstową"""
        if not self.connected:
            logger.error("Nie połączony")
            return False
        
        try:
            message_bytes = message.encode('utf-8')
            frame = CustomProtocol.build_tcp_frame(
                message_bytes,
                packet_type=CustomProtocol.TYPE_DATA
            )
            
            with self.lock:
                self.socket.send(frame)
                self.stats['bytes_sent'] += len(message_bytes)
                self.stats['packets_sent'] += 1
            
            logger.info(f"Wysłano {len(message_bytes)} B")
            return True
        except Exception as e:
            logger.error(f"Błąd wysyłania: {e}")
            self.connected = False
            return False
    
    def send_binary(self, data: bytes) -> bool:
        """Wysyła dane binarne"""
        if not self.connected:
            logger.error("Nie połączony")
            return False
        
        try:
            frame = CustomProtocol.build_tcp_frame(
                data,
                packet_type=CustomProtocol.TYPE_DATA
            )
            
            with self.lock:
                self.socket.send(frame)
                self.stats['bytes_sent'] += len(data)
                self.stats['packets_sent'] += 1
            
            logger.info(f"Wysłano {len(data)} B danych binarnych")
            return True
        except Exception as e:
            logger.error(f"Błąd wysyłania: {e}")
            self.connected = False
            return False
    
    def _receive_loop(self):
        """Pętla odbierania"""
        while self.connected:
            try:
                data = self.socket.recv(65535)
                
                if not data:
                    logger.warning("Serwer zamknął połączenie")
                    self.connected = False
                    break
                
                result = CustomProtocol.parse_tcp_frame(data)
                if result:
                    header, payload = result
                    with self.lock:
                        self.stats['bytes_received'] += len(payload)
                        self.stats['packets_received'] += 1
                    
                    logger.debug(f"Odebrano {len(payload)} B")
                else:
                    logger.warning("Nieprawidłowa ramka TCP")
            
            except socket.timeout:
                pass
            except Exception as e:
                logger.error(f"Błąd odbierania: {e}")
                self.connected = False
        
        # Automat reconnect
        if self.auto_reconnect and not self.connected:
            logger.info(f"Próba reconnect za {self.reconnect_interval}s...")
            time.sleep(self.reconnect_interval)
            self.connect()
    
    def get_stats(self) -> Dict:
        """Zwraca statystyki"""
        with self.lock:
            return self.stats.copy()