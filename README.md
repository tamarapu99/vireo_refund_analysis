# Vireo Refund Analysis

An AI-assisted refund analysis tool built to help Vireo's Finance and Customer Support teams understand refund volume, refund reasons, agent-level patterns, and data-quality issues.

The project combines **Python, Pandas, Streamlit, and a local LLM prototype**. Financial calculations and business reporting are handled deterministically with Python/Pandas, while the LLM was tested as an experimental classification assistant.

---

## 1. Business Problem

Vireo sells consumer electronics such as:

* Earbuds
* Headphones
* Smart speakers
* Watches

The Finance Controller requested a monthly refund analysis answering:

* How much money is being refunded?
* What are the main refund reasons?
* How do refunds vary by month?
* Which agents or teams are associated with refund activity?
* Are there possible policy-control issues?
* Can the helpdesk refund numbers be reconciled with the finance export?

A major concern was that the finance export appeared to show **more than ₹1 crore per quarter**, while the helpdesk report showed approximately **₹11 lakh per quarter**.

The analysis therefore needed to address data quality before producing business conclusions.

---

## 2. Project Objective

The goal was to build a small working analysis tool that:

1. Loads the supplied support and business data.
2. Identifies refund tickets.
3. Corrects legacy monetary values.
4. Detects duplicate migrated tickets.
5. Produces monthly refund summaries.
6. Breaks refunds down by reason.
7. Provides agent/team-level analysis.
8. Performs selected policy-control checks.
9. Provides a Streamlit dashboard.
10. Tests whether an LLM can reliably assist with refund classification.

---

## 3. Data Used

The project uses the supplied Vireo datasets:

* `tickets.csv`
* `agents.csv`
* `orders.csv`
* `customers.csv`
* `products.csv`
* `support-policy.pdf`
* `email-thread.txt`

The raw data is **not included in this GitHub repository** because it contains business/customer information.

The analysis code expects the data to be placed locally inside:

```text
data/
```

---

## 4. Key Data Findings

The ticket dataset contains:

* **12,238 tickets**
* Date range: **January 1, 2025 – June 30, 2026**
* Timestamp standard: **IST**
* Source systems:

  * Helpdesk
  * Legacy Freshdesk

There were:

* **2,465 raw refund records**
* **2,340 unique refund tickets** after duplicate migration handling

### Legacy amount issue

During validation, legacy Freshdesk refund amounts were found to be stored at **100× the actual INR value**.

For example:

```text
Raw legacy value:       212400
Corrected INR value:      2124
```

Therefore:

```text
legacy_fd refund amount ÷ 100 = INR value
```

Current helpdesk values were already stored in INR.

---

## 5. Duplicate Migration Records

The email thread and data investigation indicated that some historical Freshdesk tickets had been re-imported into the current helpdesk.

The analysis found:

* **125 duplicate ticket IDs**
* Each duplicate appeared once under `helpdesk` and once under `legacy_fd`
* The duplicate pairs had matching refund reason and corrected refund value
* Duplicate corrected refund value: approximately **₹7.22 lakh**

For the business analysis, the helpdesk record was retained when the same ticket existed in both systems.

The original records remain available in the local cleaned output for auditability.

---

## 6. Final Refund Results

After monetary correction and duplicate handling:

| Metric                |      Result |
| --------------------- | ----------: |
| Total support tickets |      12,238 |
| Unique refund tickets |       2,340 |
| Total refund value    | ₹67.10 lakh |
| Average refund        |      ₹2,867 |
| Median refund         |      ₹2,499 |
| Overall refund rate   |      19.12% |

### Main refund reasons

| Reason       | Refund Tickets | Refund Value |
| ------------ | -------------: | -----------: |
| GW-OTHER     |            991 |  ₹29.07 lakh |
| RETURN-QC-OK |            452 |  ₹11.81 lakh |
| DUP-PAYMENT  |            321 |   ₹8.85 lakh |
| CANCEL       |            222 |   ₹6.13 lakh |
| DOA-REPL     |            147 |   ₹4.71 lakh |
| WTY-BUYBACK  |             89 |   ₹2.89 lakh |
| PRICE-ADJ    |             71 |   ₹2.07 lakh |
| LOST-TRANSIT |             47 |   ₹1.57 lakh |

The largest category was **GW-OTHER**, accounting for approximately **42% of unique refund tickets**.

---

## 7. Policy-Control Checks

Two checks were included as review populations rather than confirmed violations.

### Refund + replacement

The analysis identified:

* **166 tickets** where both a refund and replacement were recorded.

The policy states that a customer should not receive both a refund and replacement for the same order.

These records should therefore be reviewed rather than automatically treated as confirmed policy violations.

### Goodwill refunds above ₹500

The analysis identified:

* **879 GW-OTHER refunds above ₹500**
* Approximately **₹28.72 lakh** in refund value

The policy states that goodwill credits are capped at ₹500 per ticket and require Team Lead approval.

These records should therefore be reviewed for approval evidence and correct reason coding.

---

## 8. Agent Analysis

Agent-level analysis uses the agent assignment period rather than simply joining on `agent_id`.

This is important because the supplied agent roster can contain multiple assignment records for an agent.

