import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.optimize import brentq

# =============================
# Page Config
# =============================
st.set_page_config(
    page_title="Hot-Air Balloon Buoyancy Simulator",
    page_icon="🎈",
    layout="wide"
)

# =============================
# Product-style UI CSS
# =============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff7f2 0%, #f7fbff 45%, #f7f4ff 100%);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

h1 {
    font-size: 3.1rem !important;
    font-weight: 850 !important;
    letter-spacing: -1px;
    color: #26233a;
}

h2, h3 {
    color: #312b4f;
    font-weight: 780 !important;
}

div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.76);
    border: 1px solid rgba(120, 120, 160, 0.18);
    padding: 18px;
    border-radius: 22px;
    box-shadow: 0 8px 24px rgba(80, 70, 120, 0.08);
}

div[data-testid="stMetricLabel"] {
    font-size: 0.95rem;
    color: #6b647f;
}

div[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 800;
    color: #2b2740;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fff2ec 0%, #f5f3ff 100%);
    border-right: 1px solid rgba(120, 120, 160, 0.15);
}

div[data-testid="stPlotlyChart"],
div[data-testid="stPyplot"] {
    background: rgba(255, 255, 255, 0.76);
    padding: 18px;
    border-radius: 24px;
    box-shadow: 0 8px 26px rgba(80, 70, 120, 0.08);
    border: 1px solid rgba(120, 120, 160, 0.15);
}

.katex-display {
    background: rgba(255, 255, 255, 0.68);
    border-radius: 18px;
    padding: 14px 10px;
    box-shadow: 0 6px 18px rgba(80, 70, 120, 0.05);
}

div[data-testid="stAlert"] {
    border-radius: 18px;
}

hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(80, 70, 120, 0.28), transparent);
}

p, li {
    font-size: 1.05rem;
    line-height: 1.65;
    color: #343044;
}
</style>
""", unsafe_allow_html=True)

# =============================
# Title + Hero Section
# =============================
st.title("🎈 Hot-Air Balloon Buoyancy Simulator")

st.markdown("""
<div style="
    background: rgba(255, 255, 255, 0.72);
    padding: 28px 32px;
    border-radius: 28px;
    border: 1px solid rgba(120,120,160,0.18);
    box-shadow: 0 12px 35px rgba(80,70,120,0.10);
    margin-bottom: 28px;
">
    <h3 style="margin-top:0;">A calculus-powered design tool for buoyancy and hot-air balloon modeling</h3>
    <p style="margin-bottom:0;">
        Adjust temperature, passenger load, and material density to see how Archimedes’ principle
        becomes an interactive engineering model.
    </p>
