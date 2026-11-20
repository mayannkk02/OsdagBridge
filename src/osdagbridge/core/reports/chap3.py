# =============================================================================
# Chapter 3: Loads and Load Combinations
# Refactored for clear separation of Vehicle Live Loads and Footway Loads,
# structured parameter columns, and repeated headers across page breaks.
# =============================================================================

from osdagbridge.core.utils.common import (
    KEY_CB_LOAD,
    KEY_LL_CUSTOM_VEHICLES,
    KEY_LL_FOOTPATH_PRESSURE_MODE,
    KEY_LL_FOOTPATH_PRESSURE_VALUE,
    KEY_LL_IRC_70R_BOGIE,
    KEY_LL_IRC_70R_TRACKED,
    KEY_LL_IRC_70R_WHEELED,
    KEY_LL_IRC_AA_TRACKED,
    KEY_LL_IRC_AA_WHEELED,
    KEY_LL_IRC_CLASS_A,
    KEY_LL_IRC_CLASS_FATIGUE,
    KEY_LL_IRC_CLASS_SV,
    KEY_MATERIAL_DECK_DENSITY,
    KEY_MATERIAL_GIRDER_DENSITY,
    KEY_PL_SELF_WEIGHT_FACTOR,
    KEY_RL_LOAD_VALUE,
    KEY_SL_DAMPING,
    KEY_SL_DEAD_LOAD_MODE,
    KEY_SL_DEAD_LOAD_VALUE,
    KEY_SL_HORIZONTAL_COEFF,
    KEY_SL_IMPORTANCE_FACTOR,
    KEY_SL_LIVE_LOAD_MODE,
    KEY_SL_LIVE_LOAD_VALUE,
    KEY_SL_SEISMIC_ZONE,
    KEY_SL_SOIL_TYPE,
    KEY_SL_SPECTRAL_COEFF,
    KEY_SL_TIME_PERIOD,
    KEY_SL_VERTICAL_COEFF,
    KEY_SL_ZONE_FACTOR,
    KEY_SPAN,
    KEY_TL_BRIDGE_TEMP_MAX,
    KEY_TL_BRIDGE_TEMP_MIN,
    KEY_TL_HIGHEST_MAX_TEMP,
    KEY_TL_LOWEST_MIN_TEMP,
    KEY_TL_TEMP_FALL,
    KEY_TL_TEMP_RISE,
    KEY_WC_LD_LANE_TABLE_COUNT,
    KEY_WC_MATERIAL,
    KEY_WC_THICKNESS,
    KEY_WL_AVG_EXPOSED_HEIGHT,
    KEY_WL_BASIC_WIND_SPEED,
    KEY_WL_HOURLY_MEAN_WIND,
    KEY_WL_HOURLY_WIND_PRESSURE,
    KEY_WL_LONGITUDINAL_WIND_FORCE,
    KEY_WL_TERRAIN_TYPE,
    KEY_WL_TRANSVERSE_WIND_FORCE,
    KEY_WL_VERTICAL_WIND_FORCE
)

from osdagbridge.core.reports.report_utils import _tex, _render_value
from .styles import make_longtable_headers


