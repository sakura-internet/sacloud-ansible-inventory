#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys
from os import environ

# for exclude hosts, check tags
filtering_tags = ["__with_sacloud_inventory"]

# override filtering tags.
# example for `SACLOUD_INVENTORY_FILTER_TAGS=__with_sacloud_inventory,cluster1 ./sacloud_inventory.py`
override_filter_tags = environ.get("SACLOUD_INVENTORY_FILTER_TAGS", None)
if override_filter_tags is not None:
    filtering_tags = override_filter_tags.split(",")

# Install usacloud
# https://sacloud.github.io/usacloud/start_guide/
is_usacloud_installed = None
if sys.version_info.major == 3 and sys.version_info.minor > 3:
    import shutil

    is_usacloud_installed = shutil.which("usacloud")
else:  # python < 3.4
    import distutils.spawn

    is_usacloud_installed = distutils.spawn.find_executable("usacloud")
if not is_usacloud_installed:
    subprocess.check_output("curl -fsSL https://releases.usacloud.jp/usacloud/repos/install.sh | bash", shell=True)

parser = argparse.ArgumentParser(description="Ansible dynamic inventory for sakura cloud")
parser.add_argument("--list", action="store_true", default=True,
                    help="List all active Droplets as Ansible inventory (default: True)")
parser.add_argument("--host", action="store", help="Get all Ansible inventory variables about a specific Droplet")
args = parser.parse_args()


def convert_host_var(instance):
    # parse description and extract host options
    host_options = {}
    description = instance["Description"]
    if description != "":
        try:
            host_options = json.loads(description)["sacloud_inventory"]
        except:
            pass

    # detect ansible_host vars
    interfaces = instance["Interfaces"]
    ahost = instance["Name"]
    if "hostname_type" in host_options:
        if host_options["hostname_type"] == "instance_name":
            pass
        else:
            n = re.findall(r"^nic(\d)_ip$", host_options["hostname_type"])  # like "nic1_ip"
            if len(n) == 1:
                if_info = interfaces[int(n[0])]
                if "UserIPAddress" in if_info:
                    ahost = str(if_info["UserIPAddress"])
                if "IPAddress" in if_info:
                    ahost = str(if_info["IPAddress"])

    hostvar = {
        "ansible_host": ahost,
        "name": instance["Name"],
        "sacloud_id": instance["ID"],
        "sacloud_tags": instance["Tags"],
        "sacloud_interfaces": [ifc for ifc in instance["Interfaces"]],
        "sacloud_disks": [d for d in instance["Disks"]],
    }

    # append additional host vars
    if "host_vers" in host_options:
        hostvar.update(host_options["host_vers"])

    return hostvar


if args.host is not None or args.host == "":
    s = subprocess.check_output("usacloud server read --out json {}".format(args.host), shell=True)
    result = json.loads(s.decode("utf-8"))[0]
    hostvar = convert_host_var(result)
    print(json.dumps(hostvar, sort_keys=True, indent=2, separators=(",", ": ")))
elif args.list:
    s = subprocess.check_output("usacloud server list --out json --max=1000", shell=True)
    result = json.loads(s.decode("utf-8"))

    inventory = {}
    hostvars = {}
    for instance in result:
        # filter hosts by tags
        if not all(filter_term in instance["Tags"] for filter_term in filtering_tags):
            continue

        zone = instance["Zone"]["Name"]
        host = instance["Name"]
        if zone not in inventory.keys():
            inventory[zone] = []
        inventory[zone].append(host)

        for tag in instance["Tags"]:
            if tag not in inventory.keys():
                inventory[tag] = []
            inventory[tag].append(host)

        hostvars[host] = convert_host_var(instance)

    for k, v in inventory.items():
        v.sort()

    inventory["_meta"] = {"hostvars": hostvars}

    print(json.dumps(inventory, sort_keys=True, indent=2, separators=(",", ": ")))
