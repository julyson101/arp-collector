import logging

from netmiko import ConnectHandler

logger = logging.getLogger(__name__)


def collect_arp(device: dict, username: str, password: str) -> str:
    """
    Connect to a network device and retrieve its ARP table.

    Args:
        device: Device information from the inventory.
        username: Username used to authenticate to the device.
        password: Password used to authenticate to the device.

    Returns:
        Raw ARP table output returned by the device.
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
        # Always close the SSH session, even if command execution fails.
        connection.disconnect()
