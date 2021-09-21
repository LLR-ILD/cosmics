import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from matplotlib import gridspec


def plot_slices(pos, dim):
    def bins(x):
        x_first = x[0] - (x[1] - x[0]) / 2
        x_last = x[-1] + (x[-1] - x[-2]) / 2
        x_mid = (x[1:] + x[:-1]) / 2
        return np.concatenate(([x_first], x_mid, [x_last]))

    fig_2d = plt.figure(figsize=(10, 3))
    gs = gridspec.GridSpec(1, 4, width_ratios=[1, 1, 1, 0.1])
    for i, (dim1, dim2) in enumerate([("x", "y"), ("x", "z"), ("y", "z")]):
        ax = plt.subplot(gs[i])
        h = ax.hist2d(
            dim[dim1],
            dim[dim2],
            weights=dim["e"],
            bins=(bins(pos[dim1]), bins(pos[dim2])),
            # norm=LogNorm(),
        )
        ax.set_xlabel(dim1)
        ax.set_ylabel(dim2)
    cax = plt.subplot(gs[-1])
    fig_2d.colorbar(h[3], cax=cax)
    cax.set_ylabel("Energy")
    fig_2d.tight_layout()
    return fig_2d


def plot_3d(dim):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(dim["x"], dim["y"], dim["z"], marker="o")
    return fig


def plotly_3d(dim):
    scat_3d = go.Scatter3d(
        x=dim["x"],
        y=dim["y"],
        z=dim["z"],
        mode="markers",
        marker=dict(size=12, color=dim["e"], colorscale="Viridis", opacity=0.8),
        hovertemplate="E: %{text:.2f}<br>(%{x:.1f},%{y:.1f},%{z:.1f})<extra></extra>",
        text=dim["e"],
    )
    fig = go.Figure(data=[scat_3d])
    return fig
