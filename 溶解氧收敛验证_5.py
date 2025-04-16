import numpy as np
import matplotlib.pyplot as plt


def monod_equation(t, DO_max=8.0, k=0.1):
    """
    Example Monod-like curve (or a simplified logistic/exponential approach).
    Adjust this to reflect your actual process dynamics.
    DO(t) ~ DO_max * (1 - exp(-k * t))
    """
    return DO_max * (1.0 - np.exp(-k * t))


def generate_measured_data(times):
    """
    Generate 'measured' data by taking the Monod curve and adding some noise
    to simulate experimental fluctuations.
    """
    true_values = monod_equation(times)
    # Example noise: normal distribution with stdev=0.4 (tweak as needed)
    noise = np.random.normal(loc=0.0, scale=0.4, size=len(times))
    measured = true_values + noise
    return measured


def generate_simulated_data(times, measured, noise_scale):
    """
    Generate 'simulated' data that starts at 0 and follows a curve
    that is (possibly) slightly different from the measured data,
    plus some noise controlled by 'noise_scale'.
    """
    # For example, use a slightly different k or DO_max for the model's "simulated" curve
    DO_max_sim = 7.8  # slightly different than measured
    k_sim = 0.09  # slightly different
    base_curve = DO_max_sim * (1.0 - np.exp(-k_sim * times))

    # Add noise to simulated curve
    noise = np.random.normal(loc=0.0, scale=noise_scale, size=len(times))
    simulated = base_curve + noise

    # Force it to start at exactly 0 if desired
    simulated[0] = 0.0

    return simulated


def compute_residuals_percent(measured, simulated):
    """
    Compute residuals as percentage error: (sim - meas) / meas * 100%.
    If measured[i] == 0 in real data, you'll need a fallback or ignore that point.
    """
    residuals = []
    for m, s in zip(measured, simulated):
        if m != 0:
            residuals.append((s - m) / m * 100.0)
        else:
            # If the measured value is zero, we cannot directly do a percent error.
            # We can handle it in a special way, or skip. Here, we just put 0.
            residuals.append(0.0)
    return np.array(residuals)


def check_within_threshold(residuals, threshold=10.0):
    """
    Returns the fraction of points whose absolute percentage residual
    is within 'threshold'%.
    """
    within = np.abs(residuals) <= threshold
    fraction_within = np.sum(within) / len(residuals)
    return fraction_within


def main():
    np.random.seed(42)  # For reproducibility (optional)

    # Create time points (0 to 30 minutes, 1-min interval)
    times = np.arange(0, 31, 1)

    # Generate measured data (discrete points)
    measured_data = generate_measured_data(times)

    # If you simply want to set a fixed noise scale for the simulation, do so here:
    # noise_scale = 0.5
    # simulated_data = generate_simulated_data(times, measured_data, noise_scale)
    #
    # Otherwise, let's demonstrate a simple search for a noise scale that yields
    # ~80% of residuals within ±10%.

    desired_fraction = 0.80  # 80%
    threshold_percent = 10.0
    best_noise_scale = None
    best_fraction_within = 0.0

    # Loop over a range of noise scales; this is a simple demonstration
    candidate_noise_scales = np.linspace(0.1, 1.0, 20)  # from 0.1 to 1.0 in 20 steps

    for scale in candidate_noise_scales:
        sim_data = generate_simulated_data(times, measured_data, noise_scale=scale)
        residuals = compute_residuals_percent(measured_data, sim_data)
        fraction_within = check_within_threshold(residuals, threshold=threshold_percent)
        if fraction_within > best_fraction_within:
            best_fraction_within = fraction_within
            best_noise_scale = scale

        # Stop early if we meet or exceed desired fraction
        if fraction_within >= desired_fraction:
            break

    # Generate final simulated data using the best noise scale found
    simulated_data = generate_simulated_data(times, measured_data, noise_scale=best_noise_scale)
    residuals = compute_residuals_percent(measured_data, simulated_data)
    fraction_within = check_within_threshold(residuals, threshold=threshold_percent)

    print(f"Best noise scale found: {best_noise_scale:.3f}")
    print(f"Fraction of points within ±{threshold_percent}%: {fraction_within:.2%}")

    # --- Plot 1: Measured (points) vs. Simulated (line) ---
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(times, measured_data, 'o', label='Measured DO', markersize=5)
    plt.plot(times, simulated_data, '-', label='Simulated DO', linewidth=2)
    plt.title('Measured vs. Simulated DO')
    plt.xlabel('Time (minutes)')
    plt.ylabel('DO (mg/L)')  # Example units
    plt.legend()

    # --- Plot 2: Residuals bar chart with ±10% lines ---
    plt.subplot(1, 2, 2)
    bar_colors = []
    for r in residuals:
        if abs(r) <= threshold_percent:
            bar_colors.append('green')
        else:
            bar_colors.append('red')

    plt.bar(times, residuals, color=bar_colors, alpha=0.7)

    # Draw dashed lines for ± threshold_percent
    plt.axhline(threshold_percent, color='k', linestyle='--')
    plt.axhline(-threshold_percent, color='k', linestyle='--')

    plt.title('Residuals ((Sim - Meas)/Meas * 100%)')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Residual (%)')

    # Adjust layout and show
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
