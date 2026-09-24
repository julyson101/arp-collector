from unittest.mock import patch

import pytest

from arp_collector.collector import collect_arp


def test_collect_arp_returns_command_output() -> None:
    """
    Verify that collect_arp() returns the ARP output from the device.
    """
    device = {
        "name": "TEST.RTR01",
        "host": "192.0.2.1",
        "device_type": "cisco_ios",
    }

    with patch("arp_collector.collector.ConnectHandler") as mock_connect_handler:
        mock_connection = mock_connect_handler.return_value
        mock_connection.send_command.return_value = "TEST ARP OUTPUT"

        result = collect_arp(
            device=device,
            username="testuser",
            password="testpassword",
        )

        assert result == "TEST ARP OUTPUT"

        mock_connect_handler.assert_called_once_with(
            device_type="cisco_ios",
            host="192.0.2.1",
            username="testuser",
            password="testpassword",
        )

        mock_connection.send_command.assert_called_once_with("show arp")
        mock_connection.disconnect.assert_called_once_with()


def test_collect_arp_disconnects_when_command_fails() -> None:
    """
    Verify that collect_arp() disconnects when command execution raises an error.
    """
    device = {
        "name": "TEST.RTR01",
        "host": "192.0.2.1",
        "device_type": "cisco_ios",
    }

    with patch("arp_collector.collector.ConnectHandler") as mock_connect_handler:
        mock_connection = mock_connect_handler.return_value
        mock_connection.send_command.side_effect = RuntimeError("Command failed")

        with pytest.raises(RuntimeError, match="Command failed"):
            collect_arp(
                device=device,
                username="testuser",
                password="testpassword",
            )

        mock_connection.disconnect.assert_called_once_with()
