import netifaces
import ipaddress


def get_local_ip() -> str:
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr["addr"]
                if ip.startswith("192.") or ip.startswith("10.") or ip.startswith("172."):
                    return ip
    return "127.0.0.1"


def get_network_cidr() -> str:
    ip = get_local_ip()
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                if addr["addr"] == ip:
                    netmask = addr.get("netmask", "255.255.255.0")
                    cidr = sum(bin(int(x)).count("1") for x in netmask.split("."))
                    return f"{ip}/{cidr}"
    return "192.168.1.0/24"


def get_network_range() -> str:
    cidr = get_network_cidr()
    net = ipaddress.ip_network(cidr, strict=False)
    return str(net)
