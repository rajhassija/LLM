import streamlit as st
import json

# Load existing rules from JSON file
def load_rules():
    try:
        with open("rules.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save rule sets to a JSON file
def save_rule_sets(rule_sets):
    with open("rule_sets.json", "w") as f:
        json.dump(rule_sets, f, indent=4)

# Load existing rule sets from JSON file
def load_rule_sets():
    try:
        with open("rule_sets.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Streamlit UI for Rule Sets
st.title("Rule Set Authoring Tool")

# Create a New Rule Set
st.header("Create a New Rule Set")
rule_set_id = st.text_input("Rule Set ID", "")
rule_set_name = st.text_input("Rule Set Name", "")

rules = load_rules()
if not rules:
    st.warning("No rules found. Create individual rules first.")
else:
    rule_options = [rule.get("rule_id") for rule in rules]
    selected_rules = st.multiselect("Select Rules to Include in the Rule Set", rule_options)

    if st.button("Save Rule Set"):
        if not rule_set_id or not rule_set_name or not selected_rules:
            st.error("Please fill in all fields and select at least one rule.")
        else:
            rule_sets = load_rule_sets()
            new_rule_set = {
                "rule_set_id": rule_set_id,
                "rule_set_name": rule_set_name,
                "rules": selected_rules
            }
            rule_sets.append(new_rule_set)
            save_rule_sets(rule_sets)
            st.success("Rule Set saved successfully!")
            st.json(new_rule_set)

# View Existing Rule Sets
st.header("View Existing Rule Sets")
if st.button("Load Rule Sets"):
    rule_sets = load_rule_sets()
    if not rule_sets:
        st.warning("No rule sets found. Create a new rule set first.")
    else:
        for rule_set in rule_sets:
            st.subheader(f"Rule Set: {rule_set['rule_set_name']} ({rule_set['rule_set_id']})")
            st.write("Rules Included:", rule_set["rules"])
