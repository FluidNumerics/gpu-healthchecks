import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from time import sleep
import os

# Infra
num_nodes = 256
gpus_per_node = 8

grid_shape = (32, 64)
simulate_health_check_time = 2

# Map status to colors
status_colors = {
    0: "#2ecc71",  # Green
    1: "#f1c40f",  # Yellow
    2: "#e74c3c",  # Red
}

status_dict = {
    0: "Healthy",
    1: "Undergoing Health Check",
    2: "Unhealthy",
}

square_width = 16
square_corner_radius = 2

gpu_array = [
    {
        "id": i * gpus_per_node + j,
        "node": i,
        "gpu": j,
        "status": 2,  # Default status is 2 (Unhealthy)
    }
    for i in range(num_nodes)
    for j in range(gpus_per_node)
]


def node_gpu_path(node, gpu):
    base_path = "nodes"
    node_path = os.path.join(base_path, f"node{node}")
    gpu_path = os.path.join(node_path, f"gpu{gpu}")
    return gpu_path


def check_status(node, gpu):
    gpu_path = node_gpu_path(node, gpu)
    status_file = os.path.join(gpu_path, "current_status")

    if not os.path.exists(status_file):
        return 2  # Default to Unhealthy if status file doesn't exist

    with open(status_file, "r") as f:
        content = f.read().strip()
        if content.isdigit():
            status = int(content)
        else:
            print(
                f"Invalid content in status file for Node {node}, GPU {gpu}: {content}"
            )
            print("Possibly trying to read during status change.")
            # Retry after a short delay
            sleep(0.1)
            return check_status(node, gpu)

    return status


def update_gpu_array():
    for device in gpu_array:
        node = device["node"]
        gpu = device["gpu"]
        device["status"] = check_status(node, gpu)


# Main
app = dash.Dash(__name__, update_title=None)
app.title = "GPU Health Dashboard"

app.layout = html.Div(
    [
        html.H1(
            "GPU Health Monitoring Dashboard",
            style={"textAlign": "center", "color": "#ecf0f1"},
        ),
        # Legend for GPU status
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            style={
                                "width": f"{square_width}px",
                                "height": f"{square_width}px",
                                "backgroundColor": status_colors[status],
                                "borderRadius": f"{square_corner_radius}px",
                                "display": "inline-block",
                                "marginRight": "10px",
                            },
                        ),
                        html.Span(
                            status_dict[status],
                            style={
                                "lineHeight": f"{square_width}px",
                                "verticalAlign": "top",
                            },
                        ),
                    ],
                    style={"display": "inline-block", "marginRight": "20px"},
                )
                for status in status_dict
            ],
            style={"textAlign": "center", "color": "#ecf0f1", "marginBottom": "20px"},
        ),
        # Grid for GPU status
        html.Div(id="gpu-grid"),
        dcc.Interval(id="interval", interval=1000, n_intervals=0),
    ],
    style={"backgroundColor": "#1e1e1e", "minHeight": "100vh", "padding": "40px"},
)


@app.callback(
    Output("gpu-grid", "children"),
    [Input("interval", "n_intervals")],
)
def update_gpu_grid(n):
    update_gpu_array()

    # Group GPUs by node
    grouped_by_node = {}
    for device in gpu_array:
        node = device["node"]
        if node not in grouped_by_node:
            grouped_by_node[node] = []
        grouped_by_node[node].append(device)

    # Create containers for each node
    return [
        html.Div(
            children=[
                html.Div(  # This div will hold the node number and the node container
                    children=[
                        # Node number OUTSIDE the box, but centered above it
                        html.Div(
                            f"{node}",
                            style={
                                "textAlign": "center",
                                "fontSize": "16px",
                                "fontWeight": "bold",
                                "marginBottom": "5px",  # Adjust margin as needed
                                "color": "#ecf0f1",
                                "width": f"{2 * square_width}px",  # Ensure it's the same width as the node container for centering
                            },
                        ),
                        # Node container
                        html.Div(
                            children=[
                                # Individual GPU squares
                                html.Div(
                                    title=f"Node: \t{device['node']}\nGPU: \t{device['gpu']}\nStatus: \t{status_dict[device['status']]} ({device['status']})",
                                    style={
                                        "width": f"{square_width}px",
                                        "height": f"{square_width}px",
                                        "borderRadius": f"{square_corner_radius}px",
                                        "backgroundColor": status_colors[
                                            device["status"]
                                        ],
                                        "transition": "background-color 0.3s ease",
                                        "margin": f"{square_width/8}px",
                                        "display": "block",
                                    },
                                )
                                for device in grouped_by_node[node]
                            ],
                            style={
                                "border": f"{square_width / 8}px solid #ecf0f1",
                                "borderRadius": f"{2 * square_corner_radius}px",
                                "padding": f"{square_width/4}px",
                                "width": f"{2 * square_width}px",
                                "boxSizing": "border-box",
                                # Removed margin here, as the parent div will handle spacing between node groups
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "flexDirection": "column",  # Arrange children (number and container) vertically
                        "alignItems": "center",  # Center items horizontally
                        "margin": f"{square_width/4}px",  # Apply margin to this outer div for spacing between node groups
                    },
                )
                for node in grouped_by_node
            ],
            # Outermost div should be centered horizontally
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(32, auto)",  # Adjust minmax as needed
                "justifyItems": "center",
                "marginLeft": "144px",
                "marginRight": "144px",
            },
        )
    ]


# def update_gpu_grid(n):
#     update_gpu_array()
#     return [
#         html.Div(
#             title=f"Node: \t{device['node']}\nGPU: \t{device['gpu']}\nStatus: \t{status_dict[device['status']]} ({device['status']})",
#             style={
#                 "width": f"{square_width}px",
#                 "height": f"{square_width}px",
#                 "borderRadius": f"{square_corner_radius}px",
#                 "backgroundColor": status_colors[device["status"]],
#                 "transition": "background-color 0.3s ease",
#             },
#         )
#         for device in gpu_array
#     ]


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