</div>
""", unsafe_allow_html=True)

# =============================
# Force Balance Formulas
# =============================
st.markdown("### ⚖️ Force Balance")

st.markdown(
    "A hot-air balloon hovers when the upward buoyant force equals the total downward weight."
)

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
# Sidebar Inputs
# =============================
st.sidebar.markdown("## 🎛️ Control Panel")
st.sidebar.caption("Tune the physical parameters and watch the model update in real time.")

n_people = st.sidebar.slider("Number of people", 1, 10, 4)
mass_per_person = st.sidebar.slider("Mass per person (kg)", 40, 100, 70)
T_hot_C = st.sidebar.slider("Hot air temperature (°C)", 80, 120, 100)
basket_mass = st.sidebar.slider("Basket + equipment mass (kg)", 100, 500, 250)
material_density_g = st.sidebar.slider("Balloon material density (g/m²)", 20, 120, 64)

# =============================
# Derived Quantities
# =============================
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
    return (
        (rho_out - rho_hot) * volume(R)
        - eta * surface_area(R)
        - basket_mass
        - m_people
    )

try:
    R_min = brentq(balance_equation, 0.1, 50)
except Exception:
    R_min = None

# =============================
# Top Metrics
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
            opacity=0.76,
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
            name="Buoyant force",
            showscale=False
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
        margin=dict(l=0, r=0, b=0, t=35),
        title="3D Model of the Required Hot-Air Balloon"
    )

    st.plotly_chart(fig3d, use_container_width=True)

    st.markdown(
        "The color gradient represents a qualitative pressure proxy: lower points experience greater pressure, creating upward buoyant force."
    )

    # =============================
    # Column Integration Animation
    # =============================
    st.markdown("### 🧊 Column Integration Animation")

    st.markdown("""
    This animation visualizes the core idea behind the double integral.

    Instead of treating buoyancy as one mysterious upward force, we decompose the balloon into many vertical columns.  
    Each column contributes a small upward force because the pressure at the bottom is greater than the pressure at the top.
    """)

    st.latex(r"""
    F_z
    =
    \iint_D
    \left[
    P_{\text{bottom}}(x,y)
    -
    P_{\text{top}}(x,y)
    \right]
    dA
    """)

    st.latex(r"""
    P_{\text{bottom}} - P_{\text{top}}
    =
    \rho_{\text{out}} g
    \left(
    z_{\text{top}} - z_{\text{bottom}}
    \right)
    """)

    R_vis = R_min
    num_columns = 11

    xs = np.linspace(-R_vis, R_vis, num_columns)
    ys = np.linspace(-R_vis, R_vis, num_columns)

    column_data = []

    for x0 in xs:
        for y0 in ys:
            if x0**2 + y0**2 <= R_vis**2:
                h = np.sqrt(R_vis**2 - x0**2 - y0**2)

                z_bottom = R_vis + 2 - h
                z_top = R_vis + 2 + h

                column_height = z_top - z_bottom
                force_proxy = column_height

                column_data.append((x0, y0, z_bottom, z_top, force_proxy))

    column_data.sort(key=lambda c: c[0]**2 + c[1]**2)

    frames = []

    for k in range(1, len(column_data) + 1):
        visible_columns = column_data[:k]
        frame_traces = []

        for x0, y0, z_bottom, z_top, force_proxy in visible_columns:
            frame_traces.append(
                go.Scatter3d(
                    x=[x0, x0],
                    y=[y0, y0],
                    z=[z_bottom, z_top],
                    mode="lines",
                    line=dict(width=6),
                    showlegend=False
                )
            )

            frame_traces.append(
                go.Cone(
                    x=[x0],
                    y=[y0],
                    z=[z_top],
                    u=[0],
                    v=[0],
                    w=[force_proxy * 0.15],
                    sizemode="absolute",
                    sizeref=R_vis * 0.25,
                    showscale=False,
                    showlegend=False
                )
            )

        frames.append(go.Frame(data=frame_traces, name=str(k)))

    fig_col = go.Figure(data=[], frames=frames)

    theta_c = np.linspace(0, 2 * np.pi, 60)
    phi_c = np.linspace(0, np.pi, 60)
    theta_c, phi_c = np.meshgrid(theta_c, phi_c)

    x_s = R_vis * np.sin(phi_c) * np.cos(theta_c)
    y_s = R_vis * np.sin(phi_c) * np.sin(theta_c)
    z_s = R_vis * np.cos(phi_c) + R_vis + 2

    fig_col.add_trace(
        go.Surface(
            x=x_s,
            y=y_s,
            z=z_s,
            opacity=0.18,
            colorscale="Blues",
            showscale=False,
            name="Balloon shell"
        )
    )

    fig_col.update_layout(
        height=700,
        scene=dict(
            xaxis_title="x",
            yaxis_title="y",
            zaxis_title="z",
            aspectmode="data"
        ),
        title="Column Integral Interpretation of Buoyancy",
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=120, redraw=True),
                                transition=dict(duration=0),
                                fromcurrent=True
                            )
                        ],
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[
                            [None],
                            dict(
                                frame=dict(duration=0, redraw=False),
                                mode="immediate",
                                transition=dict(duration=0)
                            )
                        ],
                    ),
                ],
            )
        ],
        margin=dict(l=0, r=0, b=0, t=40)
    )

    st.plotly_chart(fig_col, use_container_width=True)

    st.markdown("""
    **Interpretation:**  
    Each vertical column represents one small area element in the projected disk.  
    The taller the column, the larger the pressure difference between its bottom and top.  
    Adding all column contributions gives the total buoyant force.
    """)

    st.latex(r"""
    F_z
    =
    \iiint_W
    \rho_{\text{out}} g
    \, dV
    =
    \rho_{\text{out}} gV
    """)

    # =============================
    # Mass Breakdown
    # =============================
    st.markdown("### 🧮 Mass Breakdown")

    st.write(f"People mass: **{m_people:.1f} kg**")
    st.write(f"Basket + equipment mass: **{basket_mass:.1f} kg**")
    st.write(f"Balloon material mass: **{material_mass:.1f} kg**")

    # =============================
    # Force Balance
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
    # Plot 1: Net Lift vs Radius
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
    ax.set_ylabel("Net lift capacity after payload (kg equivalent)")
    ax.set_title("Net Lift vs Balloon Radius")
    st.pyplot(fig)

    st.markdown("""
    The balloon begins to hover at the point where the curve crosses zero.  
    To the left of this point, it cannot lift the load. To the right, it has extra lifting capacity.
    """)

    # =============================
    # Plot 2: Radius vs Temperature
    # =============================
    st.markdown("### 🌡️ Required Radius vs Temperature")

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
    ax2.set_xlabel("Hot air temperature (°C)")
    ax2.set_ylabel("Required radius (m)")
    ax2.set_title("Required Radius vs Temperature")
    st.pyplot(fig2)

    st.markdown("""
    Higher temperature lowers the density of the hot air, increasing the density difference:
    """)

    st.latex(r"""
    \rho_{\text{out}} - \rho_{\text{hot}}
    """)

    st.markdown("Therefore, the required balloon radius decreases.")

    # =============================
    # Key Insight
    # =============================
    st.markdown("### 🧠 Key Mathematical Insight")

    st.latex(r"\text{Useful lift} \sim R^3")
    st.latex(r"\text{Material mass} \sim R^2")

    st.markdown("""
    Volume grows faster than surface area.  
    This is why larger balloons become more efficient: the useful lift increases cubically, while the fabric cost increases quadratically.
    """)

else:
    st.error("No valid solution found under the current parameters.")