def ch3_loads(input_dict):
    from osdagbridge.core.utils.codes.irc6_2017 import IRC6_2017

    span = input_dict.get(KEY_SPAN)
    span_m = 30.0
    if span not in (None, ""):
        try:
            span_m = float(span)
        except Exception:
            span_m = 30.0

    lanes = input_dict.get(KEY_WC_LD_LANE_TABLE_COUNT)
    lanes_int = 2
    if lanes not in (None, ""):
        try:
            lanes_int = int(lanes)
        except Exception:
            lanes_int = 2

    # Calculate overall braking force from IRC 6 Cl. 211.2
    try:
        braking_force_t = IRC6_2017.cl_211_2_braking_force(lanes_int)
        braking_force_kN = braking_force_t * 9.81
    except Exception:
        braking_force_kN = 392.40

    # Calculate impact factors per IRC 6
    try:
        im_a = 1.0 + IRC6_2017.cl_208_2_impact_factor(span_m)
    except Exception:
        im_a = 1.150

    try:
        im_70r = 1.0 + IRC6_2017.cl_208_3_impact_factor(span_m)
    except Exception:
        im_70r = 1.100

    # Vehicle configurations library
    VEHICLE_DB = {
        "Class A": {
            "key": KEY_LL_IRC_CLASS_A,
            "total_load": "554.00",
            "impact": f"{im_a:.3f}",
            "braking_considered": "Yes",
            "braking_val": f"{braking_force_kN:.2f}",
            "eccentricity": "1.20 m from kerb",
        },
        "Class 70R (Wheeled)": {
            "key": KEY_LL_IRC_70R_WHEELED,
            "total_load": "1000.00",
            "impact": f"{im_70r:.3f}",
            "braking_considered": "Yes",
            "braking_val": f"{braking_force_kN:.2f}",
            "eccentricity": "0.50 m from kerb",
        },
        "Class 70R (Tracked)": {
            "key": KEY_LL_IRC_70R_TRACKED,
            "total_load": "700.00",
            "impact": f"{im_70r:.3f}",
            "braking_considered": "Yes",
            "braking_val": f"{min(braking_force_kN, 140.0):.2f}",
            "eccentricity": "0.50 m from kerb",
        },
        "Class AA (Wheeled)": {
            "key": KEY_LL_IRC_AA_WHEELED,
            "total_load": "400.00",
            "impact": f"{im_70r:.3f}",
            "braking_considered": "Yes",
            "braking_val": f"{min(braking_force_kN, 80.0):.2f}",
            "eccentricity": "0.50 m from kerb",
        },
        "Class AA (Tracked)": {
            "key": KEY_LL_IRC_AA_TRACKED,
            "total_load": "700.00",
            "impact": f"{im_70r:.3f}",
            "braking_considered": "Yes",
            "braking_val": f"{min(braking_force_kN, 140.0):.2f}",
            "eccentricity": "0.50 m from kerb",
        },
        "Class SV": {
            "key": KEY_LL_IRC_CLASS_SV,
            "total_load": "3960.00",
            "impact": "1.000",
            "braking_considered": "No",
            "braking_val": "---",
            "eccentricity": "Centered on carriage",
        },
        "Class 70R (Bogie)": {
            "key": KEY_LL_IRC_70R_BOGIE,
            "total_load": "400.00",
            "impact": f"{im_70r:.3f}",
            "braking_considered": "Yes",
            "braking_val": f"{min(braking_force_kN, 80.0):.2f}",
            "eccentricity": "0.50 m from kerb",
        },
        "Class Fatigue": {
            "key": KEY_LL_IRC_CLASS_FATIGUE,
            "total_load": "554.00",
            "impact": "1.000",
            "braking_considered": "No",
            "braking_val": "---",
            "eccentricity": "Center of lane",
        },
    }

    # Dynamically select vehicles specified in input_dict
    selected_vehicles = []
    for vname, vmeta in VEHICLE_DB.items():
        if input_dict.get(vmeta["key"]):
            selected_vehicles.append((vname, vmeta))

    # Add custom vehicles if any
    custom = input_dict.get(KEY_LL_CUSTOM_VEHICLES)
    if custom and isinstance(custom, list):
        for c in custom:
            cname = c.get('name') if isinstance(c, dict) else str(c)
            if cname:
                selected_vehicles.append((
                    cname,
                    {
                        "total_load": str(c.get("load", "Custom")) if isinstance(c, dict) else "Custom",
                        "impact": "1.100",
                        "braking_considered": "Yes",
                        "braking_val": f"{braking_force_kN:.2f}",
                        "eccentricity": "Lane center",
                    }
                ))

    # Fallback default if none explicitly marked in dictionary
    if not selected_vehicles:
        selected_vehicles = [
            ("Class A", VEHICLE_DB["Class A"]),
            ("Class 70R (Wheeled)", VEHICLE_DB["Class 70R (Wheeled)"]),
            ("Class SV", VEHICLE_DB["Class SV"]),
        ]

    # Build Vehicle Live Loads Table Rows
    vehicle_rows = []
    for vname, vdata in selected_vehicles:
        vehicle_rows.append(
            f"\\textnormal{{{_tex(vname)}}} & "
            f"{vdata['total_load']} & "
            f"{vdata['impact']} & "
            f"{vdata['braking_considered']} & "
            f"{vdata['braking_val']} & "
            f"{vdata['eccentricity']} \\\\[6pt]\n\\hline"
        )
    vehicle_table_body = "\n".join(vehicle_rows)

    # Footway load parameters
    fp_mode = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_MODE, "")
    fp_value = input_dict.get(KEY_LL_FOOTPATH_PRESSURE_VALUE, "")
    if str(fp_mode).strip().lower() in ("as per irc 6", "as per irc6", "automatic"):
        try:
            fp_intensity = f"{IRC6_2017.cl_206_1_footway_load():.3f} kN/m\\textsuperscript{{2}}"
            fp_ref = "IRC 6:2017 Cl. 206.1 (Span-dependent formula)"
        except Exception:
            fp_intensity = "4.000 kN/m\\textsuperscript{2}"
            fp_ref = "IRC 6:2017 Cl. 206.1"
    elif fp_value not in (None, ""):
        fp_intensity = f"{fp_value} kN/m\\textsuperscript{{2}}"
        fp_ref = "User defined custom footway loading"
    else:
        fp_intensity = "4.000 kN/m\\textsuperscript{2}"
        fp_ref = "IRC 6:2017 Cl. 206.1"

    footpath_width = input_dict.get("typical_section.footpath_width", "1.50")

    # Wind and Seismic variables
    vz_val = input_dict.get(KEY_WL_HOURLY_MEAN_WIND)
    pz_val = input_dict.get(KEY_WL_HOURLY_WIND_PRESSURE)
    if not vz_val or not pz_val:
        try:
            _vb = input_dict.get(KEY_WL_BASIC_WIND_SPEED) or input_dict.get('wind_speed')
            _h = input_dict.get(KEY_WL_AVG_EXPOSED_HEIGHT)
            _ter = {
                "Plain Terrain": "plain",
                "Terrain with Obstructions": "obstructed",
            }.get(str(input_dict.get(KEY_WL_TERRAIN_TYPE, "")).strip(), "plain")
            _res = IRC6_2017.table_12(float(_h), _ter, float(_vb))
            if not vz_val:
                vz_val = _res.get("Vz")
            if not pz_val:
                pz_val = _res.get("Pz")
        except Exception:
            pass

    sl_zone_factor = input_dict.get(KEY_SL_ZONE_FACTOR)
    sl_spectral = input_dict.get(KEY_SL_SPECTRAL_COEFF)
    sl_ah = input_dict.get(KEY_SL_HORIZONTAL_COEFF)
    sl_av = input_dict.get(KEY_SL_VERTICAL_COEFF)
    if not sl_ah or not sl_zone_factor:
        try:
            _zone = input_dict.get(KEY_SL_SEISMIC_ZONE) or input_dict.get('seismic_zone')
            _zmap = {"1": "I", "2": "II", "3": "III", "4": "IV", "5": "V"}
            _z = str(_zone).strip().upper()
            if _z.isdigit():
                _z = _zmap.get(_z)
            _smap = {"Type I – Rocky or Hard": 1, "Type II – Medium Soil": 2, "Type III – Soft Soil": 3}
            _st = _smap.get(str(input_dict.get(KEY_SL_SOIL_TYPE, "")), 1)
            _tp = input_dict.get(KEY_SL_TIME_PERIOD)
            _damp = input_dict.get(KEY_SL_DAMPING) or "5"
            _dl_v = input_dict.get(KEY_SL_DEAD_LOAD_VALUE)
            _ll_v = input_dict.get(KEY_SL_LIVE_LOAD_VALUE)
            _dead = float(_dl_v) if str(input_dict.get(KEY_SL_DEAD_LOAD_MODE, "")) == "Custom" and _dl_v else 0.0
            _live = float(_ll_v) if str(input_dict.get(KEY_SL_LIVE_LOAD_MODE, "")) == "Custom" and _ll_v else 0.0
            _res = IRC6_2017.cl_218_5_1(zone=f"Zone {_z}", soil_type=_st, dead_load_kN=_dead,
                                        live_load_kN=_live, period_T=float(_tp) if _tp else None,
                                        damping_percent=float(_damp))
            if not sl_zone_factor:
                sl_zone_factor = _res.get("Z")
            if not sl_spectral:
                sl_spectral = _res.get("Sa_g_adjusted")
            if not sl_ah:
                sl_ah = _res.get("Ah")
            if not sl_av:
                sl_av = round(_res.get("Ah", 0) * 2 / 3, 4)
        except Exception:
            pass

    # Load combinations
    _LOAD_LABEL_MAP = {
        'dead_load': 'DL', 'surfacing': 'SIDL', 'live_load': 'LL', 'wind_load': 'WL',
        'thermal_load': 'TL', 'vehicle_collision': 'VC', 'barge_impact': 'BI',
        'floating_bodies': 'FB', 'seismic': 'EQ',
    }

    def _fmt_factors(factors):
        parts = []
        for load, val in factors.items():
            label = _LOAD_LABEL_MAP.get(load, load.upper())
            if isinstance(val, dict):
                add = val.get('adding')
                rel = val.get('relieving')
                add_s = f"{add:.2f}" if add is not None else '--'
                rel_s = f"{rel:.2f}" if rel is not None else '--'
                parts.append(f"{label}({add_s}/{rel_s})")
            else:
                if val is None:
                    continue
                parts.append(f"{label}({val:.2f})")
        return ' + '.join(parts)

    uls_combos = IRC6_2017.uls_load_combinations()
    sls_combos = IRC6_2017.sls_load_combinations()
    lc_rows = []
    for i, combo in enumerate(uls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"ULS-{i:02d} & {cases} \\\\[6pt]\n\\hline")
    for i, combo in enumerate(sls_combos, start=1):
        cases = _fmt_factors(combo['factors'])
        lc_rows.append(f"SLS-{i:02d} & {cases} \\\\[6pt]\n\\hline")
    lc_rows_str = "\n".join(lc_rows)

    return r"""
\chapter{Loads and Load Combinations}

This section summarizes all design gravity, lateral, environmental, and live loads applied to the bridge, along with the standard IRC 6 limit state load combinations.

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + make_longtable_headers(
        r"\textbf{Dead Load -- Self Weight}",
        r"\textbf{Parameter} & \textbf{Design Value}",
        2,
        label="tab:dead-load"
    ) + r"""
