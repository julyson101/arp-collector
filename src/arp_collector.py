from netmiko import ConnectHandler


def collect_arp(device, username, password):
    """
    Connects to a network device and retrieves ARP table.
    """
    print(f"Connecting to {device['name']} ({device['host']})")

    connection = ConnectHandler(
            device_type=device["device_type"],
            host=device["host"],
            username=username,
            password=password,
    )

    try:
        return connection.send_command("show arp")
    finally: 
        connection.disconnect()
