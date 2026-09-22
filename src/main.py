from pathlib import Path

import logging

import yaml
from arp_collector import collect_arp

from netmiko.exceptions import (
        NetmikoAuthenticationException,
        NetmikoTimeoutException,
)

from arp_collector import collect_arp

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "arp_collector.log"

logger = logging.getLogger(__name__)

INVENTORY_FILES = [
    ROOT_DIR / "inventory" / "ios-devices.yml",
    ROOT_DIR / "inventory" / "ocnos-devices.yml",
]

CREDENTIALS_FILE = Path.home() / ".config" / "network-automation" / "credentials.yml"
OUTPUT_FILE = BASE_DIR / "output" / "arp_output.txt"


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(),
            ],
    )

    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.getLogger("netmiko").setLevel(logging.WARNING)


def load_yaml(path):
    with path.open("r") as f:
        return yaml.safe_load(f)


def load_devices():
    devices = []

    for inventory_file in INVENTORY_FILES:
        data = load_yaml(inventory_file)
        devices.extend(data.get("devices", []))

    return devices


def load_credentials():
    return load_yaml(CREDENTIALS_FILE)


def main():
    setup_logging()

    devices = load_devices()
    credentials = load_credentials()

    success_count = 0
    failure_count = 0

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    
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
