# Quick script to build directories with the following structure:
# nodes/
#   - node1/
#     - gpu0/
#       - current_status
#     - gpu1/
#     - ...
#     - gpu7/
#   - node2/
#   - ...
#   - node256/

import os


def destroy_node_directories(base_path="nodes", num_nodes=256, gpus_per_node=8):
    for node in range(num_nodes):
        node_path = os.path.join(base_path, f"node{node}")
        if os.path.exists(node_path):
            for gpu in range(gpus_per_node):
                gpu_path = os.path.join(node_path, f"gpu{gpu}")
                if os.path.exists(gpu_path):
                    # Remove the current status file
                    status_file = os.path.join(gpu_path, "current_status")
                    if os.path.exists(status_file):
                        os.remove(status_file)
                    # Remove the GPU directory
                    os.rmdir(gpu_path)
            # Remove the node directory
            os.rmdir(node_path)
    if os.path.exists(base_path) and not os.listdir(base_path):
        os.rmdir(base_path)
    print("Node directories destroyed successfully.")


def create_node_directories(base_path="nodes", num_nodes=256, gpus_per_node=8):
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    for node in range(num_nodes):
        node_path = os.path.join(base_path, f"node{node}")
        if not os.path.exists(node_path):
            os.makedirs(node_path)

        for gpu in range(gpus_per_node):
            gpu_path = os.path.join(node_path, f"gpu{gpu}")
            if not os.path.exists(gpu_path):
                os.makedirs(gpu_path)

            # Create a file to store the current status
            status_file = os.path.join(gpu_path, "current_status")
            # Set to overwrite mode
            with open(status_file, "w") as f:
                f.write("2")  # Default status is 2 (Unhealthy)
    print("Node directories created successfully.")


if __name__ == "__main__":
    destroy_node_directories()
    create_node_directories()
