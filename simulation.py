# =============================================================================
# THE YACOUBA LOOP — Monte Carlo Simulation (v2)
# Author  : Danny Nawa Myunda
#           Independent Researcher | Copperbelt University, Zambia
#           "One World, One People"
# =============================================================================
# RECOMMENDED PARAMETERS
#   Starting Biomass : 450 to 850+ kg/ha  (degraded to recovering Sahel land)
#   Livestock Count  : 0.1 to 0.7 animals/ha (light to moderate stocking rate)
#   These ranges reflect real Sahelian field conditions — UNCCD & FAO data.

import random
import statistics
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# --- SCIENCE CONSTANTS (unchanged from v1) ---
MONTHLY_CONSUMPTION  = 185   # kg per animal per month (FAO Standard)
SAHEL_GROWTH_COEFF   = 2.4   # kg of new grass per 1 mm of rain
MANURE_RATE          = 0.30  # 30% of consumed grass returns as manure
BIOCHAR_CONVERSION   = 0.15  # 15% of manure converts to biochar benefit
#   Note: 15% is an optimistic estimate accounting for losses due to
#   weathering, collection inefficiency, and drying before pyrolysis.
RESTORATION_BOOST    = 0.80  # 80% average synergy (Zai Pits + Biochar)

# --- RAINFALL MODEL (v2 improvement) ---
# Real Sahel seasons cluster rain in the middle months (July–August peak).
# Using profile templates + noise is more realistic than uniform random.
RAINFALL_PROFILES = [
    [8,  18, 35, 28, 12],   # typical moderate season
    [5,  12, 42, 38, 20],   # late-peak season
    [10, 25, 48, 30, 15],   # strong season
    [6,  10, 22, 18,  8],   # poor/drought season
    [12, 30, 50, 45, 25],   # exceptional season
]

def sahel_rainfall():
    """Return monthly rainfall (mm) for one simulated 5-month rainy season."""
    profile = random.choice(RAINFALL_PROFILES)
    return [max(3, v + random.uniform(-8, 8)) for v in profile]


# --- CORE SIMULATION (same logic as v1, now inside a function) ---
def simulate_season(start_grass, animals, system_active):
    """
    Simulate one 5-month rainy season.
    Returns a list of 6 biomass values: [start, month1, ..., month5]
    """
    grass = start_grass
    history = [grass]
    monthly_rain = sahel_rainfall()

    for month in range(5):
        # Livestock reduce intake when grass is scarce (real Sahel behaviour)
        grazing_pressure = min(1.0, grass / (animals * MONTHLY_CONSUMPTION))
        consumed = animals * MONTHLY_CONSUMPTION * grazing_pressure

        grass = max(0, grass - consumed)

        # Rainfall-driven regrowth
        rainfall   = monthly_rain[month]
        new_growth = rainfall * SAHEL_GROWTH_COEFF

        # The Restoration Synergy
        if system_active:
            water_bonus   = new_growth * RESTORATION_BOOST
            manure_kg     = consumed   * MANURE_RATE
            biochar_bonus = manure_kg  * BIOCHAR_CONVERSION
            new_growth   += water_bonus + biochar_bonus

        grass = max(0, grass + new_growth)
        history.append(grass)

    return history


# --- MONTE CARLO WRAPPER ---
def monte_carlo(n_runs, start_grass, animals, system_active):
    """
    Run the simulation n_runs times.
    Returns:
        finals   — list of final biomass values (month 5 of each run)
        medians  — median biomass at each of the 6 time points
    """
    all_histories = [
        simulate_season(start_grass, animals, system_active)
        for _ in range(n_runs)
    ]

    finals  = [h[5] for h in all_histories]
    medians = [
        statistics.median(h[m] for h in all_histories)
        for m in range(6)
    ]
    return finals, medians


# --- RESULTS ANALYSIS ---
def recovery_probability(finals, threshold):
    """Percentage of runs where final biomass exceeds threshold."""
    above = sum(1 for f in finals if f >= threshold)
    return round(above / len(finals) * 100, 1)

def land_health_label(biomass):
    if biomass > 2000:  return "THRIVING  — Desert Pushed Back"
    if biomass >= 1000: return "STABLE    — Holding Ground"
    if biomass >= 500:  return "STRESSED  — Restoration Recommended"
    return                     "DEGRADED  — Critical Intervention Needed"


# --- PLOTTING ---
GREEN  = "#3B6D11"
AMBER  = "#854F0B"
GREY   = "#888780"

