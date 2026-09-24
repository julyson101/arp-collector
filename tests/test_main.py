from pathlib import Path

from arp_collector.main import load_yaml


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
