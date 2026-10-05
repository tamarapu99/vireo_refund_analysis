import pandas as pd
import ollama

# Load the tickets file
tickets = pd.read_csv(
    "data/9ac91960-ee62-4501-85f2-32ffe5ea9ccc-tickets.csv"
)

# Select 5 unique refund tickets
refunds = (
    tickets[tickets["refund_amount_inr"].notna()]
    .drop_duplicates("ticket_id")
    .head(5)
)

# Read our prompt
with open("prompts/prompt_v2.txt", "r") as file:
    prompt_template = file.read()

# These are the only valid refund codes
valid_codes = [
    "GW-OTHER",
    "RETURN-QC-OK",
    "DUP-PAYMENT",
    "CANCEL",
    "DOA-REPL",
    "WTY-BUYBACK",
    "PRICE-ADJ",
    "LOST-TRANSIT"
]

correct = 0
invalid = 0

print("\n5-TICKET AI TEST")
print("=" * 60)

# Test each refund ticket
for _, ticket in refunds.iterrows():

    prompt = prompt_template.replace(
        "{customer_message}",
        str(ticket["customer_message"])
    )

    prompt = prompt.replace(
        "{agent_notes}",
        str(ticket["agent_notes"])
    )

    response = ollama.chat(
        model="llama3.2:1b",
        messages=[
            {
                "role": "system",
                "content": "You are a refund classification system."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    prediction = response["message"]["content"].strip()

    # Check whether the AI returned a valid refund code
    if prediction not in valid_codes:
        prediction = "INVALID"
        invalid += 1

    # Compare AI prediction with actual code
    if prediction == ticket["refund_reason_code"]:
        result = "CORRECT"
        correct += 1
    else:
        result = "WRONG"

    print("\nTicket ID:", ticket["ticket_id"])
    print("Actual code:", ticket["refund_reason_code"])
    print("AI prediction:", prediction)
    print("Result:", result)

# Calculate accuracy
accuracy = (correct / len(refunds)) * 100

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print("Total tickets tested:", len(refunds))
print("Correct:", correct)
print("Wrong:", len(refunds) - correct - invalid)
print("Invalid AI responses:", invalid)
print("Accuracy:", round(accuracy, 2), "%")