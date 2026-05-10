import threading
import time
from typing import List, Optional
from scapy.all import ARP, Ether, srp

from ..models.device import Device
from ..utils.vendor import lookup_vendor
from ..utils.network import get_network_range


class NetworkScanner:
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._devices: List[Device] = []
        self._callback = None

    def set_callback(self, callback):
        self._callback = callback

    @property
    def devices(self) -> List[Device]:
        return self._devices

    def scan(self, timeout: int = 10) -> List[Device]:
        network = get_network_range()
        arp = ARP(pdst=network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp

        result = srp(packet, timeout=timeout, verbose=0)[0]
        devices = []
        seen_macs = set()
        for sent, received in result:
            mac = received.hwsrc
            if mac in seen_macs:
                continue
            seen_macs.add(mac)
            ip = received.psrc
            vendor = lookup_vendor(mac)
            devices.append(Device(
                ip=ip,
                mac=mac,
                hostname=self._resolve_hostname(ip),
                vendor=vendor,
                online=True,
            ))

        self._devices = devices
        if self._callback:
            self._callback(devices)
        return devices

    def _resolve_hostname(self, ip: str) -> str:
        try:
            import socket
            name, _, _ = socket.gethostbyaddr(ip)
            return name
        except Exception:
            return "Unknown"

    def start_continuous_scan(self, interval: int = 30):
        self._running = True
        self._thread = threading.Thread(target=self._scan_loop, args=(interval,), daemon=True)
        self._thread.start()

    def stop_continuous_scan(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _scan_loop(self, interval: int):
        while self._running:
            self.scan()
            time.sleep(interval)
