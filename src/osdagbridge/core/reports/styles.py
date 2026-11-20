# =============================================================================
# OsdagBridge — Centralized Formatting & Style System (Single Source of Truth)
# Defines global document layout settings, color palettes, custom table styles,
# header/footer themes, spacing rules, and visualization styling parameters.
# =============================================================================

from dataclasses import dataclass
from typing import List, Optional


# -----------------------------------------------------------------------------
# 1. Document Geometry & Page Layout
# -----------------------------------------------------------------------------
# Generous bottom margin and footskip ensure table rows and explanatory notes
# never bleed into the fancyhdr footer rule (resolves Page 30 footer overlap).
PAGE_GEOMETRY = {
    "paper": "a4paper",
    "top": "25mm",
    "bottom": "30mm",
    "left": "20mm",
    "right": "20mm",
    "headheight": "20pt",
    "headsep": "10pt",
    "footskip": "18mm",
}

LINE_STRETCH = 1.15


# -----------------------------------------------------------------------------
# 2. Color Palettes
# -----------------------------------------------------------------------------
COLOR_PALETTE = {
    "osdagGreen": "91B014",       # Brand Primary Green (#91B014)
    "osdagDarkGreen": "6E880B",   # Accent Dark Green
    "osdagLightGreen": "F4F7E6",  # Table header highlight tint
    "osdagGrey": "555555",        # Muted text grey
    "passGreen": "2E7D32",        # Standard PASS check indicator
    "failRed": "C62828",          # Standard FAIL check indicator
    "warnOrange": "E65100",       # Standard WARN check indicator
    "tableHeaderBg": "EAEAEA",    # Subtle grey table header fill
    "tableRuleColor": "888888",   # Clean table border rule color
}


# -----------------------------------------------------------------------------
# 3. Table Layout & Buffer Constraints
# -----------------------------------------------------------------------------
TABLE_STYLES = {
    "tabcolsep": "6pt",
    "arraystretch": "1.15",
    "LTpre": "0pt",
    "LTpost": "6pt",
    "arrayrulewidth": "0.5pt",
    "extrarowheight": "0.6pt",
    "needspace_before_table": "6\\baselineskip",
}


# -----------------------------------------------------------------------------
# 4. Helper: Standard Longtable Header & Footer Generator
# -----------------------------------------------------------------------------
def make_longtable_headers(caption: str, header_row: str, num_cols: int, label: Optional[str] = None) -> str:
    """
    Generate standard longtable header and continuation blocks with \\endfirsthead
    and \\endhead so table headers reliably repeat on every subsequent page.

    Parameters:
        caption: Table caption string (can include formatting like \\textbf{...})
        header_row: The LaTeX header row string (without trailing \\hline or \\endfirsthead)
        num_cols: Total number of columns in the table (for multicolumn spans)
        label: Optional LaTeX label (e.g., 'tab:live-loads')
    """
    lbl_tex = f"\\label{{{label}}}\n" if label else ""
    hdr_clean = header_row.strip().rstrip(r"\hline").strip()

    return (
        f"\\caption{{{caption}}}\n"
        f"{lbl_tex}"
        f"\\hline\n"
        f"{hdr_clean} \\\\\n"
        f"\\hline\n"
        f"\\endfirsthead\n\n"
        f"\\multicolumn{{{num_cols}}}{{c}}{{\\small\\textit{{\\tablename\\ \\thetable{{}} -- Continued from previous page}}}} \\\\[4pt]\n"
        f"\\hline\n"
        f"{hdr_clean} \\\\\n"
        f"\\hline\n"
        f"\\endhead\n\n"
        f"\\hline\n"
        f"\\multicolumn{{{num_cols}}}{{r}}{{\\small\\textit{{Continued on next page...}}}} \\\\\n"
        f"\\endfoot\n\n"
        f"\\hline\n"
        f"\\endlastfoot\n"
    )


# -----------------------------------------------------------------------------
# 5. Chart & Visualization Styling Constants
# -----------------------------------------------------------------------------
CHART_THEME = {
    "dpi": 300,
    "figure_bg": "#FFFFFF",
    "axes_bg": "#FAFAFA",
    "grid_color": "#E0E0E0",
    "grid_alpha": 0.7,
    "osdag_primary": "#91B014",
    "osdag_secondary": "#2A75D3",
    "pass_color": "#2E7D32",
    "fail_color": "#C62828",
    "threshold_line_color": "#D32F2F",
    "threshold_line_style": "--",
    "threshold_line_width": 1.75,
    "font_family": "sans-serif",
    "title_fontsize": 11,
    "label_fontsize": 10,
    "tick_fontsize": 8.5,
    "legend_fontsize": 8.5,
}


# -----------------------------------------------------------------------------
# 6. LaTeX Preamble Configuration Generator
# -----------------------------------------------------------------------------
def get_latex_styles_preamble() -> str:
    """Return the centralized LaTeX styling commands to be injected into the document preamble."""
    geom = PAGE_GEOMETRY
    cols = COLOR_PALETTE
    t_style = TABLE_STYLES

    color_defs = "\n".join([f"\\definecolor{{{k}}}{{HTML}}{{{v}}}" for k, v in cols.items()])

    return rf"""
% === Centralized Styles: Geometry & Layout ===
\usepackage[{geom['paper']}, top={geom['top']}, bottom={geom['bottom']}, left={geom['left']}, right={geom['right']}, headheight={geom['headheight']}, headsep={geom['headsep']}, footskip={geom['footskip']}]{{geometry}}

% === Centralized Styles: Color Definitions ===
{color_defs}

% === Centralized Styles: Table Formatting ===
\setlength{{\tabcolsep}}{{{t_style['tabcolsep']}}}
\renewcommand{{\arraystretch}}{{{t_style['arraystretch']}}}
\setlength{{\LTpre}}{{{t_style['LTpre']}}}
\setlength{{\LTpost}}{{{t_style['LTpost']}}}
\setlength{{\arrayrulewidth}}{{{t_style['arrayrulewidth']}}}
\setlength{{\extrarowheight}}{{{t_style['extrarowheight']}}}

% Prevent tables from breaking across page bottoms awkwardly
\BeforeBeginEnvironment{{table}}{{\needspace{{{t_style['needspace_before_table']}}}}}
\BeforeBeginEnvironment{{longtable}}{{\needspace{{{t_style['needspace_before_table']}}}}}
"""
