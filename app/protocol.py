"""
protocol.py - Definicja własnego protokołu TCP/UDP
Ramka TCP: 0xCAFEBABE (magiczny numer, 20 bajtów nagłówka)
Ramka UDP: 0xDEADBEEF (magiczny numer, 16 bajtów nagłówka)
"""

import struct
import time
from typing import Tuple, Optional
import binascii


class CustomProtocol:
    """Implementacja własnego protokołu TCP/UDP"""
    
    # Magiczne numery
    TCP_MAGIC = 0xCAFEBABE
    UDP_MAGIC = 0xDEADBEEF
    
    # Typy pakietów
    TYPE_DATA = 0x01
    TYPE_AUDIO = 0x02
    TYPE_CONTROL = 0x03
    TYPE_HEARTBEAT = 0x04
    
    # Rozmiary nagłówków
    TCP_HEADER_SIZE = 20
    UDP_HEADER_SIZE = 16
    
    @staticmethod
    def calculate_crc32(data: bytes) -> int:
        """Oblicza sumę kontrolną CRC32"""
        return binascii.crc32(data) & 0xffffffff
    
    @staticmethod
    def build_tcp_frame(message: bytes, packet_type: int = TYPE_DATA, 
                       sequence_num: int = 0) -> bytes:
        """
        Buduje ramkę TCP
        Struktura (20 B):
        - Magic number (4 B): 0xCAFEBABE
        - Type (1 B): 0x01=DATA, 0x02=AUDIO, 0x03=CONTROL
        - Length (2 B): długość danych
        - CRC32 (4 B): suma kontrolna
        - Timestamp (4 B): czas wysłania
        - Sequence number (4 B): numer sekwencyjny
        + Dane zmiennej długości
        """
        timestamp = int(time.time() * 1000) & 0xffffffff
        message_len = len(message)
        
        # Buduj nagłówek (bez CRC na początek)
        header = struct.pack('>I', CustomProtocol.TCP_MAGIC)  # Magic
        header += struct.pack('B', packet_type)                 # Type
        header += struct.pack('>H', message_len)                # Length
        header += struct.pack('>I', 0)                          # Placeholder CRC
        header += struct.pack('>I', timestamp)                  # Timestamp
        header += struct.pack('>I', sequence_num)               # Sequence
        
        # Oblicz CRC32 na nagłówek + dane
        full_data = header + message
        crc = CustomProtocol.calculate_crc32(full_data)
        
        # Wstaw CRC do nagłówka
        header = struct.pack('>I', CustomProtocol.TCP_MAGIC)
        header += struct.pack('B', packet_type)
        header += struct.pack('>H', message_len)
        header += struct.pack('>I', crc)
        header += struct.pack('>I', timestamp)
        header += struct.pack('>I', sequence_num)
        
        return header + message
    
    @staticmethod
    def parse_tcp_frame(data: bytes) -> Optional[Tuple[dict, bytes]]:
        """
        Parsuje ramkę TCP
        Zwraca: (header_info, payload) lub None jeśli błąd
        """
        if len(data) < CustomProtocol.TCP_HEADER_SIZE:
            return None
        
        try:
            # Rozpakuj nagłówek
            magic, = struct.unpack('>I', data[0:4])
            if magic != CustomProtocol.TCP_MAGIC:
                return None
            
            pkt_type, = struct.unpack('B', data[4:5])
            msg_len, = struct.unpack('>H', data[5:7])
            crc, = struct.unpack('>I', data[7:11])
            timestamp, = struct.unpack('>I', data[11:15])
            seq_num, = struct.unpack('>I', data[15:19])
            
            # Pobierz payload
            payload = data[19:19 + msg_len]
            
            if len(payload) != msg_len:
                return None
            
            # Weryfikuj CRC
            full_data = data[:7] + struct.pack('>I', 0) + data[11:19] + payload
            calculated_crc = CustomProtocol.calculate_crc32(full_data)
            
            if calculated_crc != crc:
                return None
            
            header_info = {
                'magic': hex(magic),
                'type': pkt_type,
                'length': msg_len,
                'crc': hex(crc),
                'timestamp': timestamp,
                'sequence': seq_num
            }
            
            return (header_info, payload)
        
        except struct.error:
            return None
    
    @staticmethod
    def build_udp_frame(message: bytes, packet_id: int = 0, 
                       total_packets: int = 1, packet_type: int = TYPE_AUDIO) -> bytes:
        """
        Buduje ramkę UDP
        Struktura (16 B):
        - Magic number (4 B): 0xDEADBEEF
        - Type (1 B): 0x02=AUDIO
        - Length (2 B): długość danych
        - CRC32 (4 B): suma kontrolna
        - Packet ID (2 B): ID pakietu w sekwencji
        - Total packets (2 B): całkowita liczba pakietów
        - Timestamp (1 B): czas (kompresowany)
        + Dane zmiennej długości
        """
        message_len = len(message)
        timestamp = int(time.time() * 100) & 0xff
        
        # Buduj nagłówek
        header = struct.pack('>I', CustomProtocol.UDP_MAGIC)   # Magic
        header += struct.pack('B', packet_type)                 # Type
        header += struct.pack('>H', message_len)                # Length
        header += struct.pack('>I', 0)                          # Placeholder CRC
        header += struct.pack('>H', packet_id)                  # Packet ID
        header += struct.pack('>H', total_packets)              # Total packets
        header += struct.pack('B', timestamp)                   # Timestamp
        
        # Oblicz CRC32
        full_data = header + message
        crc = CustomProtocol.calculate_crc32(full_data)
        
        # Wstaw CRC
        header = struct.pack('>I', CustomProtocol.UDP_MAGIC)
        header += struct.pack('B', packet_type)
        header += struct.pack('>H', message_len)
        header += struct.pack('>I', crc)
        header += struct.pack('>H', packet_id)
        header += struct.pack('>H', total_packets)
        header += struct.pack('B', timestamp)
        
        return header + message
    
    @staticmethod
    def parse_udp_frame(data: bytes) -> Optional[Tuple[dict, bytes]]:
        """
        Parsuje ramkę UDP
        Zwraca: (header_info, payload) lub None jeśli błąd
        """
        if len(data) < CustomProtocol.UDP_HEADER_SIZE:
            return None
        
        try:
            # Rozpakuj nagłówek
            magic, = struct.unpack('>I', data[0:4])
            if magic != CustomProtocol.UDP_MAGIC:
                return None
            
            pkt_type, = struct.unpack('B', data[4:5])
            msg_len, = struct.unpack('>H', data[5:7])
            crc, = struct.unpack('>I', data[7:11])
            pkt_id, = struct.unpack('>H', data[11:13])
            total_pkts, = struct.unpack('>H', data[13:15])
            timestamp, = struct.unpack('B', data[15:16])
            
            # Pobierz payload
            payload = data[16:16 + msg_len]
            
            if len(payload) != msg_len:
                return None
            
            # Weryfikuj CRC
            full_data = data[:7] + struct.pack('>I', 0) + data[11:16] + payload
            calculated_crc = CustomProtocol.calculate_crc32(full_data)
            
            if calculated_crc != crc:
                return None
            
            header_info = {
                'magic': hex(magic),
                'type': pkt_type,
                'length': msg_len,
                'crc': hex(crc),
                'packet_id': pkt_id,
                'total_packets': total_pkts,
                'timestamp': timestamp
            }
            
            return (header_info, payload)
        
        except struct.error:
            return None