def plot_results(with_finals, no_finals, with_medians, no_medians):
    months = ["Start", "Month 1", "Month 2", "Month 3", "Month 4", "Month 5"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle(
        "Yacouba Loop — Monte Carlo Simulation\n"
        "Danny Nawa Myunda · Copperbelt University · One World, One People",
        fontsize=11, y=1.01
    )

    # --- Left: Median trajectory ---
    ax1 = axes[0]
    ax1.plot(months, with_medians, color=GREEN, marker="o", linewidth=2.2,
             label="With Yacouba Loop")
    ax1.plot(months, no_medians,   color=AMBER, marker="s", linewidth=2.2,
             linestyle="--", label="Without Yacouba Loop", alpha=0.8)
    ax1.fill_between(months, with_medians, no_medians,
                     where=[w > n for w,n in zip(with_medians, no_medians)],
                     alpha=0.08, color=GREEN)
    ax1.set_title("Median Biomass Trajectory", fontsize=10)
    ax1.set_ylabel("Field Biomass (kg/ha)")
    ax1.legend(fontsize=9)
    ax1.grid(axis="y", alpha=0.3)
    ax1.tick_params(axis="x", rotation=20)

    # --- Right: Distribution of final biomass ---
    ax2 = axes[1]
    bins = [0, 500, 1000, 1500, 2000, 2500, 3000, 4000, 6000]
    n = len(with_finals)
    with_counts = [sum(1 for f in with_finals if bins[i] <= f < bins[i+1]) / n * 100
                   for i in range(len(bins)-1)]
    no_counts   = [sum(1 for f in no_finals   if bins[i] <= f < bins[i+1]) / n * 100
                   for i in range(len(bins)-1)]
    labels = ["<500","500–1k","1k–1.5k","1.5k–2k","2k–2.5k","2.5k–3k","3k–4k","4k+"]
    x = range(len(labels))
    w = 0.38
    ax2.bar([i - w/2 for i in x], with_counts, width=w, color=GREEN,
            alpha=0.82, label="With Yacouba Loop")
    ax2.bar([i + w/2 for i in x], no_counts,   width=w, color=AMBER,
            alpha=0.65, label="Without Yacouba Loop")
    ax2.set_title("Final Biomass Distribution (Month 5)", fontsize=10)
    ax2.set_ylabel("% of runs")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
    ax2.legend(fontsize=9)
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("yacouba_loop_results.png", dpi=150, bbox_inches="tight")
    print("\nChart saved: yacouba_loop_results.png")
    plt.show()


# --- USER INPUT ---
def get_inputs():
    print("=" * 60)
    print("  THE YACOUBA LOOP — Monte Carlo Simulation (v2)")
    print("  Danny Nawa Myunda · Copperbelt University")
    print("=" * 60)
    print("\nRecommended: Biomass 450–850 kg/ha | Livestock 0.1–0.7/ha\n")
    grass   = int(input("Starting Biomass (kg/ha)           : "))
    animals = float(input("Livestock Count (animals/ha)       : "))
    n_runs  = int(input("Number of simulation runs [500]    : ") or "500")
    return grass, animals, n_runs


# --- MAIN ---
if __name__ == "__main__":
    grass, animals, n_runs = get_inputs()

    print(f"\nRunning {n_runs} seasons WITH the Yacouba Loop...")
    with_finals, with_medians = monte_carlo(n_runs, grass, animals, system_active=True)

    print(f"Running {n_runs} seasons WITHOUT the Yacouba Loop...")
    no_finals, no_medians = monte_carlo(n_runs, grass, animals, system_active=False)

    # Summary statistics
    w_med = statistics.median(with_finals)
    n_med = statistics.median(no_finals)
    lift  = round((w_med - n_med) / max(1, n_med) * 100, 1)

    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    print(f"  Median final biomass  WITH loop : {w_med:,.0f} kg/ha")
    print(f"  Median final biomass  NO loop   : {n_med:,.0f} kg/ha")
    print(f"  Biomass lift from system        : +{lift}%")
    print(f"\n  Land health (median, with loop) : {land_health_label(w_med)}")
    print(f"  Land health (median, no loop)   : {land_health_label(n_med)}")

    print("\n  RECOVERY PROBABILITIES")
    thresholds = [(2000, "Thriving  (>2000 kg/ha)"),
                  (1000, "Stable    (>1000 kg/ha)"),
                  (500,  "Not degraded (>500 kg/ha)")]
    for t, label in thresholds:
        wp = recovery_probability(with_finals, t)
        np = recovery_probability(no_finals,   t)
        print(f"    {label}")
        print(f"      With loop: {wp:5.1f}%   |   Without: {np:5.1f}%")

    print("\n  DATA SOURCES")
    print("    FAO/GIEWS Sahel Biomass Report")
    print("    Lehmann & Joseph (2015) — Biochar for Environmental Management")
    print("    UNCCD Sahelian Field Data (2024)")
    print("    FAO Copernicus Biomass Data")
    print("=" * 60)

    plot_results(with_finals, no_finals, with_medians, no_medians)
 

   
 