\textnormal{Steel Self-Weight Applied} & """ + (_render_value(input_dict, KEY_MATERIAL_GIRDER_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Concrete Deck Weight} & """ + (_render_value(input_dict, KEY_MATERIAL_DECK_DENSITY, ' kN/m\\textsuperscript{3}')) + r""" \\[6pt]
\hline
\textnormal{Self-Weight Factor} & """ + (_render_value(input_dict, KEY_PL_SELF_WEIGHT_FACTOR)) + r""" \\[6pt]
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + make_longtable_headers(
        r"\textbf{Dead Load for Surfacing (DW)}",
        r"\textbf{Parameter} & \textbf{Design Value}",
        2,
        label="tab:surfacing-load"
    ) + r"""
\textnormal{Wearing Course Load} & """ + (_render_value(input_dict, KEY_WC_MATERIAL)) + r""" x """ + (_render_value(input_dict, KEY_WC_THICKNESS)) + r""" \\[6pt]
\hline
\textnormal{Additional SIDL (Crash Barrier)} & """ + (_render_value(input_dict, KEY_CB_LOAD)) + r""" kN/m per barrier \\[6pt]
\hline
\textnormal{Railing Load} & """ + (_render_value(input_dict, KEY_RL_LOAD_VALUE)) + r""" kN/m\sdstar{} \\[6pt]
\end{longtable}

