import streamlit as st
import sympy as smp
from fuzzywuzzy import process
from decimal import Decimal

# ──────────────────────────  Page config  ──────────────────────────
st.set_page_config(
    page_title="Pet Value Calculator",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="auto",
)

# ───────────────────────────   Styling   ───────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fugaz+One&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Fugaz One', sans-serif;
        background-color: #0d0d0d;
        color: #fff;
    }
    .stTextInput > div > div > input,
    .stNumberInput input {
        border-radius: 999px !important;
        background-color: #1a1a1a;
        color: white;
        padding: 0.6rem 1rem;
    }
    .stSelectbox > div > div {
        border-radius: 999px !important;
        background-color: #1a1a1a;
        color: white;
    }
    .stButton button {
        background-color: #ff5722;
        color: white;
        border: none;
        border-radius: 999px;
        padding: 0.6rem 2rem;
        font-size: 1.1rem;
        margin-top: 1rem;
    }
    .stButton button:hover {
        background-color: #e64a19;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔥 Pet Value Calculator")

# ───────────────────────  Variant multipliers  ─────────────────────
variant_multipliers = {
    "normal": 1,
    "shiny": 40,
    "mythic": 80,
    "shiny mythic": 320,
}

# ────────────────────────  Helper functions  ───────────────────────
def find_closest_match(input_string, valid_strings, threshold=70):
    match, score = process.extractOne(input_string, valid_strings)
    return match if score >= threshold else None


def calculate_value(
    type_input,
    variant_input,
    exist=None,
    rarity=None,
    demand=None,
    c=None,
    price=None,
    variant_multi=None,
    island_chance=None,
):
    x_sym = smp.Symbol("x")
    multiplier = variant_multipliers.get(variant_input, 1)

    if type_input in ["permanent", "limited"]:
        i1 = smp.integrate(
            smp.sqrt((rarity * multiplier) / (exist + 2)), (x_sym, 0, exist + 2)
        )
        i2 = smp.integrate(
            smp.sqrt((rarity * multiplier) / exist), (x_sym, 0, exist)
        )
        multiplier_factor = 0.1 if type_input == "permanent" else 0.5
        diff = (i1 - i2) * (1 + multiplier_factor * smp.exp(0.25 * demand))

    elif type_input == "aura":
        safe_lower = 1e-6  # prevent divide by zero
        const_expr = (rarity * multiplier) * (island_chance / 100)
        i1 = smp.integrate(
            smp.sqrt(const_expr / (exist + 1)), (x_sym, safe_lower, exist + 1)
        )
        i2 = smp.integrate(
            smp.sqrt(const_expr / exist), (x_sym, safe_lower, exist)
        )
        diff = (i1 - i2) * (1 + 0.1 * smp.exp(0.25 * demand))

    elif type_input == "pass":
        i1 = smp.integrate(
            (((1 - smp.exp(-c * x_sym)) / c) / rarity), (x_sym, 0, demand + 1)
        )
        i2 = smp.integrate(
            (((1 - smp.exp(-c * x_sym)) / c) / rarity), (x_sym, 0, demand)
        )
        diff = (i1 - i2) ** 3
        if variant_input == "normal":
            diff = smp.sqrt(diff) / 2
        else:
            diff = diff / (1 / (variant_multi / 10))
            diff = 0.5 * smp.sqrt(diff)

    elif type_input == "shop":
        i1 = smp.integrate(
            (price * (1 - smp.exp(-c * x_sym))) / (c / x_sym), (x_sym, 0, demand + 2)
        )
        i2 = smp.integrate(
            (price * (1 - smp.exp(-c * x_sym))) / (c / x_sym), (x_sym, 0, demand)
        )
        diff = (i1 - i2) ** 1.15
        if variant_input != "normal":
            diff = diff / (1 / variant_multi)
        diff = 0.5 * smp.sqrt(diff)
    else:
        return None

    return diff.evalf()


# ────────────────────────────  UI  ────────────────────────────
pet_type = st.selectbox("Select pet type", ["permanent", "limited", "pass", "shop", "aura"])
variant = st.selectbox("Select pet variant", ["normal", "shiny", "mythic", "shiny mythic"])
variant_multi = variant_multipliers[variant]

value = None  # will hold the final result

# ─────────────────────────  PERMANENT / LIMITED  ─────────────────────────
if pet_type in ["permanent", "limited"]:
    exist = st.number_input("Enter # of exist", min_value=1, step=1)
    rarity = st.number_input("Enter rarity", min_value=0.0001, format="%.4f")

    # ▼ Live preview
    st.caption(f"**Preview — Exist:** {exist:,}  • Rarity:** {rarity:,.4f}")

    demand = st.slider("Enter demand (1‑20)", 1, 20)

    if st.button("Calculate Value"):
        value = calculate_value(
            pet_type, variant, exist=exist, rarity=rarity, demand=demand
        )

# ────────────────────────────────  AURA  ───────────────   ─────────────────
elif pet_type == "aura":
    exist = st.number_input("Enter # of exist", min_value=1, step=1)
    rarity = st.number_input("Enter rarity", min_value=0.0001, format="%.4f")
    island_chance = st.number_input("Enter island chance", min_value=0.0001, format="%.4f")

    # ▼ Live preview
    st.caption(
        f"**Preview — Exist:** {exist:,} • Rarity:** {rarity:,.4f} • Island chance:** {island_chance:,.4f}"
    )

    demand = st.slider("Enter demand (1‑20)", 1, 20)
    if st.button("Calculate Value"):
        value = calculate_value(
            pet_type,
            variant,
            exist=exist,
            rarity=rarity,
            demand=demand,
            island_chance=island_chance,
        )

# ───────────────────────────────  PASS  ────────────────────────────────
elif pet_type == "pass":
    rarity = st.number_input("Enter rarity", min_value=0.0001, format="%.4f")
    demand = st.slider("Enter demand (1‑20)", 1, 20)
    c = st.number_input("Enter c value (0.01 – 1)", min_value=0.01, format="%.3f")

    # ▼ Live preview
    st.caption(f"**Preview — Rarity:** {rarity:,.4f} • c:** {c:,.3f}")

    if st.button("Calculate Value"):
        value = calculate_value(
            pet_type,
            variant,
            rarity=Decimal(rarity),
            demand=demand,
            c=Decimal(c),
            variant_multi=variant_multi,
        )

# ───────────────────────────────  SHOP  ────────────────────────────────
elif pet_type == "shop":
    price = st.number_input("Enter price", min_value=1, step=1)
    demand = st.slider("Enter demand (1‑20)", 1, 20)
    c = st.number_input("Enter c value (0.01 – 1)", min_value=0.01, format="%.3f")

    # ▼ Live preview
    st.caption(f"**Preview — Price:** {price:,} • c:** {c:,.3f}")

    if st.button("Calculate Value"):
        value = calculate_value(
            pet_type,
            variant,
            price=price,
            demand=demand,
            c=Decimal(c),
            variant_multi=variant_multi,
        )

# ───────────────────────────  Result display  ───────────────────────────
if value is not None:
    try:
        evaluated = value.evalf()
        if evaluated.is_number:
            st.markdown(f"### 📈 Estimated Value: **{round(float(evaluated), 2):,}**")
        else:
            st.warning("The expression could not be fully evaluated.")
    except Exception as e:
        st.error(f"Error converting value: {e}")
