"""
host_discovery.py - Odkrywanie hostów w sieci Docker
"""

import socket
import ipaddress
import threading
import logging
from typing import List, Dict
import json

logger = logging.getLogger(__name__)


class HostDiscovery:
    """Odkrywanie hostów w sieci Docker"""
    
    def __init__(self):
        self.discovered_hosts: List[Dict] = []
        self.lock = threading.Lock()
    
    def scan_network(self, cidr: str, timeout: float = 1.0) -> List[Dict]:
        """Skanuje sieć Docker w zakresu CIDR"""
        
        try:
            network = ipaddress.ip_network(cidr, strict=False)
        except ValueError as e:
            logger.error(f"Nieprawidłowy zakres CIDR: {e}")
            return []
        
        logger.info(f"Skanowanie sieci {cidr}...")
        
        threads = []
        self.discovered_hosts = []
        
        # Utwórz wątki dla każdego adresu
        for ip in list(network.hosts())[:50]:  # Limit dla wydajności
            thread = threading.Thread(
                target=self._probe_host,
                args=(str(ip), timeout),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # Czekaj na zakończenie
        for thread in threads:
            thread.join(timeout=timeout + 1)
        
        logger.info(f"Skanowanie zakończone, znaleziono {len(self.discovered_hosts)} hostów")
        return self.discovered_hosts
    
    def _probe_host(self, ip: str, timeout: float):
        """Sprawdza czy host jest dostępny na porcie 5000"""
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Spróbuj połączyć na TCP 5000 (Flask)
            result = sock.connect_ex((ip, 5000))
            sock.close()
            
            if result == 0:
                # Host jest dostępny
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    hostname = ip
                
                host_info = {
                    'name': hostname,
                    'ip': ip,
                    'type': 'Network Service',
                    'status': 'online',
                    'port': 5000
                }
                
                with self.lock:
                    self.discovered_hosts.append(host_info)
                
                logger.debug(f"Host znaleziony: {hostname} ({ip})")
        
        except Exception as e:
            pass
    
    def get_discovered_hosts(self) -> List[Dict]:
        """Zwraca listę odkrytych hostów"""
        with self.lock:
            return self.discovered_hosts.copy()
    
    def add_manual_host(self, ip: str, name: str = None) -> bool:
        """Dodaje host ręcznie"""
        
        if not name:
            try:
                name = socket.gethostbyaddr(ip)[0]
            except:
                name = ip
        
        host_info = {
            'name': name,
            'ip': ip,
            'type': 'Manual',
            'status': 'online',
            'port': 5000
        }
        
        with self.lock:
            # Sprawdź czy już istnieje
            for host in self.discovered_hosts:
                if host['ip'] == ip:
                    return False
            
            self.discovered_hosts.append(host_info)
        
        logger.info(f"Dodano host: {name} ({ip})")
        return True
    
    def remove_host(self, ip: str) -> bool:
        """Usuwa host"""
        
        with self.lock:
            for i, host in enumerate(self.discovered_hosts):
                if host['ip'] == ip:
                    self.discovered_hosts.pop(i)
                    return True
        
        return False
    
    def clear_hosts(self):
        """Czyści listę"""
        with self.lock:
            self.discovered_hosts = []
    
    def check_host_status(self, ip: str, timeout: float = 1.0) -> bool:
        """Sprawdza czy host jest dostępny"""
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, 5000))
            sock.close()
            return result == 0
        except:
            return False