\vspace{1em}
% ── Separate Distinct Table 3.3: Vehicle Live Loads ──
\begin{longtable}{|C{3.2cm}|C{2.4cm}|C{2.0cm}|C{2.0cm}|C{2.5cm}|C{2.9cm}|}
\caption{\textbf{Vehicle Live Loads (LL) --- per IRC 6:2017}} \label{tab:vehicle-live-loads} \\
\hline
\multirow{2}{*}{\textbf{Vehicle Class}} & \multirow{2}{*}{\makecell{\textbf{Total Load}\\\textbf{(kN)}}} & \multirow{2}{*}{\makecell{\textbf{Impact}\\\textbf{Factor}}} & \multicolumn{3}{c|}{\textbf{Braking Load}} \\
\cline{4-6}
& & & \textbf{Considered?} & \textbf{Value (kN)} & \textbf{Eccentricity} \\
\hline
\endfirsthead

\multicolumn{6}{c}{{\small\textit{\tablename\ \thetable{} -- Continued from previous page}}} \\[4pt]
\hline
\multirow{2}{*}{\textbf{Vehicle Class}} & \multirow{2}{*}{\makecell{\textbf{Total Load}\\\textbf{(kN)}}} & \multirow{2}{*}{\makecell{\textbf{Impact}\\\textbf{Factor}}} & \multicolumn{3}{c|}{\textbf{Braking Load}} \\
\cline{4-6}
& & & \textbf{Considered?} & \textbf{Value (kN)} & \textbf{Eccentricity} \\
\hline
\endhead

