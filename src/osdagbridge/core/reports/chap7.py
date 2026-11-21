# =============================================================================
# Chapter 7: Material Take-off & Quantity Summary
# Displays the Bill of Materials table and embeds programmatic visualizations
# for structural steel tonnage and concrete volume vs reinforcement weight.
# =============================================================================

from .styles import make_longtable_headers


def ch7_quantities(input_dict, fig_paths=None):
    fig_paths = fig_paths or {}
    steel_fig_tex = ""
    concrete_fig_tex = ""

    steel_path = fig_paths.get("material_steel_tonnage")
    if steel_path:
        p_steel = steel_path.replace("\\", "/")
        steel_fig_tex = rf"""
\vspace{{1.2em}}
\begin{{figure}}[H]
\centering
\includegraphics[width=0.85\textwidth]{{{p_steel}}}
\caption{{\textbf{{Structural Steel Tonnage Breakdown (Girders, Cross Bracing, End Diaphragms)}}}}
\label{{fig:material-steel-tonnage}}
\end{{figure}}
"""

    concrete_rebar_path = fig_paths.get("material_concrete_rebar")
    if concrete_rebar_path:
        p_conc = concrete_rebar_path.replace("\\", "/")
        concrete_fig_tex = rf"""
\vspace{{1.2em}}
\begin{{figure}}[H]
\centering
\includegraphics[width=0.85\textwidth]{{{p_conc}}}
\caption{{\textbf{{Deck Slab: Concrete Volume ($m^3$) vs. Reinforcement Steel Weight (MT)}}}}
\label{{fig:material-concrete-rebar}}
\end{{figure}}
"""

    return r"""
\chapter{Material Take-off \& Quantity Summary}
\label{ch:material-takeoff}

This chapter details the comprehensive Bill of Materials (BOM) for the bridge structure, summarizing material volumes, component quantities, and estimated steel tonnages per component.

\vspace{1em}
\begingroup
\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{|C{1.0cm}|L{3.8cm}|C{2.6cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|C{1.8cm}|}
""" + make_longtable_headers(
        r"\textbf{Bill of Materials (Steel, Concrete, and Reinforcement Quantities)}",
        r"\textbf{S.N.} & \textbf{Item Description} & \textbf{Volume} & \textbf{Quantity} & \textbf{Total Volume} & \textbf{Weight (MT)} & \textbf{Total Weight (MT)}",
        7,
        label="tab:bom-summary"
    ) + r"""
1 & Structural Steel (IS 2062) for Girders & """ + str(input_dict.get("steel_girders_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_qty", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("steel_girders_wt_total", "N.A.")) + r""" \\
\hline
2(a) & Cross Bracing - Top Chord & """ + str(input_dict.get("bracing_top_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_top_wt_total", "N.A.")) + r""" \\
\hline
2(b) & Cross Bracing - Bottom Chord & """ + str(input_dict.get("bracing_bot_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_bot_wt_total", "N.A.")) + r""" \\
\hline
2(c) & Cross Bracing - Diagonal Chord & """ + str(input_dict.get("bracing_diag_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_qty", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("bracing_diag_wt_total", "N.A.")) + r""" \\
\hline
3 & Concrete (M40) for Deck Slab & """ + str(input_dict.get("concrete_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("concrete_deck_wt_total", "N.A.")) + r""" \\
\hline
4 & Reinforcement Steel (Fe 500) & """ + str(input_dict.get("rebar_deck_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_qty", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("rebar_deck_wt_total", "N.A.")) + r""" \\
\hline
5 & Shear Stud Connectors & """ + str(input_dict.get("shear_studs_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_qty", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("shear_studs_wt_total", "N.A.")) + r""" \\
\hline
6 & Crash Barrier & """ + str(input_dict.get("crash_barrier_vol_formula", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_qty", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_vol_total", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_single", "N.A.")) + r""" & """ + str(input_dict.get("crash_barrier_wt_total", "N.A.")) + r""" \\
\end{longtable}
\endgroup

\noindent\textit{Note: Material quantities are derived directly from structural analysis dimensions, standard material density of structural steel ($7850\text{ kg/m}^3$), reinforced concrete ($25\text{ kN/m}^3$), and average deck slab reinforcement density ($120\text{ kg/m}^3$).}

""" + steel_fig_tex + concrete_fig_tex
