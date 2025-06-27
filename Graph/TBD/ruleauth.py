import streamlit as st
import json
import networkx as nx

# Ontology Schema
# The ontology graph models the relationships between classes and their attributes.
# Classes (e.g., Product, Order, Customer) represent high-level entities, and attributes
# are connected to their respective classes using a directed graph structure.
ontology = nx.DiGraph()
classes = {
    "Product": ["id", "name", "price", "category"],
    "Order": ["id", "product_id", "quantity", "total_price"],
    "Customer": ["id", "name", "email", "loyalty_points"],
}
for cls, attributes in classes.items():
    ontology.add_node(cls, type="class")
    for attr in attributes:
        ontology.add_node(f"{cls}.{attr}", type="attribute")
        ontology.add_edge(cls, f"{cls}.{attr}", relation="has_attribute")

# Function to get ontology schema lookup
# Retrieves all attributes defined in the ontology schema for use in UI dropdowns.
def get_ontology_attributes():
    attributes = []
    for cls in classes:
        attributes.extend([f"{cls}.{attr}" for attr in classes[cls]])
    return attributes

# Streamlit UI
st.title("Rule Authoring Tool")

# Rule Details
st.header("Create a New Rule")
rule_id = st.text_input("Rule ID", "")
rule_description = st.text_area("Rule Description", "")

# Conditions
st.subheader("Define Conditions")
conditions = []
num_conditions = st.number_input("Number of Conditions", min_value=1, max_value=10, step=1, value=1)
ontology_attributes = get_ontology_attributes()

for i in range(num_conditions):
    st.write(f"Condition {i+1}")
    condition_type = st.selectbox(f"Condition Type for Condition {i+1}", ["AND", "OR"], key=f"condition_type_{i}")
    attribute = st.selectbox(f"Attribute for Condition {i+1}", ontology_attributes, key=f"cond_attr_{i}")
    operator = st.selectbox(
        f"Operator for Condition {i+1}",
        ["equals", "not_equals", "greater_than", "less_than", "in", "not_in", "between"],
        key=f"cond_op_{i}"
    )
    value = st.text_input(f"Value for Condition {i+1}", key=f"cond_val_{i}")
    conditions.append({"type": condition_type, "attribute": attribute, "operator": operator, "value": value})

# Actions
st.subheader("Define Actions") # This section defines the actions triggered when the rule conditions are met.
actions = []
num_actions = st.number_input("Number of Actions", min_value=1, max_value=10, step=1, value=1)

action_types = ["Perform Operation", "Return True", "Return False", "Return Constant"]

for i in range(num_actions):
    st.write(f"Action {i+1}")
    action_type = st.selectbox(f"Action Type for Action {i+1}", action_types, key=f"act_type_{i}")

    if action_type == "Perform Operation":
        attribute = st.selectbox(f"Attribute for Action {i+1}", ontology_attributes, key=f"act_attr_{i}")
        operation = st.selectbox(
            f"Operation for Action {i+1}",
            ["add", "multiply"],
            key=f"act_op_{i}"
        )
        value = st.text_input(f"Value for Action {i+1}", key=f"act_val_{i}")
        actions.append({"type": "operation", "attribute": attribute, "operation": operation, "value": float(value) if value.isdigit() else value})

    elif action_type == "Return True":
        actions.append({"type": "return", "value": True})

    elif action_type == "Return False":
        actions.append({"type": "return", "value": False})

    elif action_type == "Return Constant":
        constant_value = st.text_input(f"Constant Value for Action {i+1}", key=f"constant_val_{i}")
        actions.append({"type": "return", "value": constant_value})

# Submit Rule
if st.button("Save Rule"):
    rule = {
        "rule_id": rule_id,
        "description": rule_description,
        "conditions": conditions,
        "actions": actions
    }

    # Append rule to JSON file
    try:
        with open("rules.json", "r") as f:
            existing_rules = json.load(f)
            if isinstance(existing_rules, dict):
                existing_rules = [existing_rules]
    except FileNotFoundError:
        existing_rules = []

    existing_rules.append(rule)

    with open("rules.json", "w") as f:
        json.dump(existing_rules, f, indent=4)

    st.success("Rule saved successfully!")
    st.json(rule)

# View Existing Rules
st.header("View Existing Rules")
if st.button("Load Rules"):
    try:
        with open("rules.json", "r") as f:
            existing_rules = json.load(f)
        st.json(existing_rules)
    except FileNotFoundError:
        st.error("No rules found. Create a new rule first.")

