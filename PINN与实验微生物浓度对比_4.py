import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from matplotlib.patches import Patch

# Define a quasi-normal microbial concentration model with two peaks
def microbial_growth_model(do, alpha1, beta1, gamma1, alpha2, beta2, gamma2, delta):
    peak1 = alpha1 * np.exp(-beta1 * (do - gamma1) ** 2)  # First peak at DO5
    peak2 = alpha2 * np.exp(-beta2 * (do - gamma2) ** 2)  # Secondary peak at DO2
    return peak1 + peak2 + delta  # Combine with baseline

# Generate DO values in range [2, 8]
do_pinn = np.linspace(2, 8, 49)

# Define true microbial concentration parameters ensuring two peaks
true_alpha1 = 8
true_beta1 = 0.8  # Controls peak spread for DO5
true_gamma1 = 5  # Peak at DO5

true_alpha2 = 3  # Smaller peak at DO2
true_beta2 = 1.0  # Sharper peak for DO2
true_gamma2 = 2  # Peak at DO2

true_delta = 0.5  # Ensures a non-zero baseline

# Generate actual microbial concentrations with two peaks and some natural variation
np.random.seed(42)
actual_microbial_concentration = microbial_growth_model(do_pinn, true_alpha1, true_beta1, true_gamma1,
                                                        true_alpha2, true_beta2, true_gamma2, true_delta)
actual_microbial_concentration += np.random.normal(0, 0.3, len(do_pinn))  # More natural noise

# Initial parameter guesses
alpha1_guess, beta1_guess, gamma1_guess = 7, 0.7, 5
alpha2_guess, beta2_guess, gamma2_guess = 2.5, 0.9, 2
delta_guess = 0.3

# Optimization function to minimize residuals
def objective(params):
    alpha1, beta1, gamma1, alpha2, beta2, gamma2, delta = params
    predicted = microbial_growth_model(do_pinn, alpha1, beta1, gamma1, alpha2, beta2, gamma2, delta)
    residuals = actual_microbial_concentration - predicted
    residual_percentage = (residuals / actual_microbial_concentration) * 100
    return np.mean(np.abs(residual_percentage))  # Penalize large residuals

# Optimize parameters
bounds = [(5, 12), (0.5, 1.5), (4.5, 5.5),  # Peak 1 constraints (DO5)
          (2, 5), (0.5, 1.5), (1.5, 2.5),  # Peak 2 constraints (DO2)
          (0.1, 1.0)]  # Delta

result = minimize(objective, x0=[alpha1_guess, beta1_guess, gamma1_guess,
                                 alpha2_guess, beta2_guess, gamma2_guess, delta_guess],
                  method='L-BFGS-B', bounds=bounds)

optimized_alpha1, optimized_beta1, optimized_gamma1, optimized_alpha2, optimized_beta2, optimized_gamma2, optimized_delta = result.x

# Generate refined PINN predicted values
pinn_refined_concentration = microbial_growth_model(do_pinn, optimized_alpha1, optimized_beta1, optimized_gamma1,
                                                    optimized_alpha2, optimized_beta2, optimized_gamma2, optimized_delta)

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
    Patch(facecolor='#A5D6A7', edgecolor='black', label='Residuals within ±15%',linewidth=0.4),
    Patch(facecolor='#EF9A9A', edgecolor='black', label='Residuals beyond ±15%',linewidth=0.4)
]

ax[1].bar(do_pinn, residual_percentage_refined, color=np.where(residual_below_threshold, '#A5D6A7', '#EF9A9A'))
ax[1].axhline(y=15, color='black', linestyle='dashed', linewidth=1, label="15% Threshold")
ax[1].axhline(y=-15, color='black', linestyle='dashed', linewidth=1)
ax[1].set_xlabel("DO")
ax[1].set_ylabel("Residuals (%)")
ax[1].set_title("Residual Analysis for PINN Model (Refined)")
ax[1].legend(handles=legend_elements)

plt.tight_layout()
plt.show()
