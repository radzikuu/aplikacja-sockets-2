import struct
import hashlib
import time

class CustomProtocol:
    """Własny protokół z nagłówkami i sumami kontrolnymi"""
    
    HEADER_FORMAT = '!BBHIQ'  # version, type, length, sequence, timestamp
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    VERSION = 1
    
    # Typy ramek
    TYPE_DATA = 0x01
    TYPE_ACK = 0x02
    TYPE_HEARTBEAT = 0x03
    TYPE_FILE = 0x04
    
    @staticmethod
    def create_frame(data: bytes, frame_type: int, sequence: int) -> bytes:
        """Tworzy ramkę z nagłówkiem i sumą kontrolną"""
        timestamp = int(time.time() * 1000)
        data_length = len(data)
        
        # Nagłówek
        header = struct.pack(
            CustomProtocol.HEADER_FORMAT,
            CustomProtocol.VERSION,
            frame_type,
            data_length,
            sequence,
            timestamp
        )
        
        # Suma kontrolna (SHA256 pierwszych 16 bajtów)
        checksum = hashlib.sha256(header + data).digest()[:16]
        
        return header + data + checksum
    
    @staticmethod
    def parse_frame(frame: bytes) -> tuple:
        """Parsuje ramkę i weryfikuje sumę kontrolną"""
        if len(frame) < CustomProtocol.HEADER_SIZE + 16:
            raise ValueError("Ramka za krótka")
        
        # Rozpakuj nagłówek
        header = frame[:CustomProtocol.HEADER_SIZE]
        version, frame_type, length, sequence, timestamp = struct.unpack(
            CustomProtocol.HEADER_FORMAT, header
        )
        
        # Wyciągnij dane i sumę kontrolną
        data = frame[CustomProtocol.HEADER_SIZE:-16]
        received_checksum = frame[-16:]
        
        # Weryfikuj sumę kontrolną
        calculated_checksum = hashlib.sha256(header + data).digest()[:16]
        if received_checksum != calculated_checksum:
            raise ValueError("Błędna suma kontrolna")
        
        return version, frame_type, data, sequence, timestamp
