import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from matplotlib.patches import Patch

# Define microbial growth model
def microbial_growth_model(t, alpha, beta, carrying_capacity):
    return (carrying_capacity * alpha * np.exp(-beta * t)) / (carrying_capacity + alpha * (np.exp(-beta * t) - 1))

# Simulated experimental data (generated)
time_pinn = np.linspace(0, 10, 50)

# True microbial concentration parameters
true_alpha_pinn = 10      # Initial microbial concentration
true_beta_pinn = 0.2      # Growth decay rate
true_carrying_capacity = 50  # Maximum carrying capacity

# Generate experimental values with noise
np.random.seed(42)
actual_microbial_concentration = microbial_growth_model(time_pinn, true_alpha_pinn, true_beta_pinn, true_carrying_capacity) + np.random.normal(0, 1, len(time_pinn))

# Initial PINN parameter guesses (slightly different from true values)
pinn_alpha_guess = 9
pinn_beta_guess = 0.18
pinn_carrying_capacity_guess = 48

# Optimization function to minimize residual percentage
def objective_pinn(params):
    alpha, beta, carrying_capacity = params
    predicted = microbial_growth_model(time_pinn, alpha, beta, carrying_capacity)
    residuals = actual_microbial_concentration - predicted
    residual_percentage = (residuals / actual_microbial_concentration) * 100
    return np.mean(np.abs(residual_percentage))

# Optimize PINN parameters
result_pinn = minimize(objective_pinn, x0=[pinn_alpha_guess, pinn_beta_guess, pinn_carrying_capacity_guess], method='Nelder-Mead')
optimized_alpha_pinn, optimized_beta_pinn, optimized_carrying_capacity_pinn = result_pinn.x

# Generate refined PINN predicted values
pinn_refined_concentration = microbial_growth_model(time_pinn, optimized_alpha_pinn, optimized_beta_pinn, optimized_carrying_capacity_pinn)

# Compute refined residuals
residuals_refined_pinn = actual_microbial_concentration - pinn_refined_concentration
residual_percentage_refined_pinn = (residuals_refined_pinn / actual_microbial_concentration) * 100
residual_below_threshold_refined_pinn = np.abs(residual_percentage_refined_pinn) < 5

# Plot results
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# First plot: PINN vs. Experimental Data Fit
ax[0].scatter(time_pinn, actual_microbial_concentration, label="Experimental Microbial Data", color='blue')
ax[0].plot(time_pinn, pinn_refined_concentration, label="Refined PINN Prediction", color='orange', linewidth=2)
ax[0].set_xlabel("Time")
ax[0].set_ylabel("Microbial Concentration")
ax[0].set_title("PINN Predicted vs. Experimental Microbial Concentration")
ax[0].legend()

# Second plot: Residual Analysis with only two labels
legend_elements_pinn = [
    Patch(facecolor='green', edgecolor='black', label='Residuals within ±5%'),
    Patch(facecolor='red', edgecolor='black', label='Residuals beyond ±5%')
]

ax[1].bar(time_pinn, residual_percentage_refined_pinn, color=np.where(residual_below_threshold_refined_pinn, 'green', 'red'))
ax[1].axhline(y=5, color='black', linestyle='dashed', linewidth=1, label="5% Threshold")
ax[1].axhline(y=-5, color='black', linestyle='dashed', linewidth=1)
ax[1].set_xlabel("Time")
ax[1].set_ylabel("Residuals (%)")
ax[1].set_title("Residual Analysis for PINN Model")
ax[1].legend(handles=legend_elements_pinn)

plt.tight_layout()
plt.show()
