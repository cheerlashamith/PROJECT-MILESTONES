import streamlit as st


def show():

    st.title("🦺 AI Site Safety Monitor")

    st.write(
        "Monitor worker safety compliance and identify missing PPE equipment."
    )

    st.subheader("👷 PPE Compliance Checklist")

    helmet = st.checkbox("🪖 Helmet")
    shoes = st.checkbox("👞 Safety Shoes")
    jacket = st.checkbox("🦺 Reflective Jacket")
    gloves = st.checkbox("🧤 Gloves")
    goggles = st.checkbox("🥽 Safety Goggles")
    harness = st.checkbox("🪢 Safety Harness")

    total_items = 6

    selected = sum([
        helmet,
        shoes,
        jacket,
        gloves,
        goggles,
        harness
    ])

    score = int(
        (selected / total_items) * 100
    )

    st.divider()

    st.subheader("📊 Safety Compliance Dashboard")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Compliance Score",
        f"{score}%"
    )

    c2.metric(
        "PPE Items",
        f"{selected}/{total_items}"
    )

    if score >= 90:
        risk = "Low"
        color = "🟢"

    elif score >= 60:
        risk = "Medium"
        color = "🟠"

    else:
        risk = "High"
        color = "🔴"

    c3.metric(
        "Risk Level",
        risk
    )

    c4.metric(
        "Site Status",
        "Safe" if score >= 80 else "Attention Required"
    )

    st.progress(score / 100)

    st.divider()

    st.subheader("🚨 Missing Safety Equipment")

    missing = []

    if not helmet:
        missing.append("Helmet")

    if not shoes:
        missing.append("Safety Shoes")

    if not jacket:
        missing.append("Reflective Jacket")

    if not gloves:
        missing.append("Gloves")

    if not goggles:
        missing.append("Safety Goggles")

    if not harness:
        missing.append("Safety Harness")

    if len(missing) == 0:
        st.success(
            "✅ All mandatory PPE equipment detected."
        )
    else:
        for item in missing:
            st.warning(
                f"⚠ Missing: {item}"
            )

    st.divider()

    st.subheader("🤖 AI Safety Recommendations")

    if score >= 90:
        st.success(
            "✅ Site safety compliance is excellent."
        )
        st.success(
            "✅ Continue periodic inspections."
        )

    elif score >= 60:
        st.warning(
            "⚠ Improve PPE compliance before starting hazardous activities."
        )
        st.warning(
            "⚠ Conduct additional safety awareness sessions."
        )

    else:
        st.error(
            "🚨 High safety risk detected."
        )
        st.error(
            "🚨 Work should not continue until mandatory PPE is provided."
        )

    st.divider()

    st.subheader("📈 Safety Compliance Analytics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Compliant Items",
        selected
    )

    col2.metric(
        "Missing Items",
        total_items - selected
    )

    col3.metric(
        "Compliance Rating",
        f"{score}/100"
    )