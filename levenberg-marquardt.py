import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Simulated experimental data (time series)
time = np.linspace(0, 10, 50)  # Time in arbitrary units

# Define the true model: an exponential decay with noise
def true_model(t, alpha, beta):
    return alpha * np.exp(-beta * t)

# True parameters
true_alpha = 5.0
true_beta = 0.3

# Generate synthetic observations with some noise
np.random.seed(42)
observed_values = true_model(time, true_alpha, true_beta) + np.random.normal(0, 0.2, len(time))

# Fit using the Levenberg-Marquardt optimization (nonlinear least squares)
popt, pcov = curve_fit(true_model, time, observed_values, method='lm')

# Extract optimized parameters
optimized_alpha, optimized_beta = popt

# Generate predicted values
predicted_values = true_model(time, optimized_alpha, optimized_beta)

# Compute residuals
residuals = observed_values - predicted_values
residual_percentage = (residuals / observed_values) * 100

# Check if residuals are below 5%
residual_below_threshold = np.abs(residual_percentage) < 5

# Plotting the results
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# First plot: Model fitting vs. Experimental Data
ax[0].scatter(time, observed_values, label="Experimental Data", color='blue')
ax[0].plot(time, predicted_values, label="Fitted Model", color='red', linewidth=2)
ax[0].set_xlabel("Time")
ax[0].set_ylabel("Response Variable")
ax[0].set_title("Model Fit Using Levenberg-Marquardt Optimization")
ax[0].legend()

# Second plot: Residual Analysis
ax[1].bar(time, residual_percentage, color=np.where(residual_below_threshold, 'green', 'red'))
ax[1].axhline(y=5, color='black', linestyle='dashed', linewidth=1, label="5% Threshold")
ax[1].axhline(y=-5, color='black', linestyle='dashed', linewidth=1)
ax[1].set_xlabel("Time")
ax[1].set_ylabel("Residuals (%)")
ax[1].set_title("Residual Analysis for Robustness Verification")
ax[1].legend()

plt.tight_layout()
plt.show()
