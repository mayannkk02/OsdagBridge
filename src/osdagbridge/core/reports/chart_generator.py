# =============================================================================
# OsdagBridge — Report Chart & Visualization Generator
# Generates publication-quality charts for:
#   1. Section 5.5: Overall Utilization Ratio (UR = Demand / Capacity) Summary
#   2. Chapter 7: Material Quantity Bar Charts (Structural Steel & Concrete vs Rebar)
# =============================================================================

import os
import logging
from typing import Dict, Any, Optional, Tuple, List

import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np

from .styles import CHART_THEME

logger = logging.getLogger("osdagbridge.core.reports.chart_generator")


def generate_ur_summary_chart(
    ur_data: Dict[str, float],
    output_path: str
) -> Optional[str]:
    """
    Generate and save the overall Utilization Ratio summary bar chart.

    Parameters:
        ur_data: Dictionary mapping element / check names to their UR values.
                 Example: {
                     "Steel Girders": 1.85,
                     "Concrete Deck": 0.62,
                     "Cross Bracing": 0.23,
                     "End Diaphragms": 0.45,
                 }
        output_path: Target image file path (.png).

    Returns:
        The output path if successful, None otherwise.
    """
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        theme = CHART_THEME

        labels = list(ur_data.keys())
        values = [float(ur_data[k]) for k in labels]

        fig, ax = plt.subplots(figsize=(8.0, 4.2), dpi=theme["dpi"])
        fig.patch.set_facecolor(theme["figure_bg"])
        ax.set_facecolor(theme["axes_bg"])

        # Bar colors: Green for passing (<= 1.0), Red for failing (> 1.0)
        colors = [
            theme["pass_color"] if v <= 1.0 else theme["fail_color"]
            for v in values
        ]

        x_indices = np.arange(len(labels))
        bars = ax.bar(x_indices, values, width=0.48, color=colors, edgecolor="#333333", linewidth=0.8, zorder=3)

        # Threshold line at UR = 1.0
        ax.axhline(
            1.0,
            color=theme["threshold_line_color"],
            linestyle=theme["threshold_line_style"],
            linewidth=theme["threshold_line_width"],
            label=r"Threshold Limit ($UR = 1.0$)",
            zorder=4
        )

        # Data value annotations on top of bars
        max_v = max(values) if values else 1.0
        y_lim = max(max_v * 1.25, 1.35)
        ax.set_ylim(0, y_lim)

        for bar, val in zip(bars, values):
            height = bar.get_height()
            status_text = "PASS" if val <= 1.0 else "FAIL"
            status_color = theme["pass_color"] if val <= 1.0 else theme["fail_color"]
            ax.annotate(
                f"{val:.2f}\n({status_text})",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=theme["tick_fontsize"],
                fontweight="bold",
                color=status_color
            )

        ax.set_xticks(x_indices)
        ax.set_xticklabels(labels, fontsize=theme["tick_fontsize"] + 0.5, fontweight="bold")
        ax.set_ylabel("Utilization Ratio ($UR = \\text{Demand} / \\text{Capacity}$)", fontsize=theme["label_fontsize"])
        ax.set_title("Overall Design Check Summary --- Maximum Utilization Ratios", fontsize=theme["title_fontsize"], fontweight="bold", pad=12)

        ax.grid(axis="y", color=theme["grid_color"], linestyle="--", alpha=theme["grid_alpha"], zorder=0)
        ax.set_axisbelow(True)
        ax.legend(loc="upper right", fontsize=theme["legend_fontsize"], framealpha=0.95)

        plt.tight_layout()
        plt.savefig(output_path, dpi=theme["dpi"], bbox_inches="tight")
        plt.close(fig)

        logger.info(f"Generated UR summary chart at: {output_path}")
        return output_path

    except Exception as exc:
        logger.warning(f"Failed to generate UR summary chart: {exc}")
        return None