\hline
\multicolumn{6}{r}{{\small\textit{Continued on next page...}}} \\
\endfoot

\hline
\endlastfoot

""" + vehicle_table_body + r"""
\end{longtable}
\noindent\textit{Note: Live load parameters, impact allowances, and braking forces configured per IRC 6:2017 Cl. 204, 208, and 211. Centrifugal forces are not applicable ($0.00\text{ kN}$) for straight bridge alignments per Cl. 212.}

\vspace{1em}
% ── Separate Distinct Table 3.4: Footpath Live Loads ──
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + make_longtable_headers(
        r"\textbf{Footpath Live Load --- per IRC 6:2017}",
        r"\textbf{Parameter} & \textbf{Design Specification}",
        2,
        label="tab:footpath-live-load"
    ) + r"""
\textnormal{Footway Live Load Intensity} & """ + fp_intensity + r""" \\[6pt]
\hline
\textnormal{Governing Code Reference} & """ + fp_ref + r""" \\[6pt]
\hline
\textnormal{Footpath Width} & """ + _tex(str(footpath_width)) + r""" m \\[6pt]
\hline
\textnormal{Pedestrian Combination Factor ($\psi$)} & 0.80 (ULS Combination with Vehicular LL) \\[6pt]
\hline
\textnormal{Accidental Wheel Load on Footpath} & $40.0\text{ kN}$ single wheel load check (IRC 6 Cl. 206.3) \\[6pt]
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + make_longtable_headers(
        r"\textbf{Wind Load (WL) --- per IRC 6}",
        r"\textbf{Parameter} & \textbf{Design Value}",
        2,
        label="tab:wind-load"
    ) + r"""