The matching process considers:

* Agent ID
* Assignment dates
* Ticket resolution/assignment date
* Team
* Tier

This avoids incorrectly multiplying ticket or refund counts when an agent has multiple roster records.

The analysis also considers team context because different teams have different responsibilities.

For example, the Returns Desk is expected to process a large share of refunds by design, so comparing raw refund totals between all teams would be misleading.

---

## 9. AI / LLM Experiment

An LLM was tested as an experimental refund-reason classification assistant.

The model was given:

* Customer message
* Agent notes
* Allowed refund reason codes

The classifier was instructed to return exactly one of:

```text
GW-OTHER
RETURN-QC-OK
DUP-PAYMENT
CANCEL
DOA-REPL
WTY-BUYBACK
PRICE-ADJ
LOST-TRANSIT
```

Two prompt versions were developed and saved under:

```text
prompts/
```

The project also includes the AI testing script:

```text
tests/test_ai.py
```

### AI result

The local LLM prototype did not achieve reliable structured classification during testing.

Because the experiment was not sufficiently reliable, **LLM output was not used to calculate the final financial results**.

This was an intentional design decision.

The final refund amounts, rates, monthly totals, and policy checks are calculated using deterministic Python/Pandas logic so that the financial numbers remain reproducible and auditable.

---

## 10. Dashboard

A Streamlit dashboard was created to make the analysis easier to review.

The dashboard provides:

* Total refund value
* Unique refund tickets
* Total support tickets
* Overall refund rate
* Monthly refund trends
* Refund reason breakdown
* Team filtering
* Agent-level summary
* Policy review indicators

The dashboard is intended as a lightweight finance/support review tool rather than a full production application.

---

## 11. Project Structure

```text
vireo_refund_analysis/
│
├── app.py
├── analysis.py
├── .gitignore
│
├── outputs/
│   ├── agent_summary.csv
│   ├── monthly_refunds.csv
│   └── reason_summary.csv
│
├── prompts/
│   ├── prompt_v1.txt
│   └── prompt_v2.txt
│
└── tests/
    └── test_ai.py
```

The raw `data/` directory and environment files are intentionally excluded from GitHub.

---

## 12. Technologies Used

* Python
* Pandas
* NumPy
* Streamlit
* Python-dotenv
* PyPDF
* OpenAI API prototype
* Ollama / local LLM prototype
* Git & GitHub

---

## 13. Setup

### 1. Clone the repository

```bash
git clone https://github.com/tamarapu99/vireo_refund_analysis.git
cd vireo_refund_analysis
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the environment

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

If a `requirements.txt` file is provided:

```bash
pip install -r requirements.txt
```

Otherwise, install the required packages:

```bash
pip install pandas numpy streamlit python-dotenv pypdf openai ollama
```

### 5. Add the supplied data

Place the assignment data inside:

```text
data/
```

The raw data should remain local and should not be committed to GitHub.

---

## 14. Run the Analysis

Run:

```bash
python analysis.py
```

The analysis generates summary files inside:

```text
outputs/
```

---

## 15. Run the Dashboard

Start Streamlit with:

```bash
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

## 16. Reproducibility and Validation

The analysis includes validation checks for:

* Ticket counts
* Refund counts
* Refund amounts
* Legacy monetary conversion
* Duplicate ticket IDs
* Agent assignment matching
* Monthly totals
* Refund reason totals
* Policy review populations

The final business analysis is based on **2,340 unique refund tickets** and a corrected refund value of approximately **₹67.10 lakh**.

---

## 17. Business Recommendations

Based on the analysis, the immediate areas for review are:

### 1. Review high-value goodwill refunds

The `GW-OTHER` category represents the largest refund category.

Reviewing high-value goodwill refunds can help determine whether:

* The correct reason code was used
* Team Lead approval was obtained
* The refund was consistent with policy

### 2. Review refund + replacement cases

The 166 identified records should be checked against order history and policy rather than automatically classified as violations.

### 3. Improve refund reason coding

The large `GW-OTHER` category reduces visibility into why money is being refunded.

More consistent reason coding would improve Finance reporting.

### 4. Monitor monthly refund trends

Refund rates increased during parts of the analysis period.

This should be interpreted alongside the documented frontline policy change and the reported **0.4 CSAT increase**, rather than automatically treating higher refunds as agent misconduct.

---

## 18. Limitations

This project is an assignment-focused analytical prototype.

Important limitations include:

* Raw customer/support data is not included in the repository.
* The LLM classifier was experimental and was not reliable enough to drive financial calculations.
* Policy-control checks identify records for review; they do not prove violations.
* Agent comparisons should consider team/tier responsibilities.
* The dashboard is designed for analysis and review, not production deployment.

---

## 19. Conclusion

The project reconciles the major data-quality issues in the supplied refund records and produces a reproducible refund analysis.

The final business view is:

> **2,340 unique refund tickets generated approximately ₹67.10 lakh in refunds, with GW-OTHER representing the largest refund category at approximately ₹29.07 lakh.**

The analysis focuses on making the refund numbers understandable, traceable, and useful for Finance and Support teams while keeping AI experimentation separate from the financial calculations.
