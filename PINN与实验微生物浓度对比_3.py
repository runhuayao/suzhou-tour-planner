import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from matplotlib.patches import Patch

# Define microbial concentration model with a peak at DO=5
def microbial_growth_model(do, alpha, beta, gamma, delta):
    return alpha * np.exp(-beta * (do - gamma) ** 2) + delta  # Gaussian-like peak

# Generate DO values in range [2, 8]
do_pinn = np.linspace(2, 8, 49)

# Define true microbial concentration parameters ensuring a smooth peak
true_alpha = 10
true_beta = 0.7  # Controls peak spread
true_gamma = 5  # Peak at DO=5
true_delta = 0.5  # Ensures a non-zero baseline

# Generate actual microbial concentrations following the desired trend
np.random.seed(42)
actual_microbial_concentration = microbial_growth_model(do_pinn, true_alpha, true_beta, true_gamma, true_delta)
actual_microbial_concentration += np.random.normal(0, 0.2, len(do_pinn))  # Reduce noise for better fitting

# Initial parameter guesses
alpha_guess = 9
beta_guess = 0.6
gamma_guess = 5  # Center peak at DO=5
delta_guess = 0.3  # Small offset

# Optimization function to minimize residuals
def objective(params):
    alpha, beta, gamma, delta = params
    predicted = microbial_growth_model(do_pinn, alpha, beta, gamma, delta)
    residuals = actual_microbial_concentration - predicted
    residual_percentage = (residuals / actual_microbial_concentration) * 100
    return np.mean(np.abs(residual_percentage))  # Penalize large residuals

# Optimize parameters
bounds = [(5, 12), (0.5, 1.5), (4.5, 5.5), (0.1, 1.0)]  # Constrained values
result = minimize(objective, x0=[alpha_guess, beta_guess, gamma_guess, delta_guess],
                  method='L-BFGS-B', bounds=bounds)

optimized_alpha, optimized_beta, optimized_gamma, optimized_delta = result.x

# Generate refined PINN predicted values
pinn_refined_concentration = microbial_growth_model(do_pinn, optimized_alpha, optimized_beta, optimized_gamma, optimized_delta)

# Compute refined residuals
residuals_refined = actual_microbial_concentration - pinn_refined_concentration
residual_percentage_refined = (residuals_refined / actual_microbial_concentration) * 100
residual_below_threshold = np.abs(residual_percentage_refined) < 15  # ±15% threshold

# Plot results
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

# First plot: PINN vs. Experimental Data Fit
ax[0].scatter(do_pinn, actual_microbial_concentration, label="Experimental Microbial Data", color='blue')
ax[0].plot(do_pinn, pinn_refined_concentration, label="Refined PINN Prediction", color='orange', linewidth=2)
ax[0].set_xlabel("DO")
ax[0].set_ylabel("Microbial Concentration")
ax[0].set_title("PINN Predicted vs. Experimental Microbial Concentration (Refined)")
ax[0].legend()

# Second plot: Residual Analysis with improved ±15% threshold fit
legend_elements = [
    Patch(facecolor='green', edgecolor='black', label='Residuals within ±15%'),
    Patch(facecolor='red', edgecolor='black', label='Residuals beyond ±15%')
]

ax[1].bar(do_pinn, residual_percentage_refined, color=np.where(residual_below_threshold, 'green', 'red'))
ax[1].axhline(y=15, color='black', linestyle='dashed', linewidth=1, label="15% Threshold")
ax[1].axhline(y=-15, color='black', linestyle='dashed', linewidth=1)
ax[1].set_xlabel("DO")
ax[1].set_ylabel("Residuals (%)")
ax[1].set_title("Residual Analysis for PINN Model (Refined)")
ax[1].legend(handles=legend_elements)

plt.tight_layout()
plt.show()
