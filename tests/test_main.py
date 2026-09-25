from pathlib import Path

import pytest

from arp_collector.main import load_credentials, load_devices, load_yaml


def test_load_devices_combines_inventory_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify that load_devices() combines devices from all inventory files.
    """
    ios_inventory = tmp_path / "ios-devices.yml"
    ocnos_inventory = tmp_path / "ocnos-devices.yml"

    ios_inventory.write_text(
        "devices:\n  - name: TEST.IOS.RTR01\n    host: 192.0.2.1\n"
    )

    ocnos_inventory.write_text(
        "devices:\n  - name: TEST.OCNOS.RTR01\n    host: 192.0.2.2\n"
    )

    monkeypatch.setattr(
        "arp_collector.main.INVENTORY_FILES",
        [ios_inventory, ocnos_inventory],
    )

    result = load_devices()

    assert result == [
        {
            "name": "TEST.IOS.RTR01",
            "host": "192.0.2.1",
        },
        {
            "name": "TEST.OCNOS.RTR01",
            "host": "192.0.2.2",
        },
    ]


def test_load_yaml(tmp_path: Path) -> None:
    """
    Verify that load_yaml() parses YAML content into a dictionary.
    """
    test_file = tmp_path / "devices.yml"
    test_file.write_text("devices:\n  - name: TEST.RTR01\n    host: 192.0.2.1\n")

    result = load_yaml(test_file)

    assert result == {
        "devices": [
            {
                "name": "TEST.RTR01",
                "host": "192.0.2.1",
            }
        ]
    }


def test_load_credentials_uses_configured_credentials_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Verify that load_credentials() reads the configured credentials file.
    """
    credentials_file = tmp_path / "credentials.yml"

    credentials_file.write_text(
        "cisco_iosxe:\n"
        "  username: test-cisco-user\n"
        "  password: test-cisco-password\n"
        "ocnos:\n"
        "  username: test-ocnos-user\n"
        "  password: test-ocnos-password\n"
    )

    monkeypatch.setattr(
        "arp_collector.main.CREDENTIALS_FILE",
        credentials_file,
    )

    result = load_credentials()

    assert result == {
        "cisco_iosxe": {
            "username": "test-cisco-user",
            "password": "test-cisco-password",
        },
        "ocnos": {
            "username": "test-ocnos-user",
            "password": "test-ocnos-password",
        },
    }
