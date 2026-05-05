from netmiko import ConnectHandler


def collect_arp(device):
    """
    Connects to a device and retrieves ARP table
    """
    print(f"Connecting to {device['name']} ({device['host']})")

    connection = ConnectHandler(
            device_type=device["device_type"],
            host=device["host"],
            username=device["username"],
            password=device["password"],
    )

    output = connection.send_command("show arp")
    connection.disconnect()

    return output

