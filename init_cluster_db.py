# Initializes the cluster database
# MUST BE RUN AS ROOT
# Assigns directory IDs from UUIDs of GPUs per node

import os
import subprocess


def get_guids():
    """
    Get the GUIDs of all GPUs in the system using `rocm-smi`.
    Returns a list of GUIDs.
    """
    result = subprocess.run(
        ["rocm-smi", "--showid"], capture_output=True, text=True, check=True
    )
    output = result.stdout.strip().splitlines()
    guids = []
    for line in output:
        # Get lines with format
        # GPU[0]          : GUID:                 19794
        if "GUID" in line:
            guid = int(line.split()[3].strip())
            guids.append(guid)
    return guids


# Make cluster/
if not os.path.exists("cluster"):
    os.makedirs("cluster")

# Make node directories
num_nodes = 1

for i in range(num_nodes):
    node_dir = f"cluster/node{i}"
    if not os.path.exists(node_dir):
        os.makedirs(node_dir)

# Make GPU directories
for i in range(num_nodes):
    node_dir = f"cluster/node{i}"
    guids = get_guids()

    for guid in guids:
        gpu_dir = f"{node_dir}/gpu-{guid}"
        if not os.path.exists(gpu_dir):
            os.makedirs(gpu_dir)
