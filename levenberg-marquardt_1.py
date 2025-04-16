import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Simulated experimental data
time = np.linspace(0, 10, 50)

# Define alternative decay model
def alternative_model(t, alpha, beta, gamma):
    return alpha * np.exp(-beta * t) + gamma

# Generate synthetic data
true_alpha, true_beta, true_gamma = 5.0, 0.3, 0.1
np.random.seed(42)
observed_values = alternative_model(time, true_alpha, true_beta, true_gamma) + np.random.normal(0, 0.2, len(time))

# Fit the model
initial_guess = [5, 0.3, 0.1]
popt_alt, _ = curve_fit(alternative_model, time, observed_values, p0=initial_guess, method='lm')

# Extract optimized parameters
optimized_alpha_alt, optimized_beta_alt, optimized_gamma_alt = popt_alt

# Generate new predictions
predicted_values_alt = alternative_model(time, optimized_alpha_alt, optimized_beta_alt, optimized_gamma_alt)

# Compute residuals
residuals_alt = observed_values - predicted_values_alt
residual_percentage_alt = (residuals_alt / observed_values) * 100
residual_below_threshold_alt = np.abs(residual_percentage_alt) < 5

# Plot results
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# Model Fit Plot
ax[0].scatter(time, observed_values, label="Experimental Data", color='blue')
ax[0].plot(time, predicted_values_alt, label="Updated Fitted Model", color='green', linewidth=2)
ax[0].set_xlabel("Time")
ax[0].set_ylabel("Response Variable")
ax[0].set_title("Improved Model Fit Using Levenberg-Marquardt Optimization")
ax[0].legend()

# Residual Analysis Plot
ax[1].bar(time, residual_percentage_alt, color=np.where(residual_below_threshold_alt, 'green', 'red'))
ax[1].axhline(y=5, color='black', linestyle='dashed', linewidth=1, label="5% Threshold")
ax[1].axhline(y=-5, color='black', linestyle='dashed', linewidth=1)
ax[1].set_xlabel("Time")
ax[1].set_ylabel("Residuals (%)")
ax[1].set_title("Residual Analysis for Robustness Verification (Updated)")
ax[1].legend()

plt.tight_layout()
plt.show()
