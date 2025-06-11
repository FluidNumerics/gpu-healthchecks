# GPU Health Check Dashboard
Copyright 2025 Fluid Numerics

## Installation
Create and activate conda env
```bash
conda create -n gpu-healthchecks python=3.11
conda activate gpu-healthchecks
pip install -r requirements.txt
```

Build `rocm-amdgpu-bench`:
```bash
mkdir rocm-amdgpu-bench/build
cd rocm-amdgpu-bench/build
cmake ..
make
```

## Running
To run during an interactive job, just run
```bash
python benchmark_gpus.py
```

To submit a batch job on a single node (e.g., `nicholson`), we provide an example batch script at `slurm/nicholson.sh`.

