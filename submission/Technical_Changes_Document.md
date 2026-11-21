# OsdagBridge LaTeX Report Generator Refactoring & Enhancements
## Technical Changes Document

**Author:** Mayank Banwale  
**Repository:** https://github.com/mayannkk02/OsdagBridge  
**Branch:** `feature/report-enhancements`  

---

### 1. Overview

This document tell us the refactoring and enhancements performed on the **OsdagBridge** repo forked from @nidhikhare12. The Before report output exhibited several visual, structural, and layout errors, including absent table continuation headers, footer margin overlap, merged live load tables with discarded inputs, lack of utilization ratio visualizations, and missing material quantity charts. 

Through this task, the report generation architecture was reconstructed around a single-source-of-truth style system (`styles.py`), dynamic multi-page table header repetition (`make_longtable_headers`), headless non-blocking data visualizations (`chart_generator.py`), and robust geometry controls.

---

### 2. Issues resolved from Report Before to Report After

#### Issue 1: Repeated Table Headers Across Page Breaks
- **Issue in Before Report:** Tables spanning multiple pages broke abruptly across page splits without column headers on continuation pages (e.g., Table 3.7 Load Combinations, Table 5.1 Girder Properties, Table 5.4 Shear Checks, Table 5.12 Fatigue Assessment, Table 5.22 Overall Summary). Only 2 tables in the entire report had `\endhead`.
- **Implementation:** Integrated `make_longtable_headers()` across all chapters (`chap2.py`, `chap3.py`, `chap4.py`, `chap5.py`, `chap7.py`). Each table now provides:
  - First-page header with full caption.
  - Continuation header with `\endhead` and an italicized `Table X.X -- Continued from previous page` sub-caption.
  - Running footer with `Continued on next page...` via `\endfoot`.
- **Verification Metric:** Count of `\endhead` and `\endfirsthead` increased from **2 in Before** to **34 in After**.

#### Issue 2: Layout, Footer Overlap, and Vertical Spacing Fixes
- **Issue in Before Report:** On page 30/31, girder check rows (e.g., "G4" multi-row label) and footnotes bled directly over the green footer rule into the running footer text.
- **Root Cause Identified:** 
  1. The footer rule definition had an aggressive negative vertical skip (`\vspace{-20pt}`) designed for software-default footnotes that dragged preceding content into the footer box.
  2. Geometry lacked adequate `footskip` buffer.
  3. Default TeX vertical box stretching forced table content into footer territory.
- **Implementation:**
  - Removed the `\vspace{-20pt}` hack in `report_generator.py` and replaced with balanced `\vspace{-12pt}` and `\vspace{2pt}` skips.
  - Added `\raggedbottom` to prevent unnatural vertical stretching.
  - Adjusted page geometry in `styles.py`: `bottom=30mm`, `footskip=18mm`, `headheight=20pt`, `headsep=10pt`.
  - Added `\needspace{6\baselineskip}` before tables to prevent awkward single-row bottom page breaks.

#### Issue 3: Load & Geometry Table Refactoring
- **Issue in Before Report:** Table 3.3 was a cramped 2-column key-value table where all 8 vehicle types were concatenated into one string, Braking Load displayed "N/A" (ignoring UI inputs), and Footpath Live Load was completely blank due to an upstream variable shadowing bug (`fp_str` calculated but unused).
- **Implementation in `chap3.py`:**
  - Split into two distinct, well-structured tables:
    1. **Table 3.3: Vehicle Live Loads (LL) — per IRC 6:2017**: Multi-column grouping with `Vehicle Class`, `Total Load (kN)`, `Impact Factor`, and a grouped `Braking Load` header (`Considered?`, `Value (kN)`, `Eccentricity`).
    2. **Table 3.4: Footpath Live Load — per IRC 6:2017**: Displays intensity ($5.000\text{ kN/m}^2$), governing code reference (IRC 6 Cl. 206.1), footpath width, and accidental wheel load check ($40.0\text{ kN}$).
  - Only vehicles explicitly selected in the Additional Inputs -> Loading tab are populated.
  - Added clarifying note regarding centrifugal forces being non-applicable ($0.00\text{ kN}$) for straight alignments per IRC 6 Cl. 212.

#### Issue 4: Utilization Ratio (UR = Demand / Capacity) Summary Visualizations
- **Issue in Before Report:** Section 5.5 (Overall Design Check Summary) contained only a raw text table with no visual comparison of design margins.
- **Implementation:**
  - Created `generate_ur_summary_chart()` in `chart_generator.py` using `matplotlib.use('Agg')` (headless mode to prevent Qt GUI threading conflicts).
  - Dynamically extracts maximum governing URs for:
    - **Steel Plate Girders** (e.g., 1.85 FAIL)
    - **Concrete Deck Slab** (e.g., 0.65 PASS)
    - **Cross Bracing** (e.g., 0.23 PASS)
    - **End Diaphragms** (e.g., 0.25 PASS)
  - Features a distinct **Red dashed horizontal threshold line at $UR = 1.0$**.
  - Color-codes passing checks in **Forest Green** ($\le 1.0$) and failing checks in **Crimson Red** ($> 1.0$) with explicit callout labels.
  - Dynamically embedded into Section 5.5 above Table 5.22.

