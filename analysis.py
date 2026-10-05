
import pandas as pd
import glob



# 1. LOAD TICKETS DATA

tickets_file = glob.glob("data/*tickets.csv")[0]

tickets = pd.read_csv(tickets_file)

print("Tickets loaded successfully")
print("Number of tickets:", len(tickets))
print("Number of columns:", len(tickets.columns))


# 2. CONVERT DATES


tickets["created_at"] = pd.to_datetime(
    tickets["created_at"],
    errors="coerce"
)

tickets["resolved_at"] = pd.to_datetime(
    tickets["resolved_at"],
    errors="coerce"
)

tickets["month"] = tickets["created_at"].dt.to_period("M").astype(str)

print("\nDate conversion completed")
print("First ticket date:", tickets["created_at"].min())
print("Last ticket date:", tickets["created_at"].max())


# 3. CHECK REFUND DATA

refunds = tickets[
    tickets["refund_amount_inr"].notna()
].copy()

print("\nRefund tickets:", len(refunds))


# 4. CORRECT LEGACY REFUND Amounts

# Start with the original refund amount
tickets["refund_inr"] = tickets["refund_amount_inr"]

# Legacy Freshdesk values are stored in a 100x native unit
legacy_mask = tickets["source_system"] == "legacy_fd"

tickets.loc[legacy_mask, "refund_inr"] = (
    tickets.loc[legacy_mask, "refund_amount_inr"] / 100
)

# Create the refund-only dataset after correcting the amounts
refunds = tickets[
    tickets["refund_amount_inr"].notna()
].copy()

print("\nRefund amount conversion completed")

print(
    "Legacy refunds converted:",
    (refunds["source_system"] == "legacy_fd").sum()
)

print(
    "Current helpdesk refunds:",
    (refunds["source_system"] == "helpdesk").sum()
)


# 5. BASIC REFUND SUMMARY


print("\n" + "=" * 70)
print("REFUND SUMMARY")
print("=" * 70)

print(
    "Total refund tickets:",
    len(refunds)
)

print(
    "Total refund value: ₹",
    round(refunds["refund_inr"].sum(), 2)
)

print(
    "Average refund: ₹",
    round(refunds["refund_inr"].mean(), 2)
)

print(
    "Median refund: ₹",
    round(refunds["refund_inr"].median(), 2)
)


# 6. MONTHLY REFUND ANALYSIS

monthly = tickets.groupby("month").agg(
    total_tickets=("ticket_id", "count"),
    refund_tickets=(
        "refund_amount_inr",
        lambda x: x.notna().sum()
    ),
    refund_value=(
        "refund_inr",
        "sum"
    )
).reset_index()

monthly["refund_rate_pct"] = (
    monthly["refund_tickets"]
    / monthly["total_tickets"]
    * 100
)

print("\n" + "=" * 70)
print("MONTHLY REFUND ANALYSIS")
print("=" * 70)

print(
    monthly.to_string(index=False)
)

# 7. REFUND ANALYSIS BY REASON

reason_summary = refunds.groupby("refund_reason_code").agg(
    refund_tickets=("ticket_id", "count"),
    total_refund_value=("refund_inr", "sum"),
    average_refund=("refund_inr", "mean"),
    median_refund=("refund_inr", "median")
).reset_index()

# Calculate percentage of all refund tickets
reason_summary["refund_share_pct"] = (
    reason_summary["refund_tickets"]
    / len(refunds)
    * 100
)

# Sort by number of refund tickets
reason_summary = reason_summary.sort_values(
    "refund_tickets",
    ascending=False
)

print("\n" + "=" * 70)
print("REFUND ANALYSIS BY REASON")
print("=" * 70)

print(
    reason_summary.to_string(
        index=False,
        formatters={
            "total_refund_value": "{:,.2f}".format,
            "average_refund": "{:,.2f}".format,
            "median_refund": "{:,.2f}".format,
            "refund_share_pct": "{:.2f}%".format
        }
    )
)


# 8. AGENT REFUND ANALYSIS

agents_file = glob.glob("data/*agents.csv")[0]
agents = pd.read_csv(agents_file)

# Convert roster dates
agents["from_date"] = pd.to_datetime(
    agents["from_date"],
    errors="coerce"
)

agents["to_date"] = pd.to_datetime(
    agents["to_date"],
    errors="coerce"
)

# Create a simple agent lookup
agent_lookup = agents[
    ["agent_id", "name", "site", "team", "shift", "tier"]
].drop_duplicates("agent_id")

# Add agent information to tickets
tickets_with_agents = tickets.merge(
    agent_lookup,
    on="agent_id",
    how="left"
)

# Calculate agent-level totals
agent_summary = tickets_with_agents.groupby(
    ["agent_id", "name", "site", "team", "tier"]
).agg(
    total_tickets=("ticket_id", "count"),
    refund_tickets=(
        "refund_amount_inr",
        lambda x: x.notna().sum()
    ),
    total_refund_value=(
        "refund_inr",
        "sum"
    ),
    average_refund=(
        "refund_inr",
        "mean"
    )
).reset_index()

# Calculate refund rate
agent_summary["refund_rate_pct"] = (
    agent_summary["refund_tickets"]
    / agent_summary["total_tickets"]
    * 100
)

# Sort by refund ticket count
agent_summary = agent_summary.sort_values(
    "refund_tickets",
    ascending=False
)

print("\n" + "=" * 70)
print("AGENT REFUND ANALYSIS")
print("=" * 70)

print(
    agent_summary.to_string(
        index=False,
        formatters={
            "total_refund_value": "{:,.2f}".format,
            "average_refund": "{:,.2f}".format,
            "refund_rate_pct": "{:.2f}%".format
        }
    )
)


# 9. REFUNDS BY AGENT

agent_refunds = refunds.merge(
    agents[["agent_id", "name", "team", "tier"]],
    on="agent_id",
    how="left"
)

agent_summary = agent_refunds.groupby(
    ["agent_id", "name", "team", "tier"]
).agg(
    refund_tickets=("ticket_id", "count"),
    refund_value=("refund_inr", "sum")
).reset_index()

agent_summary = agent_summary.sort_values(
    "refund_tickets",
    ascending=False
)

print("\n" + "=" * 70)
print("REFUNDS BY AGENT")
print("=" * 70)

print(agent_summary.to_string(index=False))


# 10. SIMPLE POLICY CHECKS

print("\n" + "=" * 70)
print("POLICY CHECKS")
print("=" * 70)

# Check 1: Refund and replacement together
refund_with_replacement = refunds[
    refunds["replacement_issued"] == "Y"
]

print(
    "Refunds with replacement also issued:",
    len(refund_with_replacement)
)

# Check 2: GW-OTHER refunds above ₹500
gw_over_500 = refunds[
    (refunds["refund_reason_code"] == "GW-OTHER") &
    (refunds["refund_inr"] > 500)
]

print(
    "GW-OTHER refunds above ₹500 requiring review:",
    len(gw_over_500)
)

print(
    "Value of these GW-OTHER refunds: ₹",
    round(gw_over_500["refund_inr"].sum(), 2)

)


# 11. VIEW SAMPLE REFUND MESSAGES

sample_refunds = refunds[
    [
        "ticket_id",
        "refund_reason_code",
        "refund_inr",
        "customer_message",
        "agent_notes"
    ]
].head(10)

print("\n" + "=" * 70)
print("SAMPLE REFUND MESSAGES")
print("=" * 70)

print(sample_refunds.to_string(index=False))