# Python file to run `rocm-amdgpu-bench` command for GPU health checks.
# and parses the output into a json

import subprocess
import socket

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


def benchmark_node():
    """
    Run the `rocm-amdgpu-bench` command and parse its output.
    Returns a dictionary with GPU health status.
    """

    path_to_bin = "rocm-amdgpu-bench/build/roofline"
    node_name = socket.gethostname()

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

    for index, guid in guid_dict.items():
        collection = database[f"gpu-{guid_dict[gpu_data['GPU Device']]}"]

        metrics_list = [
            "HBM BW",
            "MALL BW",
            "L2 BW",
            "L1 BW",
            "LDS BW",
            "Peak FLOPs (FP8)",
            "Peak FLOPs (FP16)",
            "Peak FLOPs (BF16)",
            "Peak FLOPs (FP32)",
            "Peak FLOPs (FP64)",
            "Peak IOPs (INT8)",
            "Peak IOPs (INT32)",
            "Peak IOPs (INT64)",
            "Peak MFMA FLOPs (F4)",
            "Peak MFMA FLOPs (F6)",
            "Peak MFMA FLOPs (F8)",
            "Peak MFMA FLOPs (F16)",
            "Peak MFMA FLOPs (BF16)",
            "Peak MFMA FLOPs (F32)",
            "Peak MFMA FLOPs (F64)",
            "Peak MFMA IOPs (I8)",
        ]

        gpu_stats = {
            "mean_difference": {},
            "stdev": {},
            "z_score": {},
        }

        gpu_health = {
            "Outlier": False,
            "Outlier Metrics": [],
            "Unhealthy": False,
            "Unhealthy Metrics": [],
            "Message": "",
        }

        population_benchmarks = collection.find()
        population = len(population_benchmarks)
        for metric in metrics_list:
            if population != 0:
                population_mean = (
                    sum(
                        [
                            benchmark["metrics"][metric]["mean"]
                            for benchmark in population_benchmarks
                        ]
                    )
                    / population
                )
                population_stdev = (
                    sum(
                        [
                            (benchmark["metrics"][metric]["mean"] - population_mean)
                            ** 2
                            for benchmark in population_benchmarks
                        ]
                    )
                    / population
                ) ** 0.5
                population_z_score = (
                    (gpu_data[metric]["mean"] - population_mean) / population_stdev
                    if population_stdev != 0
                    else 0
                )
            else:
                population_mean = 0
                population_stdev = 0
                population_z_score = 0

            gpu_stats["mean_difference"][metric] = (
                gpu_data[metric]["mean"] - population_mean
            )
            gpu_stats["stdev"][metric] = population_stdev
            gpu_stats["z_score"][metric] = population_z_score

            if abs(gpu_data[metric]["mean"] - population_mean) > 3 * population_stdev:
                # Mark as outlier if check lands past 3 sigma
                # Note: This does not necessarily mean the GPU is unhealthy
                # (should correlate to 0.3% of all health checks)
                if population > 30:
                    gpu_health["Outlier"] = True
                    gpu_health["Outlier Metrics"].append(metric)
                    # Mark as unhealthy if the metric is >= 5 sigma
                    # (should correlate to 0.00006% of health checks)
                    if (
                        abs(gpu_data[metric]["mean"] - population_mean)
                        > 5 * population_stdev
                    ):
                        gpu_health["Unhealthy"] = True
                        gpu_health["Unhealthy Metrics"].append(metric)
                        gpu_health["Message"] = (
                            "Health metric exceeds 5 sigma threshold. Likely unhealthy GPU."
                        )
                else:
                    gpu_health["Message"] = (
                        f"Population size ({population}) is too small to determine outliers."
                    )

    for gpu_data in all_gpu_data:
        collection = database[f"gpu-{guid_dict[gpu_data['GPU Device']]}"]
        metrics = {
            "metrics": gpu_data,
            "stats": gpu_stats,
            "health": gpu_health,
        }
        collection.insert_one(metrics)


def main():
    for _ in range(20):
        benchmark_node()


if __name__ == "__main__":
    main()