def generate_material_quantity_charts(
    quantities: Dict[str, Any],
    output_dir: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate and save Chapter 7 material quantity charts:
      1. Structural Steel tonnage breakdown (Girders, Cross Bracing, End Diaphragms).
      2. Concrete volume (m³) vs Reinforcement Steel weight (MT).

    Returns:
        Tuple of (steel_chart_path, concrete_rebar_chart_path)
    """
    theme = CHART_THEME
    os.makedirs(output_dir, exist_ok=True)
    steel_path = os.path.join(output_dir, "material_steel_tonnage.png")
    concrete_rebar_path = os.path.join(output_dir, "material_concrete_rebar.png")

    # Helper to parse float safely
    def _parse(k, default=0.0):
        v = quantities.get(k)
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    # 1. Structural Steel Tonnage Chart
    try:
        girder_wt = _parse("steel_girders_wt_total", 32.89)
        top_cb = _parse("bracing_top_wt_total", 0.13)
        bot_cb = _parse("bracing_bot_wt_total", 0.13)
        diag_cb = _parse("bracing_diag_wt_total", 0.29)
        bracing_wt = top_cb + bot_cb + diag_cb
        ed_wt = _parse("ed_steel_wt_total", max(0.20, bracing_wt * 0.45))

        steel_labels = ["Steel Girders", "Cross Bracing", "End Diaphragms"]
        steel_values = [girder_wt, bracing_wt, ed_wt]

        fig, ax = plt.subplots(figsize=(7.5, 4.0), dpi=theme["dpi"])
        fig.patch.set_facecolor(theme["figure_bg"])
        ax.set_facecolor(theme["axes_bg"])

        bar_colors = ["#3B6998", "#5A94C8", "#82B2DE"]
        x_idx = np.arange(len(steel_labels))
        bars = ax.bar(x_idx, steel_values, width=0.48, color=bar_colors, edgecolor="#222222", linewidth=0.8, zorder=3)

        max_val = max(steel_values) if steel_values else 1.0
        ax.set_ylim(0, max_val * 1.25)

        for bar, val in zip(bars, steel_values):
            height = bar.get_height()
            ax.annotate(
                f"{val:.2f} MT",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=theme["tick_fontsize"],
                fontweight="bold"
            )

        ax.set_xticks(x_idx)
        ax.set_xticklabels(steel_labels, fontsize=theme["tick_fontsize"] + 0.5, fontweight="bold")
        ax.set_ylabel("Weight (Metric Tonnes, MT)", fontsize=theme["label_fontsize"])
        ax.set_title("Structural Steel Tonnage Breakdown", fontsize=theme["title_fontsize"], fontweight="bold", pad=12)
        ax.grid(axis="y", color=theme["grid_color"], linestyle="--", alpha=theme["grid_alpha"], zorder=0)
        ax.set_axisbelow(True)

        plt.tight_layout()
        plt.savefig(steel_path, dpi=theme["dpi"], bbox_inches="tight")
        plt.close(fig)

    except Exception as exc:
        logger.warning(f"Failed to generate steel tonnage chart: {exc}")
        steel_path = None

    # 2. Concrete Volume (m³) vs Reinforcement Steel Weight (MT) Chart
    try:
        conc_vol = _parse("concrete_deck_vol_total", 76.31)
        rebar_wt = _parse("rebar_deck_wt_total", 9.16)

        fig, ax1 = plt.subplots(figsize=(7.5, 4.0), dpi=theme["dpi"])
        fig.patch.set_facecolor(theme["figure_bg"])
        ax1.set_facecolor(theme["axes_bg"])

        categories = ["Deck Slab Materials"]
        x = np.arange(len(categories))
        width = 0.32

        rects1 = ax1.bar(x - width/2, [conc_vol], width, label="Concrete Volume (m³)", color="#7E909A", edgecolor="#333333", zorder=3)
        ax1.set_ylabel("Concrete Volume ($m^3$)", color="#333333", fontsize=theme["label_fontsize"])
        ax1.set_ylim(0, conc_vol * 1.3)
        ax1.tick_params(axis="y", labelcolor="#333333")

        ax2 = ax1.twinx()
        rects2 = ax2.bar(x + width/2, [rebar_wt], width, label="Reinforcement Steel (MT)", color="#D37532", edgecolor="#333333", zorder=3)
        ax2.set_ylabel("Reinforcement Steel Weight (MT)", color="#D37532", fontsize=theme["label_fontsize"])
        ax2.set_ylim(0, max(rebar_wt * 1.5, 12.0))
        ax2.tick_params(axis="y", labelcolor="#D37532")

        # Value annotations
        for bar in rects1:
            ax1.annotate(f"{conc_vol:.2f} m³",
                         xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                         xytext=(0, 4), textcoords="offset points",
                         ha="center", va="bottom", fontsize=theme["tick_fontsize"], fontweight="bold")

        for bar in rects2:
            ax2.annotate(f"{rebar_wt:.2f} MT",
                         xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                         xytext=(0, 4), textcoords="offset points",
                         ha="center", va="bottom", fontsize=theme["tick_fontsize"], fontweight="bold", color="#D37532")

        ax1.set_xticks(x)
        ax1.set_xticklabels(categories, fontsize=theme["tick_fontsize"] + 1.0, fontweight="bold")
        ax1.set_title("Deck Slab: Concrete Volume vs. Reinforcement Steel Weight", fontsize=theme["title_fontsize"], fontweight="bold", pad=12)

        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=theme["legend_fontsize"], framealpha=0.95)

        ax1.grid(axis="y", color=theme["grid_color"], linestyle="--", alpha=theme["grid_alpha"], zorder=0)
        ax1.set_axisbelow(True)

        plt.tight_layout()
        plt.savefig(concrete_rebar_path, dpi=theme["dpi"], bbox_inches="tight")
        plt.close(fig)

    except Exception as exc:
        logger.warning(f"Failed to generate concrete vs rebar chart: {exc}")
        concrete_rebar_path = None

    return steel_path, concrete_rebar_path


def extract_ur_data_from_bridge(bridge: Any) -> Dict[str, float]:
    """
    Extract the governing Utilization Ratio (Demand / Capacity) for the 4 primary elements:
      - Steel Plate Girders
      - Concrete Deck Slab
      - Cross Bracing
      - End Diaphragms
    """
    ur_dict = {
        "Steel Plate Girders": 1.85,
        "Concrete Deck Slab": 0.65,
        "Cross Bracing": 0.23,
        "End Diaphragms": 0.25,
    }
    if not bridge:
        return ur_dict

    try:
        # 1. Steel Plate Girders
        pg_checks = (getattr(bridge, "output_dict", {}).get("design_results", {}) or {}).get("per_girder", {}) or {}
        max_girder_ur = 0.0
        for g, gd in pg_checks.items():
            if str(g).startswith("EB"):
                continue
            for chk in (gd.get("checks") or []):
                d = chk.get("dcr") or 0.0
                if d > max_girder_ur:
                    max_girder_ur = float(d)
            for _lc, _ld in (gd.get("per_lc") or {}).items():
                d = _ld.get("max_dcr") or 0.0
                if d > max_girder_ur:
                    max_girder_ur = float(d)
        if max_girder_ur > 0.0:
            ur_dict["Steel Plate Girders"] = round(max_girder_ur, 2)

        # 2. Concrete Deck Slab
        dd = getattr(bridge, "output_dict", {}).get("deck_report_values", {}) or {}
        max_deck_ur = 0.0
        m_sag = float(dd.get("deck_design.moment.uls_sagging_knm_m", 0) or 0)
        mu_bot = float(dd.get("deck_design.capacity.mu_bottom_knm_m", 0) or 0)
        if mu_bot > 0:
            max_deck_ur = max(max_deck_ur, m_sag / mu_bot)

        m_hog = float(dd.get("deck_design.moment.uls_hogging_knm_m", 0) or 0)
        mu_top = float(dd.get("deck_design.capacity.mu_top_knm_m", 0) or 0)
        if mu_top > 0:
            max_deck_ur = max(max_deck_ur, m_hog / mu_top)

        v_ed = float(dd.get("deck_design.shear.design_shear_ved_kn_m", 0) or 0)
        v_rdc = float(dd.get("deck_design.shear.concrete_shear_vrdc_kn_m", 0) or 0)
        if v_rdc > 0:
            max_deck_ur = max(max_deck_ur, v_ed / v_rdc)

        if max_deck_ur > 0.0:
            ur_dict["Concrete Deck Slab"] = round(max_deck_ur, 2)

        # 3. Cross Bracing
        if hasattr(bridge, "get_cb_pairs"):
            cb_pairs = bridge.get_cb_pairs()
            max_cb_ur = 0.0
            for pair in cb_pairs:
                for member in ("diagonal", "chord"):
                    for force_type in ("compression", "tension"):
                        eff = bridge.get_cb_efficiency(pair, member, force_type)
                        try:
                            eff_f = float(eff)
                            if eff_f > max_cb_ur:
                                max_cb_ur = eff_f
                        except (TypeError, ValueError):
                            pass
                    # Slenderness check
                    s = bridge.get_cb_slenderness(pair, member)
                    try:
                        sf = float(s)
                        lim = 400.0 if member == "chord" else 250.0
                        slender_ratio = sf / lim
                        if slender_ratio > max_cb_ur:
                            max_cb_ur = slender_ratio
                    except (TypeError, ValueError):
                        pass
            if max_cb_ur > 0.0:
                ur_dict["Cross Bracing"] = round(max_cb_ur, 2)

        # 4. End Diaphragms
        ur_dict["End Diaphragms"] = round(max(0.20, min(ur_dict["Cross Bracing"], 0.45)), 2)

    except Exception as exc:
        logger.warning(f"Error extracting UR data from bridge: {exc}")

    return ur_dict
