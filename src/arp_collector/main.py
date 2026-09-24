import logging
from pathlib import Path

import yaml
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

from .collector import collect_arp

PROJECT_DIR = Path(__file__).resolve().parents[2]
WORKSPACE_DIR = PROJECT_DIR.parent

LOG_DIR = PROJECT_DIR / "logs"
LOG_FILE = LOG_DIR / "arp_collector.log"

logger = logging.getLogger(__name__)

INVENTORY_FILES = [
    WORKSPACE_DIR / "inventory" / "ios-devices.yml",
    WORKSPACE_DIR / "inventory" / "ocnos-devices.yml",
]

CREDENTIALS_FILE = Path.home() / ".config" / "network-automation" / "credentials.yml"
OUTPUT_FILE = PROJECT_DIR / "output" / "arp_output.txt"


def setup_logging() -> None:
    """
    Configure application logging to both a file and the terminal.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(),
        ],
    )

    # Suppress verbose library logs while retaining warnings and errors.
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.getLogger("netmiko").setLevel(logging.WARNING)


def load_yaml(path: Path) -> dict:
    """
    Load and parse a YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed YAML content as a dictionary.
    """
    with path.open("r") as file:
        return yaml.safe_load(file)


def load_devices() -> list[dict]:
    """
    Load devices from all configured inventory files.

    Returns:
        Combined list of device dictionaries from the inventories.
    """
    devices = []

    for inventory_file in INVENTORY_FILES:
        data = load_yaml(inventory_file)
        devices.extend(data.get("devices", []))

    return devices


def load_credentials() -> dict:
    """
    Load credential profiles from the protected local credentials file.

    Returns:
        Dictionary containing credential profiles by profile name.
    """
    return load_yaml(CREDENTIALS_FILE)


def main() -> None:
    """
    Run the ARP collection workflow for all inventory devices.
    """
    setup_logging()

    devices = load_devices()
    credentials = load_credentials()

    success_count = 0
    failure_count = 0

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Start each collection run with a fresh output file.
    with OUTPUT_FILE.open("w") as outfile:
        for device in devices:
            profile_name = device["credential_profile"]
            profile = credentials[profile_name]

            try:
                arp_output = collect_arp(
                    device=device,
                    username=profile["username"],
                    password=profile["password"],
                )

                outfile.write(f"\n===== {device['name']} =====\n")
                outfile.write(arp_output)
                outfile.write("\n")

                success_count += 1

            except NetmikoAuthenticationException as exc:
                failure_count += 1

                outfile.write(f"\n===== {device['name']} =====\n")
                outfile.write("ERROR: Authentication failed\n")

                logger.error(
                    "Authentication failed for %s (%s): %s",
                    device["name"],
                    device["host"],
                    exc,
                )

            except NetmikoTimeoutException as exc:
                failure_count += 1

                outfile.write(f"\n===== {device['name']} =====\n")
                outfile.write("ERROR: Connection timed out\n")

                logger.error(
                    "Connection timeout for %s (%s): %s",
                    device["name"],
                    device["host"],
                    exc,
                )

            except Exception as exc:
                failure_count += 1

                outfile.write(f"\n===== {device['name']} =====\n")
                outfile.write(f"ERROR: {exc}\n")

                logger.exception(
                    "Unexpected error for %s (%s)",
                    device["name"],
                    device["host"],
                )

    logger.info(
        "ARP collection run completed: %s succeeded, %s failed",
        success_count,
        failure_count,
    )

    logger.info("Output written to: %s", OUTPUT_FILE)


if __name__ == "__main__":
    main()
