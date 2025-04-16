import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, minimize
from matplotlib.patches import Patch

# Simulated experimental data
time = np.linspace(0, 10, 50)

# Define model with fixed β=0.1 and γ=2
def fixed_param_model(t, alpha):
    return alpha * np.exp(-0.1 * t) + 2

# Generate synthetic observations with noise
true_alpha = 5.0
np.random.seed(42)
observed_values = fixed_param_model(time, true_alpha) + np.random.normal(0, 0.2, len(time))

# Optimize only alpha
popt_fixed, _ = curve_fit(fixed_param_model, time, observed_values, p0=[5], method='lm')
optimized_alpha_fixed = popt_fixed[0]

# Further refine alpha
def objective(alpha):
    predicted = fixed_param_model(time, alpha)
    residuals = observed_values - predicted
    residual_percentage = (residuals / observed_values) * 100
    return np.mean(np.abs(residual_percentage))

result = minimize(objective, x0=[optimized_alpha_fixed], method='Nelder-Mead')
optimized_alpha_refined = result.x[0]

# Generate refined predictions
predicted_values_refined = fixed_param_model(time, optimized_alpha_refined)

# Compute refined residuals
residuals_refined = observed_values - predicted_values_refined
residual_percentage_refined = (residuals_refined / observed_values) * 100
residual_below_threshold_refined = np.abs(residual_percentage_refined) < 5

# Plot results
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# First plot: Refined Model Fit
ax[0].scatter(time, observed_values, label="Experimental Data", color='blue')
ax[0].plot(time, predicted_values_refined, label=f"Refined Model (β=0.1, γ=2)", color='orange', linewidth=2)
ax[0].set_xlabel("Time")
ax[0].set_ylabel("Response Variable")
ax[0].set_title("Refined Model Fit with Fixed β=0.1, γ=2")
ax[0].legend()

# Second plot: Residual Analysis with only two labels
ax[1].bar(time, residual_percentage_refined, color=np.where(residual_below_threshold_refined, '#A5D6A7', '#EF9A9A'), label="Residuals",width=0.35)

# Adding a manual legend with only two entries
legend_elements = [
    Patch(facecolor='#A5D6A7', edgecolor='black', label='Residuals within ±5%'),
    Patch(facecolor='#EF9A9A', edgecolor='black', label='Residuals beyond ±5%')
]

ax[1].axhline(y=5, color='black', linestyle='dashed', linewidth=0.1, label="5% Threshold")
ax[1].axhline(y=-5, color='black', linestyle='dashed', linewidth=1)
ax[1].set_xlabel("Time")
ax[1].set_ylabel("Residuals (%)")
ax[1].set_title("Refined Residual Analysis (β=0.1, γ=2)")
ax[1].legend(handles=legend_elements)

plt.tight_layout()
plt.show()
