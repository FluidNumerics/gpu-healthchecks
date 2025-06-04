# Python file to run `rocm-amdgpu-bench` command for GPU health checks.
# and parses the output into a json

# run `rocm-amdgpu-bench` command and parse the output
import subprocess
import json
import os


def rocm_amdgpu_bench():
    """
    Run the `rocm-amdgpu-bench` command and parse its output.
    Returns a dictionary with GPU health status.
    """

    # Run the command
    result = subprocess.run(
        ["./rocm-amdgpu-bench"], capture_output=True, text=True, check=True
    )

    # Parse the output
    output = result.stdout.strip()
    print(output)

    parsed_data = {
        # Device information
        "GPU Device": "",
        "gfx_version": "",
        "CUs": 0,
        # Bandwidths
        "HBM BW": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "traffic": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "MALL BW": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "traffic": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "L2 BW": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "traffic": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "L1 BW": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "traffic": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "LDS BW": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "traffic": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        # Peak FLOPs
        "Peak FLOPs (FP8)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "FLOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "Peak FLOPs (FP16)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "FLOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "Peak FLOPs (BF16)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "FLOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "Peak FLOPs (FP32)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "FLOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "Peak FLOPs (FP64)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "FLOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        # Peak IOPs
        "Peak IOPs (INT8)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "IOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "Peak IOPs (INT32)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "IOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "Peak IOPs (INT64)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "IOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        # Peak MFMA FLOPs
        "Peak MFMA FLOPs (F8)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "FLOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "Peak MFMA FLOPs (F16)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "FLOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "Peak MFMA FLOPs (BF16)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "FLOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "Peak MFMA FLOPs (F32)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "FLOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        "Peak MFMA FLOPs (F64)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "FLOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
        # Peak MFMA IOPs
        "Peak MFMA IOPs (I8)": {
            "workgroupSize": 0,
            "workgroups": 0,
            "experiments": 0,
            "IOP": 0,
            "duration": 0.0,
            "mean": 0.0,
            "stdev": 0.0,
        },
    }

    # Parse output
    lines = output.splitlines()

    # Parse first line into GPU Device, gfx_version, and CUs
    first_line = lines[0].strip()

    # Parse remaining lines (every other) into respective fields

    # return health_data


# Example output from `rocm-amdgpu-bench`:
# GPU Device 0 (gfx942) with 228 CUs: Profiling...
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# HBM BW, GPU ID: 0, workgroupSize:256, workgroups:6225920, experiments:100, traffic:25501368320 bytes, duration:6.7 ms, mean:3797.8 GB/sec, stdev=10.0 GB/sec
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# MALL BW, GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, traffic:2611340115968 bytes, duration:532.7 ms, mean:4937.4 GB/sec, stdev=27.0 GB/sec
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# L2 BW, GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, traffic:1632087572480 bytes, duration:76.6 ms, mean:21305.7 GB/sec, stdev=11.3 GB/sec
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# L1 BW, GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, traffic:127506841600 bytes, duration:4.4 ms, mean:28771.9 GB/sec, stdev=15.4 GB/sec
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# LDS BW, GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, traffic:79691776000 bytes, duration:1.6 ms, mean:51072.2 GB/sec, stdev=61.3 GB/sec
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak FLOPs (FP8), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, FLOP:1081258016768, duration:17.3 ms, mean:62590.6 GFLOPS, stdev=8.6 GFLOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak FLOPs (FP16), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, FLOP:530428461056, duration:17.8 ms, mean:29780.7 GFLOPS, stdev=5.1 GFLOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak FLOPs (BF16), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, FLOP:530428461056, duration:115.225 ms, mean:4602.3 GFLOPS, stdev=1.0 GFLOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak FLOPs (FP32), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, FLOP:265214230528, duration:2.312 ms, mean:114487.4 GFLOPS, stdev=496.6 GFLOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak FLOPs (FP64), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, FLOP:122406567936, duration:1.3 ms, mean:94764.0 GFLOPS, stdev=947.0 GFLOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak IOPs (INT8), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, IOP:1081258016768, duration:17.3 ms, mean:62565.1 GOPS, stdev=11.5 GOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak IOPs (INT32), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, IOP:265214230528, duration:4.3 ms, mean:61493.5 GOPS, stdev=19.0 GOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak IOPs (INT64), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, IOP:122406567936, duration:7.6 ms, mean:16198.5 GOPS, stdev=4.2 GOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak MFMA FLOPs (F8), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, FLOP:10200547328000, duration:6.0 ms, mean:1699876.8 GFLOPS, stdev=4738.4 GFLOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak MFMA FLOPs (F16), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, FLOP:5100273664000, duration:6.1 ms, mean:833913.8 GFLOPS, stdev=1111.2 GFLOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak MFMA FLOPs (BF16), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, FLOP:2550136832000, duration:5.5 ms, mean:460655.1 GFLOPS, stdev=1029.9 GFLOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak MFMA FLOPs (F32), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, FLOP:1275068416000, duration:10.9 ms, mean:117016.3 GFLOPS, stdev=140.3 GFLOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak MFMA FLOPs (F64), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, FLOP:637534208000, duration:5.4 ms, mean:117357.3 GFLOPS, stdev=68.1 GFLOPS
#  99% [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| ]
# Peak MFMA IOPs (I8), GPU ID: 0, workgroupSize:256, workgroups:38912, experiments:100, IOP:5100273664000, duration:5.8 ms, mean:886390.2 GOPS, stdev=1867.2 GOPS
