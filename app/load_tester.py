"""
load_tester.py - Narzędzie do testów obciążeniowych
Trzy tryby:
1. normal - Normalne pakiety TCP z czekaniem na response
2. flood - Zalewanie pakietami bez czekania
3. slowloris - Powolne pakiety (atakujące słowością)
"""

import socket
import threading
import logging
import time
from typing import Dict, List
from protocol import CustomProtocol

logger = logging.getLogger(__name__)


class LoadTester:
    """Narzędzie do testów obciążeniowych"""
    
    # Tryby testów
    MODE_NORMAL = 'normal'
    MODE_FLOOD = 'flood'
    MODE_SLOWLORIS = 'slowloris'
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.running = False
        self.lock = threading.Lock()
        self.stats = {
            'packets_sent': 0,
            'successful_connections': 0,
            'errors': 0,
            'total_response_time': 0.0,
            'response_count': 0,
            'avg_response_time': 0.0,
            'min_response_time': float('inf'),
            'max_response_time': 0.0,
            'bytes_sent': 0
        }
        self.threads: List[threading.Thread] = []
    
    def start_test(self, mode: str, num_threads: int, packets_per_thread: int,
                   packet_size: int = 1024, packet_delay_ms: int = 10) -> bool:
        """Uruchamia test obciążeniowy"""
        
        if self.running:
            logger.warning("Test już się wykonuje")
            return False
        
        if mode not in [self.MODE_NORMAL, self.MODE_FLOOD, self.MODE_SLOWLORIS]:
            logger.error(f"Nieznany tryb: {mode}")
            return False
        
        self.running = True
        self._reset_stats()
        
        logger.info(f"Rozpoczęcie testu: {mode} ({num_threads} wątków, {packets_per_thread} pakietów/wątek)")
        
        # Uruchom wątki
        for thread_id in range(num_threads):
            thread = threading.Thread(
                target=self._thread_worker,
                args=(thread_id, mode, packets_per_thread, packet_size, packet_delay_ms),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
        
        return True
    
    def stop_test(self):
        """Zatrzymuje test"""
        self.running = False
        logger.info("Test zatrzymany")
    
    def _reset_stats(self):
        """Resetuje statystyki"""
        with self.lock:
            for key in self.stats:
                if key in ['min_response_time']:
                    self.stats[key] = float('inf')
                else:
                    self.stats[key] = 0.0 if isinstance(self.stats[key], float) else 0
    
    def _thread_worker(self, thread_id: int, mode: str, packets: int, 
                      packet_size: int, delay_ms: int):
        """Wątek pracownika"""
        
        for packet_num in range(packets):
            if not self.running:
                break
            
            try:
                # Utwórz socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                
                # Połącz
                start_time = time.time()
                sock.connect((self.host, self.port))
                connection_time = (time.time() - start_time) * 1000
                
                with self.lock:
                    self.stats['successful_connections'] += 1
                
                # Przygotuj dane
                data = b'X' * packet_size
                frame = CustomProtocol.build_tcp_frame(data)
                
                # Wyślij
                send_time = time.time()
                sock.send(frame)
                
                with self.lock:
                    self.stats['bytes_sent'] += packet_size
                    self.stats['packets_sent'] += 1
                
                # Obsłuż odpowiedź w zależności od trybu
                if mode == self.MODE_NORMAL:
                    # Czekaj na echo
                    response = sock.recv(65535)
                    response_time = (time.time() - send_time) * 1000
                    
                    with self.lock:
                        self.stats['total_response_time'] += response_time
                        self.stats['response_count'] += 1
                        self.stats['min_response_time'] = min(
                            self.stats['min_response_time'], response_time
                        )
                        self.stats['max_response_time'] = max(
                            self.stats['max_response_time'], response_time
                        )
                
                elif mode == self.MODE_FLOOD:
                    # Nie czekaj na odpowiedź
                    pass
                
                elif mode == self.MODE_SLOWLORIS:
                    # Wyślij powoli (po kawałku)
                    chunk_size = packet_size // 4 if packet_size >= 4 else packet_size
                    for i in range(0, packet_size, chunk_size):
                        if self.running:
                            time.sleep(0.1)
                
                sock.close()
                
                # Opóźnienie
                if delay_ms > 0:
                    time.sleep(delay_ms / 1000.0)
            
            except Exception as e:
                with self.lock:
                    self.stats['errors'] += 1
                logger.debug(f"Błąd wątku {thread_id}, pakiet {packet_num}: {e}")
                try:
                    sock.close()
                except:
                    pass
        
        logger.debug(f"Wątek {thread_id} zakończony")
    
    def _update_avg_response_time(self):
        """Aktualizuje średni czas odpowiedzi"""
        if self.stats['response_count'] > 0:
            self.stats['avg_response_time'] = (
                self.stats['total_response_time'] / self.stats['response_count']
            )
    
    def get_stats(self) -> Dict:
        """Zwraca bieżące statystyki"""
        with self.lock:
            self._update_avg_response_time()
            stats = self.stats.copy()
        
        # Obsłuż nieskończoność
        if stats['min_response_time'] == float('inf'):
            stats['min_response_time'] = 0
        
        return stats
    
    def is_running(self) -> bool:
        """Czy test się wykonuje?"""
        return self.running