#### Issue 5 : Material Quantity Bar Charts
- **Issue in Before Report:** Chapter 7 (Material Take-off) consisted only of a raw table without graphical representation of material distribution.
- **Implementation:**
  - Implemented `generate_material_quantity_charts()` in `chart_generator.py`:
    1. **Figure 7.1: Structural Steel Tonnage Breakdown**: Visualizes tonnage in Metric Tonnes (MT) across Girders ($32.89\text{ MT}$), Cross Bracing, and End Diaphragms.
    2. **Figure 7.2: Deck Slab Concrete Volume vs. Reinforcement Steel Weight**: Dual-axis chart comparing Concrete Volume ($m^3$) on the primary y-axis vs. Rebar Weight ($\text{MT}$) on the secondary y-axis.
  - Automatically embedded into Chapter 7 below Table 7.1.

#### Issue 6: Centralized Formatting & Style System (Single Source of Truth)
- **Issue in Before Report:** Hardcoded margins, line stretching, color hex codes, table paddings, and longtable parameters were scattered across multiple chapter files and `preamble()`.
- **Implementation:**
  - Established `src/osdagbridge/core/reports/styles.py` defining:
    - `PAGE_GEOMETRY`: standardized margins and vertical clearances.
    - `COLOR_PALETTE`: brand colors (`osdagGreen = #91B014`, `passGreen`, `failRed`, `warnOrange`).
    - `TABLE_STYLES`: `tabcolsep`, `arraystretch`, `LTpre`, `LTpost`, `extrarowheight`.
    - `CHART_THEME`: 300 DPI, clean palette, background fills, and font scalings.
    - `make_longtable_headers()`: unified table header factory.
    - `get_latex_styles_preamble()`: centralized LaTeX macro injection.

---

### 3. File Modification Summary

| File Path | Type | Modifications |
|---|---|---|
| `src/osdagbridge/core/reports/styles.py` | **New** | Central style configuration, palettes, geometries, and table factory |
| `src/osdagbridge/core/reports/chart_generator.py` | **New** | Headless Matplotlib pipeline for UR and Material charts |
| `src/osdagbridge/core/reports/report_generator.py` | Modified | Wired `styles.py` preamble, chart pipeline orchestration, fixed `\footrule` |
| `src/osdagbridge/core/reports/chap2.py` | Modified | Refactored 9 tables with `make_longtable_headers` |
| `src/osdagbridge/core/reports/chap3.py` | Modified | Separated vehicle LL & footway tables, multi-column braking, fixed `fp_str` bug |
| `src/osdagbridge/core/reports/chap4.py` | Modified | Refactored reactions and deflection tables with repeating headers |
| `src/osdagbridge/core/reports/chap5.py` | Modified | Refactored 13 design check tables with repeating headers, embedded Figure 5.1 UR chart |
| `src/osdagbridge/core/reports/chap7.py` | Modified | Refactored Table 7.1 with repeating headers, embedded Figures 7.1 & 7.2 |

---

### 4. Comparison Summary: Before vs. After Report

| Evaluation Criterion | Baseline (`Report_Before.pdf`) | Enhanced (`Report_After.pdf`) | Status |
|---|---|---|---|
| **Multi-page table headers** | Absent across splits (`\endhead` count: 2) | Present on all pages (`\endhead` count: 34) | **Resolved** |
| **Footer margin overlap** | Page 30 "G4" & footnotes bleed into footer | 18mm footskip + raggedbottom + balanced skips | **Resolved** |
| **Live loads structure** | Single cramped 2-column table; blank footpath | Two distinct tables; dynamic vehicle list; braking columns | **Resolved** |
| **Utilization ratio visualization** | None (only Table 5.22) | Figure 5.1 high-res bar chart with $UR = 1.0$ red dashed line | **Resolved** |
| **Material quantity visualizations** | None (only Table 7.1) | Figure 7.1 (Steel MT) & Figure 7.2 (Concrete vs Rebar) | **Resolved** |
| **Style architecture** | Hardcoded across chapter files | 100% centralized in `styles.py` | **Resolved** |
| **Output file size** | 766 KB | 1,058 KB (reflecting 300 DPI embedded vector/raster charts) | **Verified** |

### Important
 Ai agents are used to polish this Technical Changes Document.
