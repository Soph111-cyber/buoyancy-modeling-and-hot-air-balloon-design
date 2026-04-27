import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.optimize import brentq

st.set_page_config(page_title="Hot-Air Balloon Simulator", layout="wide")

st.title("🎈 Hot-Air Balloon Buoyancy Simulator")

st.markdown(
    "This interactive demo models the minimum radius of a spherical hot-air balloon needed to hover."
)

st.markdown("### ⚖️ Force Balance")

st.latex(r"""
\rho_{\text{out}} gV
=
\rho_{\text{hot}} gV
+
m_b g
+
m_{\text{people}} g
+
m_{\text{material}} g
""")

st.markdown("After canceling gravity:")

st.latex(r"""
(\rho_{\text{out}} - \rho_{\text{hot}})V
=
m_b
+
m_{\text{people}}
+
\eta A
""")

# =============================
# Constants
# =============================
R_specific = 287.058
P_atm = 101325
T_out = 288.15
g = 9.81

rho_out = P_atm / (R_specific * T_out)

# =============================
# Sidebar inputs
# =============================
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

# =============================
# Functions
# =============================
def volume(R):
    return (4 / 3) * np.pi * R**3

def surface_area(R):
    return 4 * np.pi * R**2

def balance_equation(R):
    return (rho_out - rho_hot) * volume(R) - eta * surface_area(R) - basket_mass - m_people

try:
    R_min = brentq(balance_equation, 0.1, 50)
except Exception:
    R_min = None

# =============================
# Results
# =============================
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

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Minimum radius", f"{R_min:.2f} m")

    with col5:
        st.metric("Minimum diameter", f"{diameter:.2f} m")

    with col6:
        st.metric("Balloon volume", f"{V:.1f} m³")

    # =============================
    # 3D Balloon Visualization
    # =============================
    st.markdown("### 🎈 3D Balloon Visualization")

    theta = np.linspace(0, 2 * np.pi, 80)
    phi = np.linspace(0, np.pi, 80)

    theta, phi = np.meshgrid(theta, phi)

    x = R_min * np.sin(phi) * np.cos(theta)
    y = R_min * np.sin(phi) * np.sin(theta)
    z = R_min * np.cos(phi) + R_min + 2

    pressure_proxy = -z

    fig3d = go.Figure()

    fig3d.add_trace(
        go.Surface(
            x=x,
            y=y,
            z=z,
            surfacecolor=pressure_proxy,
            opacity=0.75,
            colorscale="RdYlBu",
            showscale=True,
            colorbar=dict(title="Pressure proxy")
        )
    )

    basket_z = 0
    basket_size = R_min * 0.35

    bx = [-basket_size, basket_size, basket_size, -basket_size, -basket_size]
    by = [-basket_size, -basket_size, basket_size, basket_size, -basket_size]
    bz = [basket_z] * 5

    fig3d.add_trace(
        go.Scatter3d(
            x=bx,
            y=by,
            z=bz,
            mode="lines",
            line=dict(width=8),
            name="Basket"
        )
    )

    rope_points = [
        (-basket_size, -basket_size),
        (basket_size, -basket_size),
        (basket_size, basket_size),
        (-basket_size, basket_size),
    ]

    for rx, ry in rope_points:
        fig3d.add_trace(
            go.Scatter3d(
                x=[rx, rx * 0.45],
                y=[ry, ry * 0.45],
                z=[basket_z, R_min + 2 - R_min * 0.85],
                mode="lines",
                line=dict(width=4),
                showlegend=False
            )
        )

    fig3d.add_trace(
        go.Cone(
            x=[0],
            y=[0],
            z=[R_min + 2],
            u=[0],
            v=[0],
            w=[R_min * 0.45],
            sizemode="absolute",
            sizeref=R_min * 0.6,
            name="Buoyant force"
        )
    )

    fig3d.update_layout(
        height=700,
        scene=dict(
            xaxis_title="x (m)",
            yaxis_title="y (m)",
            zaxis_title="z (m)",
            aspectmode="data"
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        title="3D Model of the Required Hot-Air Balloon"
    )

    st.plotly_chart(fig3d, use_container_width=True)

    st.markdown(
        "The color gradient represents a qualitative pressure proxy: lower points experience greater pressure, creating upward buoyant force."
    )

    # =============================
    # Mass breakdown
    # =============================
    st.markdown("### 🧮 Mass Breakdown")

    st.write(f"People mass: **{m_people:.1f} kg**")
    st.write(f"Basket + equipment mass: **{basket_mass:.1f} kg**")
    st.write(f"Balloon material mass: **{material_mass:.1f} kg**")

    # =============================
    # Force balance
    # =============================
    st.markdown("### ⚖️ Force Balance at Hovering")

    buoyant_force = rho_out * g * V
    downward_force = (
        rho_hot * g * V
        + basket_mass * g
        + m_people * g
        + material_mass * g
    )

    st.write(f"Upward buoyant force: **{buoyant_force:.1f} N**")
    st.write(f"Total downward force: **{downward_force:.1f} N**")

    if abs(buoyant_force - downward_force) < 1:
        st.success("The balloon is approximately in equilibrium.")

    # =============================
    # Plot 1
    # =============================
    st.markdown("### 📈 Net Lift vs Radius")

    R_values = np.linspace(1, 15, 300)
    net_lift = [
        (rho_out - rho_hot) * volume(R)
        - eta * surface_area(R)
        - basket_mass
        - m_people
        for R in R_values
    ]

    fig, ax = plt.subplots()
    ax.plot(R_values, net_lift)
    ax.axhline(0, linestyle="--")
    ax.axvline(R_min, linestyle="--")
    ax.set_xlabel("Radius (m)")
    ax.set_ylabel("Net lift (kg equivalent)")
    st.pyplot(fig)

    # =============================
    # Plot 2
    # =============================
    st.markdown("### 🌡️ Radius vs Temperature")

    temps = np.linspace(80, 120, 40)
    radii = []

    for temp in temps:
        T = temp + 273.15
        rho_h = P_atm / (R_specific * T)

        def eq(R):
            return (
                (rho_out - rho_h) * volume(R)
                - eta * surface_area(R)
                - basket_mass
                - m_people
            )

        try:
            radii.append(brentq(eq, 0.1, 50))
        except Exception:
            radii.append(np.nan)

    fig2, ax2 = plt.subplots()
    ax2.plot(temps, radii)
    ax2.scatter([T_hot_C], [R_min])
    ax2.set_xlabel("Temperature (°C)")
    ax2.set_ylabel("Radius (m)")
    st.pyplot(fig2)

    # =============================
    # Insight
    # =============================
    st.markdown("### 🧠 Key Insight")

    st.latex(r"\text{Lift} \sim R^3")
    st.latex(r"\text{Material mass} \sim R^2")

    st.markdown(
        "Volume grows faster than surface area, which is why larger balloons are more efficient."
    )

else:
    st.error("No valid solution found.")
