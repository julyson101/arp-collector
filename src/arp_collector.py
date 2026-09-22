import logging

from netmiko import ConnectHandler

logger = logging.getLogger(__name__)


def collect_arp(device, username, password):
    """
    Connects to a network device and retrieves ARP table.
    """
    logger.info(
        "Connecting to %s (%s)",
        device["name"],
        device["host"],
    )


    connection = ConnectHandler(
            device_type=device["device_type"],
            host=device["host"],
            username=username,
            password=password,
    )

    try:
        output = connection.send_command("show arp")

        logger.info(
            "ARP collection successful for %s",
            device["name"],
        )

        return output


    finally: 
        connection.disconnect()
