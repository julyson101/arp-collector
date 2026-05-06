import yaml
from arp_collector import collect_arp
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent


INVENTORY_FILE = ROOT_DIR / "inventory" / "devices.yml"
OUTPUT_FILE = "output/arp_output.txt"


def load_devices():
    with open(INVENTORY_FILE, "r") as f:
        return yaml.safe_load(f)["devices"]


def main():
    devices = load_devices()

    with open(OUTPUT_FILE, "w") as outfile:
        for device in devices:
            arp_output = collect_arp(device)

            outfile.write(f"\n===== {device['name']} =====\n")
            outfile.write(arp_output)
            outfile.write("\n")

    print("ARP collection completed successfully")
            

if __name__ == "__main__":
    main()

        