\textnormal{Basic Wind Speed, Vb} & """ + (_render_value(input_dict,'wind_speed', ' m/s')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Terrain Type} & """ + (_render_value(input_dict, KEY_WL_TERRAIN_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Average Exposed Height, H (m)} & """ + (_render_value(input_dict, KEY_WL_AVG_EXPOSED_HEIGHT, ' m')) + r""" \\[6pt]
\hline
\textnormal{Hourly Mean Wind Speed, Vz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_MEAN_WIND, ' m/s')) + r""" \\[6pt]
\hline
\textnormal{Hourly Wind Pressure, Pz} & """ + (_render_value(input_dict, KEY_WL_HOURLY_WIND_PRESSURE, ' N/m\\textsuperscript{2}')) + r""" \\[6pt]
\hline
\textnormal{Transverse Wind Force} & """ + (_render_value(input_dict, KEY_WL_TRANSVERSE_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Longitudinal Wind Force} & """ + (_render_value(input_dict, KEY_WL_LONGITUDINAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\hline
\textnormal{Vertical Wind Force} & """ + (_render_value(input_dict, KEY_WL_VERTICAL_WIND_FORCE, ' kN')) + r""" \\[6pt]
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + make_longtable_headers(
        r"\textbf{Earthquake Load (EL) --- per IRC 6}",
        r"\textbf{Parameter} & \textbf{Design Value}",
        2,
        label="tab:seismic-load"
    ) + r"""
\textnormal{Seismic Zone} & """ + (_render_value(input_dict,'seismic_zone')) + r""" [from Project Location] \\[6pt]
\hline
\textnormal{Zone Factor, Z} & """ + (_render_value(input_dict, KEY_SL_ZONE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Importance Factor, I} & """ + (_render_value(input_dict, KEY_SL_IMPORTANCE_FACTOR)) + r""" \\[6pt]
\hline
\textnormal{Type of Soil} & """ + (_render_value(input_dict, KEY_SL_SOIL_TYPE)) + r""" \\[6pt]
\hline
\textnormal{Sa/g} & """ + (_render_value(input_dict, KEY_SL_SPECTRAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Horizontal Seismic Coefficient, Ah} & """ + (_render_value(input_dict, KEY_SL_HORIZONTAL_COEFF)) + r""" \\[6pt]
\hline
\textnormal{Vertical Seismic Coefficient, Av} & """ + (_render_value(input_dict, KEY_SL_VERTICAL_COEFF)) + r""" \\[6pt]
\end{longtable}

\vspace{1em}
\begin{longtable}{|L{5.5cm}|p{10.0cm}|}
""" + make_longtable_headers(
        r"\textbf{Temperature Load (TL) --- per IRC 6}",
        r"\textbf{Parameter} & \textbf{Design Value}",
        2,
        label="tab:temp-load"
    ) + r"""
\textnormal{Maximum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_max')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Minimum Shade Temperature} & """ + (_render_value(input_dict,'shade_temp_min')) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Effective Bridge Temp. Range} & """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MIN)) + r""" to """ + (_render_value(input_dict, KEY_TL_BRIDGE_TEMP_MAX)) + r""" $^\circ$C \\[6pt]
\hline
\textnormal{Temperature Rise / Fall for Design} & +""" + (_render_value(input_dict, KEY_TL_TEMP_RISE)) + r""" $^\circ$C / \textminus{}""" + (_render_value(input_dict, KEY_TL_TEMP_FALL)) + r""" $^\circ$C \\[6pt]
\end{longtable}

\vspace{1em}
\begin{longtable}{|C{4.0cm}|p{11.5cm}|}
""" + make_longtable_headers(
        r"\textbf{Load Combinations (IRC 6)}",
        r"\textbf{Combination ID} & \textbf{Load Cases and Partial Safety Factors}",
        2,
        label="tab:load-combos"
    ) + r"""
""" + lc_rows_str + r"""
\end{longtable}

\noindent\textit{Note: All IRC 6 load combinations are auto-generated by OsdagBridge. User-defined custom combinations, if any, are appended.}
"""
