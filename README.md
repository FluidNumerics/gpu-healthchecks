# GPU Health Check Dashboard

## Installation
Create and activate conda env
```bash
conda create -n gpu-dashbaord-env python=3.11
conda activate gpu-dashboard-env
```

Pip install `requirements.txt`
```bash
pip install -r requirements.txt
```

## Basic Usage

Reset all node statuses with `reset_nodes.py`.
```bash
python reset_nodes.py
```

Run the health check on all nodes
```bash
python health_check.py --all
```

Run the dashboard
```bash
python app.py
```

