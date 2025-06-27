import streamlit as st
import json
import networkx as nx

# Load ontology schema from JSON file
ontology_file = "rule_ontology.json"
def load_ontology():
    try:
        with open(ontology_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

ontology_schema = load_ontology()
classes = ontology_schema.get("classes", [])

# # Ontology Schema
# # The ontology graph models the relationships between classes and their attributes.
# ontology = nx.DiGraph()
# for class_entry in classes:
#     cls = class_entry.get("name")
#     attributes = class_entry.get("data_properties", [])
#     ontology.add_node(cls, type="class")
#     for attr in attributes:
#         ontology.add_node(f"{cls}.{attr}", type="attribute")
#         ontology.add_edge(cls, f"{cls}.{attr}", relation="has_attribute")

# # Function to get ontology schema lookup
# # Retrieves all attributes defined in the ontology schema for use in UI dropdowns.
# def get_ontology_attributes():
#     attributes = []
#     for class_entry in classes:
#         cls = class_entry.get("name")
#         for attr in class_entry.get("data_properties", []):
#             attributes.append(f"{cls}.{attr}")
#     return attributes

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
classes_list = [class_entry.get("name") for class_entry in classes]  # List of classes

for i in range(num_conditions):
    st.write(f"Condition {i+1}")
    condition_type = st.selectbox(f"Condition Type for Condition {i+1}", ["AND", "OR"], key=f"condition_type_{i}")
    selected_class = st.selectbox(f"Class for Condition {i+1}", classes_list, key=f"cond_class_{i}")
    available_attributes = next((class_entry.get("data_properties", []) for class_entry in classes if class_entry.get("name") == selected_class), [])
    attribute = st.selectbox(f"Attribute for Condition {i+1}", available_attributes, key=f"cond_attr_{i}")
    operator = st.selectbox(
        f"Operator for Condition {i+1}",
        ["equals", "not_equals", "greater_than", "less_than", "in", "not_in", "between", "compare"],
        key=f"cond_op_{i}"
    )

    rule_compare = st.selectbox(f"Rule Compare Type for Condition {i+1}", ["simple", "complex"], key=f"rule_compare_{i}")

    if rule_compare == "complex":
        compare_class = st.selectbox(f"Compare Class for Condition {i+1}", classes_list, key=f"compare_class_{i}")
        compare_attributes = next((class_entry.get("data_properties", []) for class_entry in classes if class_entry.get("name") == compare_class), [])
        compare_attribute = st.selectbox(f"Compare Attribute for Condition {i+1}", compare_attributes, key=f"compare_attr_{i}")
        conditions.append({
            "type": condition_type,
            "class": selected_class,
            "attribute": attribute,
            "operator": operator,
            "rule_compare": rule_compare,
            "compare_class": compare_class,
            "compare_attribute": compare_attribute
        })
    else:
        value = st.text_input(f"Value for Condition {i+1}", key=f"cond_val_{i}")
        conditions.append({
            "type": condition_type,
            "class": selected_class,
            "attribute": attribute,
            "operator": operator,
            "rule_compare": rule_compare,
            "value": value
        })

# Actions
st.subheader("Define Actions") # This section defines the actions triggered when the rule conditions are met.
actions = []
num_actions = st.number_input("Number of Actions", min_value=1, max_value=10, step=1, value=1)

action_types = ["Perform Operation", "Return True", "Return False"]

for i in range(num_actions):
    st.write(f"Action {i+1}")
    action_type = st.selectbox(f"Action Type for Action {i+1}", action_types, key=f"act_type_{i}")

    if action_type == "Perform Operation":
        selected_class = st.selectbox(f"Class for Action {i+1}", classes_list, key=f"act_class_{i}")
        available_attributes = next((class_entry.get("data_properties", []) for class_entry in classes if class_entry.get("name") == selected_class), [])
        attribute = st.selectbox(f"Attribute for Action {i+1}", available_attributes, key=f"act_attr_{i}")
        operation = st.selectbox(
            f"Operation for Action {i+1}",
            ["add", "multiply", "constant"],
            key=f"act_op_{i}"
        )
        value = st.text_input(f"Value for Action {i+1}", key=f"act_val_{i}")
        actions.append({"type": "operation", "class": selected_class, "attribute": attribute, "operation": operation, "value": float(value) if value.replace('.', '', 1).isdigit() and operation != "constant" else value})

    elif action_type == "Return True":
        actions.append({"type": "return", "value": True})

    elif action_type == "Return False":
        actions.append({"type": "return", "value": False})

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


# import streamlit as st
# import json
# import networkx as nx

# # Load ontology schema from JSON file
# ontology_file = "rule_ontology.json"
# def load_ontology():
#     try:
#         with open(ontology_file, "r") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return {}

# ontology_schema = load_ontology()
# classes = ontology_schema.get("classes", [])

# # Ontology Schema
# # The ontology graph models the relationships between classes and their attributes.
# ontology = nx.DiGraph()
# for class_entry in classes:
#     cls = class_entry.get("name")
#     attributes = class_entry.get("data_properties", [])
#     ontology.add_node(cls, type="class")
#     for attr in attributes:
#         ontology.add_node(f"{cls}.{attr}", type="attribute")
#         ontology.add_edge(cls, f"{cls}.{attr}", relation="has_attribute")

# # Function to get ontology schema lookup
# # Retrieves all attributes defined in the ontology schema for use in UI dropdowns.
# def get_ontology_attributes():
#     attributes = []
#     for class_entry in classes:
#         cls = class_entry.get("name")
#         for attr in class_entry.get("data_properties", []):
#             attributes.append(f"{cls}.{attr}")
#     return attributes

# # Streamlit UI
# st.title("Rule Authoring Tool")

# # Rule Details
# st.header("Create a New Rule")
# rule_id = st.text_input("Rule ID", "")
# rule_description = st.text_area("Rule Description", "")

# # Conditions
# st.subheader("Define Conditions")
# conditions = []
# num_conditions = st.number_input("Number of Conditions", min_value=1, max_value=10, step=1, value=1)
# classes_list = [class_entry.get("name") for class_entry in classes]  # List of classes

# for i in range(num_conditions):
#     st.write(f"Condition {i+1}")
#     condition_type = st.selectbox(f"Condition Type for Condition {i+1}", ["AND", "OR"], key=f"condition_type_{i}")
#     selected_class = st.selectbox(f"Class for Condition {i+1}", classes_list, key=f"cond_class_{i}")
#     available_attributes = next((class_entry.get("data_properties", []) for class_entry in classes if class_entry.get("name") == selected_class), [])
#     attribute = st.selectbox(f"Attribute for Condition {i+1}", available_attributes, key=f"cond_attr_{i}")
#     operator = st.selectbox(
#         f"Operator for Condition {i+1}",
#         ["equals", "not_equals", "greater_than", "less_than", "in", "not_in", "between", "compare"],
#         key=f"cond_op_{i}"
#     )

#     rule_compare = st.selectbox(f"Rule Compare Type for Condition {i+1}", ["simple", "complex"], key=f"rule_compare_{i}")

#     if rule_compare == "complex":
#         compare_class = st.selectbox(f"Compare Class for Condition {i+1}", classes_list, key=f"compare_class_{i}")
#         compare_attributes = next((class_entry.get("data_properties", []) for class_entry in classes if class_entry.get("name") == compare_class), [])
#         compare_attribute = st.selectbox(f"Compare Attribute for Condition {i+1}", compare_attributes, key=f"compare_attr_{i}")
#         conditions.append({
#             "type": condition_type,
#             "class": selected_class,
#             "attribute": attribute,
#             "operator": operator,
#             "rule_compare": rule_compare,
#             "compare_class": compare_class,
#             "compare_attribute": compare_attribute
#         })
#     else:
#         value = st.text_input(f"Value for Condition {i+1}", key=f"cond_val_{i}")
#         conditions.append({
#             "type": condition_type,
#             "class": selected_class,
#             "attribute": attribute,
#             "operator": operator,
#             "rule_compare": rule_compare,
#             "value": value
#         })

# # Actions
# st.subheader("Define Actions") # This section defines the actions triggered when the rule conditions are met.
# actions = []
# num_actions = st.number_input("Number of Actions", min_value=1, max_value=10, step=1, value=1)

# action_types = ["Perform Operation", "Return True", "Return False"]

# for i in range(num_actions):
#     st.write(f"Action {i+1}")
#     action_type = st.selectbox(f"Action Type for Action {i+1}", action_types, key=f"act_type_{i}")

#     if action_type == "Perform Operation":
#         attribute = st.selectbox(f"Attribute for Action {i+1}", get_ontology_attributes(), key=f"act_attr_{i}")
#         operation = st.selectbox(
#             f"Operation for Action {i+1}",
#             ["add", "multiply", "constant"],
#             key=f"act_op_{i}"
#         )
#         value = st.text_input(f"Value for Action {i+1}", key=f"act_val_{i}")
#         actions.append({"type": "operation", "attribute": attribute, "operation": operation, "value": float(value) if value.replace('.', '', 1).isdigit() and operation != "constant" else value})

#     elif action_type == "Return True":
#         actions.append({"type": "return", "value": True})

#     elif action_type == "Return False":
#         actions.append({"type": "return", "value": False})

# # Submit Rule
# if st.button("Save Rule"):
#     rule = {
#         "rule_id": rule_id,
#         "description": rule_description,
#         "conditions": conditions,
#         "actions": actions
#     }

#     # Append rule to JSON file
#     try:
#         with open("rules.json", "r") as f:
#             existing_rules = json.load(f)
#             if isinstance(existing_rules, dict):
#                 existing_rules = [existing_rules]
#     except FileNotFoundError:
#         existing_rules = []

#     existing_rules.append(rule)

#     with open("rules.json", "w") as f:
#         json.dump(existing_rules, f, indent=4)

#     st.success("Rule saved successfully!")
#     st.json(rule)

# # View Existing Rules
# st.header("View Existing Rules")
# if st.button("Load Rules"):
#     try:
#         with open("rules.json", "r") as f:
#             existing_rules = json.load(f)
#         st.json(existing_rules)
#     except FileNotFoundError:
#         st.error("No rules found. Create a new rule first.")

# # import streamlit as st
# # import json
# # import networkx as nx

# # # Load ontology schema from JSON file
# # ontology_file = "rule_ontology.json"
# # def load_ontology():
# #     try:
# #         with open(ontology_file, "r") as f:
# #             return json.load(f)
# #     except FileNotFoundError:
# #         return {}

# # ontology_schema = load_ontology()
# # classes = ontology_schema.get("classes", [])

# # # Ontology Schema
# # # The ontology graph models the relationships between classes and their attributes.
# # ontology = nx.DiGraph()
# # for class_entry in classes:
# #     cls = class_entry.get("name")
# #     attributes = class_entry.get("data_properties", [])
# #     ontology.add_node(cls, type="class")
# #     for attr in attributes:
# #         ontology.add_node(f"{cls}.{attr}", type="attribute")
# #         ontology.add_edge(cls, f"{cls}.{attr}", relation="has_attribute")

# # # Function to get ontology schema lookup
# # # Retrieves all attributes defined in the ontology schema for use in UI dropdowns.
# # def get_ontology_attributes():
# #     attributes = []
# #     for class_entry in classes:
# #         cls = class_entry.get("name")
# #         for attr in class_entry.get("data_properties", []):
# #             attributes.append(f"{cls}.{attr}")
# #     return attributes

# # # Streamlit UI
# # st.title("Rule Authoring Tool")

# # # Rule Details
# # st.header("Create a New Rule")
# # rule_id = st.text_input("Rule ID", "")
# # rule_description = st.text_area("Rule Description", "")

# # # Conditions
# # st.subheader("Define Conditions")
# # conditions = []
# # num_conditions = st.number_input("Number of Conditions", min_value=1, max_value=10, step=1, value=1)
# # classes_list = [class_entry.get("name") for class_entry in classes]  # List of classes

# # for i in range(num_conditions):
# #     st.write(f"Condition {i+1}")
# #     condition_type = st.selectbox(f"Condition Type for Condition {i+1}", ["AND", "OR"], key=f"condition_type_{i}")
# #     selected_class = st.selectbox(f"Class for Condition {i+1}", classes_list, key=f"cond_class_{i}")
# #     available_attributes = next((class_entry.get("data_properties", []) for class_entry in classes if class_entry.get("name") == selected_class), [])
# #     attribute = st.selectbox(f"Attribute for Condition {i+1}", available_attributes, key=f"cond_attr_{i}")
# #     operator = st.selectbox(
# #         f"Operator for Condition {i+1}",
# #         ["equals", "not_equals", "greater_than", "less_than", "in", "not_in", "between", "compare"],
# #         key=f"cond_op_{i}"
# #     )

# #     rule_compare = st.selectbox(f"Rule Compare Type for Condition {i+1}", ["simple", "complex"], key=f"rule_compare_{i}")

# #     if rule_compare == "complex":
# #         compare_class = st.selectbox(f"Compare Class for Condition {i+1}", classes_list, key=f"compare_class_{i}")
# #         compare_attributes = next((class_entry.get("data_properties", []) for class_entry in classes if class_entry.get("name") == compare_class), [])
# #         compare_attribute = st.selectbox(f"Compare Attribute for Condition {i+1}", compare_attributes, key=f"compare_attr_{i}")
# #         conditions.append({
# #             "type": condition_type,
# #             "class": selected_class,
# #             "attribute": attribute,
# #             "operator": operator,
# #             "rule_compare": rule_compare,
# #             "compare_class": compare_class,
# #             "compare_attribute": compare_attribute
# #         })
# #     else:
# #         value = st.text_input(f"Value for Condition {i+1}", key=f"cond_val_{i}")
# #         conditions.append({
# #             "type": condition_type,
# #             "class": selected_class,
# #             "attribute": attribute,
# #             "operator": operator,
# #             "rule_compare": rule_compare,
# #             "value": value
# #         })

# # # Actions
# # st.subheader("Define Actions") # This section defines the actions triggered when the rule conditions are met.
# # actions = []
# # num_actions = st.number_input("Number of Actions", min_value=1, max_value=10, step=1, value=1)

# # action_types = ["Perform Operation", "Return True", "Return False", "Return Constant"]

# # for i in range(num_actions):
# #     st.write(f"Action {i+1}")
# #     action_type = st.selectbox(f"Action Type for Action {i+1}", action_types, key=f"act_type_{i}")

# #     if action_type == "Perform Operation":
# #         attribute = st.selectbox(f"Attribute for Action {i+1}", get_ontology_attributes(), key=f"act_attr_{i}")
# #         operation = st.selectbox(
# #             f"Operation for Action {i+1}",
# #             ["add", "multiply"],
# #             key=f"act_op_{i}"
# #         )
# #         value = st.text_input(f"Value for Action {i+1}", key=f"act_val_{i}")
# #         actions.append({"type": "operation", "attribute": attribute, "operation": operation, "value": float(value) if value.isdigit() else value})

# #     elif action_type == "Return True":
# #         actions.append({"type": "return", "value": True})

# #     elif action_type == "Return False":
# #         actions.append({"type": "return", "value": False})

# #     elif action_type == "Return Constant":
# #         constant_value = st.text_input(f"Constant Value for Action {i+1}", key=f"constant_val_{i}")
# #         actions.append({"type": "return", "value": constant_value})

# # # Submit Rule
# # if st.button("Save Rule"):
# #     rule = {
# #         "rule_id": rule_id,
# #         "description": rule_description,
# #         "conditions": conditions,
# #         "actions": actions
# #     }

# #     # Append rule to JSON file
# #     try:
# #         with open("rules.json", "r") as f:
# #             existing_rules = json.load(f)
# #             if isinstance(existing_rules, dict):
# #                 existing_rules = [existing_rules]
# #     except FileNotFoundError:
# #         existing_rules = []

# #     existing_rules.append(rule)

# #     with open("rules.json", "w") as f:
# #         json.dump(existing_rules, f, indent=4)

# #     st.success("Rule saved successfully!")
# #     st.json(rule)

# # # View Existing Rules
# # st.header("View Existing Rules")
# # if st.button("Load Rules"):
# #     try:
# #         with open("rules.json", "r") as f:
# #             existing_rules = json.load(f)
# #         st.json(existing_rules)
# #     except FileNotFoundError:
# #         st.error("No rules found. Create a new rule first.")
