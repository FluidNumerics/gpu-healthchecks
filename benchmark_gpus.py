# Python file to run `rocm-amdgpu-bench` command for GPU health checks.
# and parses the output into a json

# run `rocm-amdgpu-bench` command and parse the output
import subprocess
import argparse

from locodb.directorydb import *


def get_guid_dict():
    """
    Get the GUIDs of all GPUs in the system using `rocm-smi`.
    Returns a dictionary mapping GPU index to GUID.
    """
    result = subprocess.run(
        ["rocm-smi", "--showid"], capture_output=True, text=True, check=True
    )
    output = result.stdout.strip().splitlines()
    guid_dict = {}
    for line in output:
        # Get lines with format
        # GPU[0]          : GUID:                 19794
        if "GUID" in line:
            guid = int(line.split()[3].strip())
            # assume single digit GPU index
            gpu_index = int(line.split()[0][4])
            guid_dict[gpu_index] = guid
    return guid_dict


def benchmark_node(node_name):
    """
    Run the `rocm-amdgpu-bench` command and parse its output.
    Returns a dictionary with GPU health status.
    """

    path_to_bin = "rocm-amdgpu-bench/build/roofline"

    # Run the command
    print("Running rocm-amdgpu-bench...")
    # If temp.log is present, just read from that
    result = subprocess.run(
        [f"./{path_to_bin}"], capture_output=True, text=True, check=True
    )
    output = result.stdout
    print("Finished running rocm-amdgpu-bench.")

    # Convert into list of lines
    # Remove blank lines
    # Remove all lines that contain "%""
    lines = output.splitlines()
    lines = [line for line in lines if line.strip()]
    lines = [line for line in lines if "%" not in line]

    all_gpu_data = []

    for line in lines:
        line_split = line.split()
        if "GPU Device " in line:
            if line_split[2] != "0":
                all_gpu_data.append(gpu_data)  # Save previous GPU data
            gpu_data = {}
            gpu_data["GPU Device"] = int(line_split[2])
            gpu_data["gfx_version"] = line_split[3][1:-1]  # Remove parentheses
            gpu_data["CUs"] = int(line_split[5])
        # Bandwidths
        elif line_split[1] == "BW,":
            bw_type = " ".join(line_split[:2]).replace(",", "")
            # e.g., "HBM BW"
            gpu_data[bw_type] = {
                "workgroupSize": int(line_split[5].split(":")[1][:-1]),
                "workgroups": int(line_split[6].split(":")[1][:-1]),
                "experiments": int(line_split[7].split(":")[1][:-1]),
                "traffic": int(line_split[8].split(":")[1].replace("bytes,", "")),
                "duration": float(line_split[10].split(":")[1].replace("ms,", "")),
                "mean": float(line_split[12].split(":")[1].replace("GB/sec,", "")),
                "stdev": float(line_split[14].split("=")[1].replace("GB/sec", "")),
            }
        # Peak FLOPs
        elif line_split[1] == "FLOPs":
            flops_type = " ".join(line_split[:3]).replace(",", "")
            # e.g., "Peak FLOPs (FP8)"
            gpu_data[flops_type] = {
                "workgroupSize": int(line_split[6].split(":")[1][:-1]),
                "workgroups": int(line_split[7].split(":")[1][:-1]),
                "experiments": int(line_split[8].split(":")[1][:-1]),
                "FLOP": int(line_split[9].split(":")[1][:-1]),
                "duration": float(line_split[10].split(":")[1].replace("ms,", "")),
                "mean": float(line_split[12].split(":")[1].replace("GFLOPS,", "")),
                "stdev": float(line_split[14].split("=")[1].replace("GFLOPS", "")),
            }
        # Peak IOPs
        elif line_split[1] == "IOPs":
            iops_type = " ".join(line_split[:3]).replace(",", "")
            # e.g., "Peak IOPs (INT8)"
            gpu_data[iops_type] = {
                "workgroupSize": int(line_split[6].split(":")[1][:-1]),
                "workgroups": int(line_split[7].split(":")[1][:-1]),
                "experiments": int(line_split[8].split(":")[1][:-1]),
                "IOP": int(line_split[9].split(":")[1][:-1]),
                "duration": float(line_split[10].split(":")[1].replace("ms,", "")),
                "mean": float(line_split[12].split(":")[1].replace("GOPS,", "")),
                "stdev": float(line_split[14].split("=")[1].replace("GOPS", "")),
            }
        # Peak MFMA FLOPs
        elif line_split[1] == "MFMA" and "FLOPs" in line:
            mfma_flops_type = " ".join(line_split[:4]).replace(",", "")
            # e.g., "Peak MFMA FLOPs (FP16)"
            gpu_data[mfma_flops_type] = {
                "workgroupSize": int(line_split[7].split(":")[1][:-1]),
                "workgroups": int(line_split[8].split(":")[1][:-1]),
                "experiments": int(line_split[9].split(":")[1][:-1]),
                "FLOP": int(line_split[10].split(":")[1][:-1]),
                "duration": float(line_split[11].split(":")[1].replace("ms,", "")),
                "mean": float(line_split[13].split(":")[1].replace("GFLOPS,", "")),
                "stdev": float(line_split[15].split("=")[1].replace("GFLOPS", "")),
            }
        # Peak MFMA IOPs
        elif line_split[1] == "MFMA" and "IOPs" in line:
            mfma_iops_type = " ".join(line_split[:4]).replace(",", "")
            # e.g., "Peak MFMA IOPs (INT8)"
            gpu_data[mfma_iops_type] = {
                "workgroupSize": int(line_split[7].split(":")[1][:-1]),
                "workgroups": int(line_split[8].split(":")[1][:-1]),
                "experiments": int(line_split[9].split(":")[1][:-1]),
                "IOP": int(line_split[10].split(":")[1][:-1]),
                "duration": float(line_split[11].split(":")[1].replace("ms,", "")),
                "mean": float(line_split[13].split(":")[1].replace("GOPS,", "")),
                "stdev": float(line_split[15].split("=")[1].replace("GOPS", "")),
            }
        else:
            # Skip any other lines that do not match the expected format
            continue
    # Append the last GPU data
    all_gpu_data.append(gpu_data)

    # file structure:
    # cluster/
    #   <hostname 1>/
    #       cpu/ <- implement later
    #       gpu-<GUID 1>/
    #           1.json
    #           2.json
    #           ...
    #       gpu-<GUID 2>/
    #           1.json
    #           2.json
    #           ...
    #       ...
    #   <hostname 2>/
    #       ...
    #   ...

    # Write results to database
    client = LocoDatabase("cluster")
    # Later, iterate over nodes
    # for node in nodes:
    #     database = client[node]
    # For now, single node
    database = client[node_name]

    guid_dict = get_guid_dict()

    for gpu_data in all_gpu_data:
        collection = database[f"gpu-{guid_dict[gpu_data['GPU Device']]}"]
        collection.insert_one(gpu_data)


def main():
    # input args to get hostname
    parser = argparse.ArgumentParser(description="Benchmark AMD GPUs in a cluster.")
    parser.add_argument(
        "-H",
        "--hostname",
        type=str,
        help="Name of the node to benchmark",
    )
    args = parser.parse_args()

    benchmark_node(args.hostname)


if __name__ == "__main__":
    main()
