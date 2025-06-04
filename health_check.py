from random import randint

# Iterate over nodes directory.
import os
from time import sleep

import argparse

num_nodes = 256
gpus_per_node = 8

status_dict = {
    0: "Healthy",
    1: "Undergoing Health Check",
    2: "Unhealthy",
}

sim_health_check_time = 4


####################
# HELPER FUNCTIONS #
####################
def hc_dummy(status_file):
    """
    Dummy health check function that simulates a health check.
    It randomly returns either 0 (healthy) or 2 (unhealthy) after a delay.
    """
    sleep(sim_health_check_time)  # Simulate a delay for the health check
    outcome = randint(0, 100)
    status = 0 if outcome < 90 else 2  # Healthy if outcome < 90, Unhealthy otherwise
    with open(status_file, "w") as f:
        f.write(str(status))

    return status


def hc_rocm_amdgpu_bench(status_file):
    """
    ROCm AMD GPU benchmark health check.
    Calls `rocm_amdgpu_bench` command to check GPU health.
    """
    # For now, use sister binary `./rocm-amdgpu-bench`
    # Parse output


hc_type_dict = {
    "dummy": hc_dummy,
}


###########
# LOGGING #
###########
class HealthCheckLogger:
    def __init__(self, log_file="health_check.log", printout=True):
        self.log_file = log_file
        self.printout = printout

    def log(self, message):
        with open(self.log_file, "a") as f:
            f.write(f"{message}\n")
        if self.printout:
            print(message)

    def log_gpu_status(self, node, gpu, status):
        message = f"Node: {node}, GPU: {gpu}, Status: {status} ({status_dict[status]})"
        self.log(message)

    def log_health_check(self, hc_type, node, gpu):
        message = f"Health Check Type: {hc_type}, Node: {node}, GPU: {gpu}"
        self.log(message)


###############################
# Core Health Check
###############################
class HealthCheck:
    def __init__(self, logger=None):
        self.logger = logger or HealthCheckLogger()
        self.base_path = "nodes"

    # Perform health check for all GPUs on all nodes
    def health_check(self, hc_type, node, gpu):
        node_path = os.path.join(self.base_path, f"node{node}")
        gpu_path = os.path.join(node_path, f"gpu{gpu}")
        status_file = os.path.join(gpu_path, "current_status")

        with open(status_file, "w") as f:
            f.write(str(1))  # Set to 1 during health check

        # sleep(sim_health_check_time)  # Simulate a delay for the health check

        self.logger.log_health_check(hc_type, node, gpu)

        # Switch cases for hc_type
        if hc_type == "dummy":
            status = hc_dummy(status_file)
        else:
            unknown_hc_type_message = f"Unknown health check type: {hc_type}"
            self.logger.log(unknown_hc_type_message)
            raise ValueError(unknown_hc_type_message)

        with open(status_file, "w") as f:
            f.write(str(status))

        self.logger.log_gpu_status(node, gpu, status)

    # Check all GPUs on all nodes
    def check_all(self, hc_type):
        num_nodes_found = len(os.listdir(self.base_path))

        # Check if number of nodes matches num_nodes
        if num_nodes_found != num_nodes:
            print(f"Expected {num_nodes} nodes, found {num_nodes_found}.")
            return

        for node in range(num_nodes_found):
            self.check_one_node(hc_type, node)

    # Check all GPUs on a specific node
    def check_one_node(self, hc_type, node):
        node_path = os.path.join(self.base_path, f"node{node}")
        gpu_directories = len(os.listdir(node_path))

        # Check if number of GPUs matches gpus_per_node
        if gpu_directories != gpus_per_node:
            print(f"Node {node} has {gpu_directories} GPUs, expected {gpus_per_node}.")
            return

        for gpu in range(gpus_per_node):
            self.check_one_gpu(hc_type, node, gpu)

    # Check one GPU
    def check_one_gpu(self, hc_type, node, gpu):
        self.health_check(hc_type, node, gpu)


########
# MAIN #
########
def main():
    parser = argparse.ArgumentParser(
        description="Check GPU health status across nodes."
    )
    # Add arguments for node and GPU selection
    parser.add_argument(
        "--all",
        action="store_true",
        help="Check health status for all nodes and GPUs.",
    )
    parser.add_argument(
        "--node",
        type=int,
        help="Specify a node to check health status. If omitted, all nodes are checked.",
    )
    parser.add_argument(
        "--gpu",
        type=int,
        help="Specify a GPU to check health status. Requires --node to be specified.",
    )
    # Add argument to specify which type of health check to perform
    parser.add_argument(
        "--type",
        type=str,
        default="dummy",
        choices=["dummy"],
        help="Specify the type of health check to perform (default: dummy).",
    )

    args = parser.parse_args()

    # Determine the scope of the health check
    health_checker = HealthCheck()

    if args.node is not None and args.gpu is not None:
        health_checker.check_one_gpu(args.type, args.node, args.gpu)
    elif args.node is not None:
        health_checker.check_one_node(args.type, args.node)
    elif args.all:
        health_checker.check_all(args.type)
    else:
        print(
            "Please specify --all, --node <node_id>, or both --node <node_id> and --gpu <gpu_id>."
        )


if __name__ == "__main__":
    main()
