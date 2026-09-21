from pathlib import Path

import yaml
from arp_collector import collect_arp

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent


INVENTORY_FILES = [
    ROOT_DIR / "inventory" / "ios-devices.yml",
    ROOT_DIR / "inventory" / "ocnos-devices.yml",
]

CREDENTIALS_FILE = Path.home() / ".config" / "network-automation" / "credentials.yml"
OUTPUT_FILE = BASE_DIR / "output" / "arp_output.txt"


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
    devices = load_devices()
    credentials = load_credentials()


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

            except Exception as exc:
                outfile.write(f"\n===== {device['name']} =====\n")
                outfile.write(f"ERROR: {exc}\n")

                print(f"ERROR connecting to {device['name']}: {exc}")

    print(f"ARP collection completed successfully")
    print(f"Output written to: {OUTPUT_FILE}")



if __name__ == "__main__":
    main()
