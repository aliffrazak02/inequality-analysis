"""
visualise.py
============
Shared plotting utilities for the inequality-analysis notebooks.

Provides:
  - COLOR_MAP      : project colour palette dict
  - EAST           : set of East Malaysia state names
  - state_colors() : return a per-row colour list from a DataFrame
  - sdi_colors()   : colour list for SDI charts (double-deprivation aware)
  - save_fig()     : save a figure to the figures/ directory
  - style_ax()     : apply consistent axis formatting
  - legend_patches(): return standard region legend handles
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch

from scripts.config import FIGURES

# ---------------------------------------------------------------------------
# Palette & constants
# ---------------------------------------------------------------------------

COLOR_MAP: dict[str, str] = {
    "west":     "#4c72b0",   # Peninsular Malaysia (blue)
    "east":     "#e07b39",   # East Malaysia (orange)
    "capital":  "#2ca02c",   # W.P. Kuala Lumpur (green)
    "deprived": "#d62728",   # Double-deprived states (red)
    "grey":     "#cccccc",   # Background / faded lines
}

EAST: set[str] = {"Sabah", "Sarawak", "W.P. Labuan"}

HIGHLIGHT_STATES = ["W.P. Kuala Lumpur", "Selangor", "Kelantan", "Sabah", "Sarawak"]
HIGHLIGHT_COLORS = ["#2ca02c", "#4c72b0", "#c44e52", "#8172b3", "#64b5cd"]


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def state_colors(states: list[str] | "pd.Series") -> list[str]:
    """Return a colour per state name using the project palette.

    East Malaysia → orange, W.P. Kuala Lumpur → green, all others → blue.
    """
    result = []
    for s in states:
        if s in EAST:
            result.append(COLOR_MAP["east"])
        elif s == "W.P. Kuala Lumpur":
            result.append(COLOR_MAP["capital"])
        else:
            result.append(COLOR_MAP["west"])
    return result


def sdi_colors(df: "pd.DataFrame") -> list[str]:
    """Return a colour per row for SDI bar charts.

    Priority: double_deprivation → red; KUL → green; East → orange; else → blue.
    """
    result = []
    for _, row in df.iterrows():
        if row.get("double_deprivation", False):
            result.append(COLOR_MAP["deprived"])
        elif row["state"] == "W.P. Kuala Lumpur":
            result.append(COLOR_MAP["capital"])
        elif row["state"] in EAST:
            result.append(COLOR_MAP["east"])
        else:
            result.append(COLOR_MAP["west"])
    return result


# ---------------------------------------------------------------------------
# Legend helpers
# ---------------------------------------------------------------------------

def legend_patches(include_deprived: bool = False) -> list[Patch]:
    """Standard region legend handles."""
    handles = [
        Patch(color=COLOR_MAP["west"],    label="Peninsular Malaysia"),
        Patch(color=COLOR_MAP["east"],    label="East Malaysia"),
        Patch(color=COLOR_MAP["capital"], label="W.P. Kuala Lumpur *"),
    ]
    if include_deprived:
        handles.insert(0, Patch(color=COLOR_MAP["deprived"], label="Double deprived (★)"))
    return handles


# ---------------------------------------------------------------------------
# Figure I/O
# ---------------------------------------------------------------------------

def save_fig(fig: "plt.Figure", name: str, tight: bool = True) -> None:
    """Save *fig* to the project figures/ directory as a PNG.

    Parameters
    ----------
    fig:   matplotlib Figure to save
    name:  filename without extension, e.g. ``'fig1_income_ranking'``
    tight: call ``bbox_inches='tight'`` (default True)
    """
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / f"{name}.png"
    kwargs = {"bbox_inches": "tight"} if tight else {}
    fig.savefig(path, **kwargs)
    print(f"Saved {path.name}")


# ---------------------------------------------------------------------------
# Axis formatting
# ---------------------------------------------------------------------------

def style_ax(
    ax: "plt.Axes",
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    rm_format: str | None = None,
    pct_format: bool = False,
) -> None:
    """Apply consistent axis styling.

    Parameters
    ----------
    ax          : matplotlib Axes
    title       : bold title text
    xlabel      : x-axis label
    ylabel      : y-axis label
    rm_format   : if ``'x'`` or ``'y'``, format that axis as ``RM {:,.0f}``
    pct_format  : if True, format x-axis as percentage with one decimal place
    """
    if title:
        ax.set_title(title, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    if rm_format == "x":
        ax.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"RM {x:,.0f}")
        )
    elif rm_format == "y":
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"RM {x:,.0f}")
        )

    if pct_format:
        ax.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"{x:.1f}%")
        )
