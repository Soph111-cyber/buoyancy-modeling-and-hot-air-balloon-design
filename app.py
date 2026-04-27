import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

st.set_page_config(page_title="Hot-Air Balloon Buoyancy Demo", layout="wide")

st.title("🎈 Hot-Air Balloon Buoyancy Simulator")
st.markdown("""
This interactive demo models the minimum radius of a spherical hot-air balloon needed to hover.

The force balance is:

\\[
\\rho_{out} gV = \\rho_{hot} gV + m_b g + m_{people} g + m_{material} g
\\]

After canceling \\(g\\):

\\[
(\\rho_{out}-\\rho_{hot})V = m_b + m_{people} + \\eta A
\\]
""")

# -----------------------------
# Constants
# -----------------------------
R_specific = 287.058
P_atm = 101325
T_out = 288.15
g = 9.81

rho_out = P_atm / (R_specific * T_out)

# -----------------------------
# Sidebar inputs
# -----------------------------
st.sidebar.header("Input Parameters")

n_people = st.sidebar.slider("Number of people", 1, 10, 4)
mass_per_person = st.sidebar.slider("Mass per person (kg)", 40, 100, 70)
T_hot_C = st.sidebar.slider("Hot air temperature (°C)", 80, 120, 100)
basket_mass = st.sidebar.slider("Basket + equipment mass (kg)", 100, 500, 250)
material_density_g = st.sidebar.slider("Balloon material density (g/m²)", 20, 120, 64)

T_hot_K = T_hot_C + 273.15
rho_hot = P_atm / (R_specific * T_hot_K)
eta = material_density_g / 1000

m_people = n_people * mass_per_person

# -----------------------------
# Balloon equations
# -----------------------------
def volume(R):
    return (4 / 3) * np.pi * R**3

def surface_area(R):
    return 4 * np.pi * R**2

def balance_equation(R):
    return (rho_out - rho_hot) * volume(R) - eta * surface_area(R) - basket_mass - m_people

# Solve radius
try:
    R_min = brentq(balance_equation, 0.1, 50)
except ValueError:
    R_min = None

# -----------------------------
# Main results
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Outside air density", f"{rho_out:.3f} kg/m³")

with col2:
    st.metric("Hot air density", f"{rho_hot:.3f} kg/m³")

with col3:
    st.metric("Density difference", f"{rho_out - rho_hot:.3f} kg/m³")

st.divider()

if R_min is not None:
    diameter = 2 * R_min
    V = volume(R_min)
    A = surface_area(R_min)
    material_mass = eta * A
    total_payload = basket_mass + m_people + material_mass

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Minimum radius", f"{R_min:.2f} m")

    with col5:
        st.metric("Minimum diameter", f"{diameter:.2f} m")

    with col6:
        st.metric("Balloon volume", f"{V:.1f} m³")

    st.markdown("### 🧮 Mass Breakdown")

    st.write(f"People mass: **{m_people:.1f} kg**")
    st.write(f"Basket + equipment mass: **{basket_mass:.1f} kg**")
    st.write(f"Balloon material mass: **{material_mass:.1f} kg**")
    st.write(f"Total supported mass: **{total_payload:.1f} kg**")

    st.markdown("### ⚖️ Force Balance at Hovering")

    buoyant_force = rho_out * g * V
    hot_air_weight = rho_hot * g * V
    basket_weight = basket_mass * g
    people_weight = m_people * g
    material_weight = material_mass * g
    downward_force = hot_air_weight + basket_weight + people_weight + material_weight

    st.write(f"Upward buoyant force: **{buoyant_force:.1f} N**")
    st.write(f"Total downward force: **{downward_force:.1f} N**")

    if abs(buoyant_force - downward_force) < 1:
        st.success("The balloon is approximately in hovering equilibrium.")

    # -----------------------------
    # Plot 1: force balance vs radius
    # -----------------------------
    st.markdown("### 📈 Net Lift vs Balloon Radius")

    R_values = np.linspace(1, 15, 300)
    net_lift_mass = [
        (rho_out - rho_hot) * volume(R) - eta * surface_area(R) - basket_mass - m_people
        for R in R_values
    ]

    fig, ax = plt.subplots()
    ax.plot(R_values, net_lift_mass)
    ax.axhline(0, linestyle="--")
    ax.axvline(R_min, linestyle="--")
    ax.set_xlabel("Radius (m)")
    ax.set_ylabel("Net lift capacity after payload (kg)")
    ax.set_title("Net Lift Capacity vs Radius")
    st.pyplot(fig)

    st.markdown("""
    **Interpretation:**  
    The balloon can hover when the curve crosses zero.  
    Below this radius, the balloon is too small.  
    Above this radius, the balloon has extra lifting capacity.
    """)

    # -----------------------------
    # Plot 2: radius vs temperature
    # -----------------------------
    st.markdown("### 🌡️ Required Radius Under Different Temperatures")

    temps_C = np.linspace(80, 120, 41)
    radii = []

    for temp_C in temps_C:
        temp_K = temp_C + 273.15
        rho_h = P_atm / (R_specific * temp_K)

        def eq_temp(R):
            return (rho_out - rho_h) * volume(R) - eta * surface_area(R) - basket_mass - m_people

        try:
            radii.append(brentq(eq_temp, 0.1, 50))
        except ValueError:
            radii.append(np.nan)

    fig2, ax2 = plt.subplots()
    ax2.plot(temps_C, radii)
    ax2.scatter([T_hot_C], [R_min])
    ax2.set_xlabel("Hot Air Temperature (°C)")
    ax2.set_ylabel("Required Radius (m)")
    ax2.set_title("Required Radius vs Hot Air Temperature")
    st.pyplot(fig2)

    st.markdown("""
    **Model insight:**  
    Higher temperature lowers the density of the hot air, increasing the density difference  
    \\(\\rho_{out} - \\rho_{hot}\\).  
    Therefore, the required radius decreases.
    """)

    # -----------------------------
    # Mathematical explanation
    # -----------------------------
    st.markdown("### 🧠 Mathematical Insight")

    st.markdown("""
    The key scaling relationship is:

    \\[
    \\text{Useful lift} \\sim R^3
    \\]

    because lift depends on volume, while

    \\[
    \\text{Material mass} \\sim R^2
    \\]

    because fabric mass depends on surface area.

    This explains why larger balloons become more efficient:
    volume grows faster than surface area.
    """)

else:
    st.error("No valid radius found under the current parameters.")
