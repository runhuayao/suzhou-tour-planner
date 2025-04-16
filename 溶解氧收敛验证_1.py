import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.patches import Patch


# Define Monod-like equation for DO simulation (ensuring monotonicity)
def monod_equation(t, DO_max, Ks, mu_max):
    return DO_max * (1 - np.exp(-mu_max * t / (Ks + t + 1e-6)))  # Small constant prevents singularity


# Generate time values (30-minute observation period)
time = np.linspace(0, 30, 50)  # 50 data points within 30 minutes

# Define true Monod parameters for simulated DO
DO_max_true = 2.0  # Maximum DO concentration
Ks_true = 5.0  # Half-saturation constant
mu_max_true = 0.1  # Maximum growth rate

# Generate simulated DO values (monotonic curve)
simulated_DO = monod_equation(time, DO_max_true, Ks_true, mu_max_true)

# Initialize adaptive noise reduction parameter
adaptive_weight = 1.0
np.random.seed(42)

# Adaptive noise reduction process
max_iterations = 1000
iteration = 0
target_ratio = 0.8  # Target: 80% residuals within ±10%

while iteration < max_iterations:
    # Apply noise with adaptive weight
    measured_DO = simulated_DO + np.random.normal(0, 0.3 * adaptive_weight, len(time))
    measured_DO = np.clip(measured_DO, 0.1, None)  # Prevent negative values

    # Compute residuals (avoid division by zero)
    residuals = measured_DO - simulated_DO
    residual_percentage = (residuals / (measured_DO + 1e-6)) * 100
    residual_within_threshold = np.abs(residual_percentage) < 10  # ±10% threshold

    # Check condition
    within_threshold_ratio = np.mean(residual_within_threshold)

    if within_threshold_ratio >= target_ratio:
        break  # Stop if condition met

    # Adjust noise reduction parameter dynamically
    adaptive_weight *= 0.98  # Reduce noise gradually
    iteration += 1

# Print final iteration count and adaptive weight
print(f"Final iteration count: {iteration}, Adaptive Weight: {adaptive_weight:.4f}")

# Plot results
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# First plot: Simulated vs. Measured DO
ax[0].plot(time, simulated_DO, label="Simulated DO (Model)", color='blue', linewidth=2)
ax[0].scatter(time, measured_DO, label="Measured DO (Noisy Data)", color='red', alpha=0.7)
ax[0].set_xlabel("Time (minutes)")
ax[0].set_ylabel("Dissolved Oxygen (mg/L)")
ax[0].set_title("Simulated vs. Measured Dissolved Oxygen")
ax[0].legend()

# Second plot: Residual Analysis
legend_elements = [
    Patch(facecolor='green', edgecolor='black', label='Residuals within ±10%'),
    Patch(facecolor='red', edgecolor='black', label='Residuals beyond ±10%')
]

ax[1].bar(time, residual_percentage, color=np.where(residual_within_threshold, 'green', 'red'))
ax[1].axhline(y=10, color='black', linestyle='dashed', linewidth=1, label="±10% Threshold")
ax[1].axhline(y=-10, color='black', linestyle='dashed', linewidth=1)
ax[1].set_xlabel("Time (minutes)")
ax[1].set_ylabel("Residuals (%)")
ax[1].set_title("Residual Analysis for DO Predictions")
ax[1].legend(handles=legend_elements)

plt.tight_layout()
plt.show()
