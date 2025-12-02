"""
udp_client.py - Klient UDP
"""

import socket
import logging
from typing import Dict
from protocol import CustomProtocol

logger = logging.getLogger(__name__)


class UDPClient:
    """Klient UDP bez stanowy (stateless)"""
    
    def __init__(self, host: str = 'localhost', port: int = 5001):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stats = {
            'bytes_sent': 0,
            'packets_sent': 0,
            'bytes_received': 0,
            'packets_received': 0
        }
    
    def send_message(self, message: str) -> bool:
        """Wysyła wiadomość tekstową"""
        try:
            message_bytes = message.encode('utf-8')
            
            # Podziel na pakiety jeśli potrzeba
            chunk_size = 65500
            chunks = [
                message_bytes[i:i + chunk_size] 
                for i in range(0, len(message_bytes), chunk_size)
            ]
            
            total_chunks = len(chunks)
            
            for idx, chunk in enumerate(chunks):
                frame = CustomProtocol.build_udp_frame(
                    chunk,
                    packet_id=idx,
                    total_packets=total_chunks,
                    packet_type=CustomProtocol.TYPE_AUDIO
                )
                
                self.socket.sendto(frame, (self.host, self.port))
                self.stats['bytes_sent'] += len(chunk)
                self.stats['packets_sent'] += 1
            
            logger.info(f"Wysłano {len(message_bytes)} B w {total_chunks} pakietach UDP")
            return True
        except Exception as e:
            logger.error(f"Błąd wysyłania UDP: {e}")
            return False
    
    def send_binary(self, data: bytes) -> bool:
        """Wysyła dane binarne (np. audio)"""
        try:
            chunk_size = 65500
            chunks = [
                data[i:i + chunk_size] 
                for i in range(0, len(data), chunk_size)
            ]
            
            total_chunks = len(chunks)
            
            for idx, chunk in enumerate(chunks):
                frame = CustomProtocol.build_udp_frame(
                    chunk,
                    packet_id=idx,
                    total_packets=total_chunks,
                    packet_type=CustomProtocol.TYPE_AUDIO
                )
                
                self.socket.sendto(frame, (self.host, self.port))
                self.stats['bytes_sent'] += len(chunk)
                self.stats['packets_sent'] += 1
            
            logger.info(f"Wysłano {len(data)} B w {total_chunks} pakietach UDP (audio)")
            return True
        except Exception as e:
            logger.error(f"Błąd wysyłania danych binarnych UDP: {e}")
            return False
    
    def close(self):
        """Zamyka gniazdo"""
        self.socket.close()
    
    def get_stats(self) -> Dict:
        """Zwraca statystyki"""
        return self.stats.copy()