import streamlit as st
import pandas as pd


# ---------------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------------

st.set_page_config(
    page_title="Vireo Refund Analysis",
    page_icon="💰",
    layout="wide"
)


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------

st.title("Vireo Refund Analysis Dashboard")

st.write(
    "Monthly refund analysis by reason and agent using cleaned "
    "and deduplicated refund records."
)


# ---------------------------------------------------------
# LOAD OUTPUT FILES
# ---------------------------------------------------------

monthly = pd.read_csv("outputs/monthly_refunds.csv")
reason = pd.read_csv("outputs/reason_summary.csv")
agents = pd.read_csv("outputs/agent_summary.csv")
refunds = pd.read_csv("outputs/cleaned_refunds.csv")


# ---------------------------------------------------------
# CONVERT DATA TYPES
# ---------------------------------------------------------

monthly["refund_value"] = pd.to_numeric(
    monthly["refund_value"],
    errors="coerce"
)

monthly["refund_rate_pct"] = pd.to_numeric(
    monthly["refund_rate_pct"],
    errors="coerce"
)

reason["total_refund_value"] = pd.to_numeric(
    reason["total_refund_value"],
    errors="coerce"
)

reason["refund_tickets"] = pd.to_numeric(
    reason["refund_tickets"],
    errors="coerce"
)

reason["refund_share_pct"] = pd.to_numeric(
    reason["refund_share_pct"],
    errors="coerce"
)

agents["total_refund_value"] = pd.to_numeric(
    agents["total_refund_value"],
    errors="coerce"
)

agents["refund_tickets"] = pd.to_numeric(
    agents["refund_tickets"],
    errors="coerce"
)

agents["refund_rate_pct"] = pd.to_numeric(
    agents["refund_rate_pct"],
    errors="coerce"
)


# ---------------------------------------------------------
# BUSINESS ANALYSIS DATA
# ---------------------------------------------------------

# The cleaned file contains all refund records for auditability.
# For the dashboard, keep one record per ticket.
refunds_analysis = (
    refunds
    .sort_values(
        "source_system",
        key=lambda x: x.eq("legacy_fd")
    )
    .drop_duplicates("ticket_id", keep="first")
    .copy()
)


# ---------------------------------------------------------
# KEY NUMBERS
# ---------------------------------------------------------

total_refund_value = refunds_analysis["refund_inr"].sum()

unique_refund_tickets = refunds_analysis["ticket_id"].nunique()

total_tickets = monthly["total_tickets"].sum()

refund_rate = (
    unique_refund_tickets / total_tickets * 100
)


# ---------------------------------------------------------
# HEADER METRICS
# ---------------------------------------------------------

st.subheader("Key Refund Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Refund Value",
        f"₹{total_refund_value:,.0f}"
    )

with col2:
    st.metric(
        "Refund Tickets",
        f"{unique_refund_tickets:,}"
    )

with col3:
    st.metric(
        "Total Tickets",
        f"{total_tickets:,}"
    )

with col4:
    st.metric(
        "Overall Refund Rate",
        f"{refund_rate:.2f}%"
    )


# ---------------------------------------------------------
# MONTHLY ANALYSIS
# ---------------------------------------------------------

st.divider()

st.subheader("Monthly Refund Trend")

st.line_chart(
    monthly.set_index("month")["refund_value"]
)


st.subheader("Monthly Refund Rate")

st.line_chart(
    monthly.set_index("month")["refund_rate_pct"]
)


# ---------------------------------------------------------
# MONTHLY TABLE
# ---------------------------------------------------------

st.subheader("Monthly Refund Summary")

monthly_display = monthly.copy()

monthly_display["refund_value"] = (
    monthly_display["refund_value"]
    .map(lambda x: f"₹{x:,.0f}")
)

monthly_display["refund_rate_pct"] = (
    monthly_display["refund_rate_pct"]
    .map(lambda x: f"{x:.2f}%")
)

st.dataframe(
    monthly_display,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# REFUND REASON ANALYSIS
# ---------------------------------------------------------

st.divider()

st.subheader("Refunds by Reason")

reason_chart = reason.set_index(
    "refund_reason_code"
)["refund_tickets"]

st.bar_chart(reason_chart)


st.subheader("Refund Value by Reason")

reason_value_chart = reason.set_index(
    "refund_reason_code"
)["total_refund_value"]

st.bar_chart(reason_value_chart)


# ---------------------------------------------------------
# REASON TABLE
# ---------------------------------------------------------

reason_display = reason.copy()

reason_display["total_refund_value"] = (
    reason_display["total_refund_value"]
    .map(lambda x: f"₹{x:,.0f}")
)

reason_display["refund_share_pct"] = (
    reason_display["refund_share_pct"]
    .map(lambda x: f"{x:.2f}%")
)

st.dataframe(
    reason_display,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# AGENT ANALYSIS
# ---------------------------------------------------------

st.divider()

st.subheader("Agent Refund Analysis")

st.write(
    "Agent results are shown with team context. "
    "Returns Desk handles a large share of refunds by design, "
    "so raw refund volume should not be treated as misconduct."
)


# ---------------------------------------------------------
# TEAM FILTER
# ---------------------------------------------------------

teams = sorted(
    agents["team"].dropna().unique().tolist()
)

selected_team = st.selectbox(
    "Filter by Team",
    ["All Teams"] + teams
)


if selected_team == "All Teams":

    filtered_agents = agents.copy()

else:

    filtered_agents = agents[
        agents["team"] == selected_team
    ].copy()


# ---------------------------------------------------------
# AGENT TABLE
# ---------------------------------------------------------

agent_display = filtered_agents[
    [
        "agent_id",
        "name",
        "team",
        "tier",
        "total_tickets",
        "refund_tickets",
        "total_refund_value",
        "refund_rate_pct"
    ]
].copy()


agent_display["total_refund_value"] = (
    agent_display["total_refund_value"]
    .map(lambda x: f"₹{x:,.0f}")
)

agent_display["refund_rate_pct"] = (
    agent_display["refund_rate_pct"]
    .map(lambda x: f"{x:.2f}%")
)


st.dataframe(
    agent_display,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# POLICY REVIEW
# ---------------------------------------------------------

st.divider()

st.subheader("Policy Review Cases")

refund_with_replacement = refunds_analysis[
    refunds_analysis["replacement_issued"] == "Y"
]

gw_over_500 = refunds_analysis[
    (refunds_analysis["refund_reason_code"] == "GW-OTHER")
    &
    (refunds_analysis["refund_inr"] > 500)
]


col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Refund + Replacement Cases",
        f"{len(refund_with_replacement):,}"
    )

with col2:

    st.metric(
        "GW-OTHER Above ₹500",
        f"{len(gw_over_500):,}"
    )


st.write(
    "These are review cases based on the available policy fields. "
    "They are not automatically confirmed policy violations."
)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Vireo Refund Analysis | Data processed with Python and Pandas | "
    "Dashboard built with Streamlit"
)