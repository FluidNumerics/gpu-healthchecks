#!/bin/bash
#SBATCH --job-name=healthcheck
#SBATCH --nodes=1
#SBATCH --cpus-per-task=48
#SBATCH --mem=100G
#SBATCH --gres=gpu:mi300a:1
#SBATCH --time=01:00:00
#SBATCH -o stdout
#SBATCH -e stderr
#SBATCH --array=0-3

# Load ROCm
module load rocm/6.4.0

# Activate and log conda environment
source "$HOME/miniconda3/etc/profile.d/conda.sh"
conda activate gpu-healthchecks
conda env list

# Run benchmark / health check
python benchmark_gpus.py -H $HOSTNAME