import ipaddress 

def is_bogon(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        bogon_ranges = [
            ipaddress.ip_network('0.0.0.0/8'),
            ipaddress.ip_network('10.0.0.0/8'),
            ipaddress.ip_network('127.0.0.0/8'),
            ipaddress.ip_network('169.254.0.0/16'),
            ipaddress.ip_network('172.16.0.0/12'),
            ipaddress.ip_network('192.168.0.0/16'),
            ipaddress.ip_network('224.0.0.0/4'),
            ipaddress.ip_network('240.0.0.0/4'),
        ]
        return any(ip_obj in net for net in bogon_ranges)
    except ValueError:
        return False