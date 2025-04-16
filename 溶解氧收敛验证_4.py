import numpy as np
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# Parameter configuration
DO_initial = 8.0    # Initial dissolved oxygen concentration (mg/L)
DO_steady = 2.0     # Steady-state dissolved oxygen concentration (mg/L)
K = 20.0            # Half-saturation constant
num_points = 100    # Number of data points
t_max = 100         # Maximum time (arbitrary units)

# Generate time series
t = np.linspace(0, t_max, num_points)

# Generate Monod trend
DO_sim_trend = (DO_initial - DO_steady) * (t / (K + t)) + DO_steady

# Generate simulated data (with small noise)
sim_noise = np.random.normal(0, 0.05, num_points)  # noise for simulated data
DO_sim = DO_sim_trend + sim_noise

# Generate measurement data (with larger noise)
meas_noise_rel = np.random.normal(0, 0.08, num_points)  # ~8% relative noise
DO_meas = DO_sim_trend * (1 + meas_noise_rel)

# Calculate residuals
residuals = DO_meas - DO_sim

# Calculate the percentage of points within ±10% threshold
# (Here “±10%” is interpreted as ±(0.1 * |simulated|))
threshold_frac = 0.1
within_threshold = np.abs(residuals) <= threshold_frac * np.abs(DO_sim)
percentage_within = np.mean(within_threshold) * 100

# For the histogram itself, we’ll display dashed lines at ±0.1 mg/L
# and color bins accordingly
hist_threshold = 0.1  # ±0.1 mg/L

# Visualization
plt.figure(figsize=(14, 10))

# Subplot 1: Main trend comparison
plt.subplot(2, 2, 1)
plt.plot(t, DO_sim, label='Simulated Data', color='blue', alpha=0.7)
plt.scatter(t, DO_meas, label='Measured Data', color='red', s=15, alpha=0.7)
plt.xlabel('Time (arbitrary units)')
plt.ylabel('Dissolved Oxygen (mg/L)')
plt.title('Comparison of Simulated and Measured Data')
plt.legend()
plt.grid(True)

# Subplot 2: Residuals over time
plt.subplot(2, 2, 2)
plt.scatter(t, residuals, s=15, color='green', alpha=0.7)
plt.axhline(0, color='black', linestyle='--')
plt.xlabel('Time (arbitrary units)')
plt.ylabel('Residual (mg/L)')
plt.title('Residuals Over Time')
plt.grid(True)

# Subplot 3: Histogram of residuals with ±10% dashed lines and color coding
plt.subplot(2, 2, 3)

# Manually compute histogram so we can color bins
counts, bins = np.histogram(residuals, bins=20)
bin_centers = 0.5 * (bins[:-1] + bins[1:])
bin_width = bins[1] - bins[0]

colors = []
for bc in bin_centers:
    if -hist_threshold <= bc <= hist_threshold:
        colors.append('green')
    else:
        colors.append('red')

# Plot the bars with the chosen colors
plt.bar(bin_centers, counts, width=bin_width, color=colors, alpha=0.7)

# Add dashed lines at ±hist_threshold
plt.axvline(-hist_threshold, color='black', linestyle='--')
plt.axvline(hist_threshold, color='black', linestyle='--')

plt.xlabel('Residual (mg/L)')
plt.ylabel('Count')
plt.title('Histogram of Residuals')
plt.grid(True)

# Subplot 4: Display statistics
plt.subplot(2, 2, 4)
plt.axis('off')
plt.text(
    0.1, 0.8,
    f'Residual Analysis:\n\n'
    f'• {percentage_within:.1f}% of residuals are within ±10% of the simulated value\n'
    f'• Max positive residual: {residuals.max():.2f} mg/L\n'
    f'• Max negative residual: {residuals.min():.2f} mg/L\n'
    f'• Mean absolute error: {np.mean(np.abs(residuals)):.2f} mg/L',
    fontsize=12, va='top'
)

plt.tight_layout()
plt.show()

