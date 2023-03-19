def parse_address(address):
    res = address.split(':')
    ip = res[0]
    port = res[1]
    return ip, port