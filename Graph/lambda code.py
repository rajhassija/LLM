import json

def evaluate_conditions(conditions, data):
    """
    Evaluate all conditions based on their type (AND/OR) and the provided data.
    :param conditions: List of condition dictionaries with type (AND/OR), attribute, operator, and value or comparison.
    :param data: Dictionary representing the data object that includes classes and their attributes.
    :return: True if conditions are met, else False.
    """
    # Separate conditions by type: AND and OR
    and_conditions = [
        cond for cond in conditions if cond.get("type") == "AND"
    ]
    or_conditions = [
        cond for cond in conditions if cond.get("type") == "OR"
    ]

    # Evaluate AND conditions (all must be true)
    for condition in and_conditions:
        if not evaluate_single_condition(condition, data):
            return False

    # Evaluate OR conditions (at least one must be true)
    if or_conditions:
        if not any(evaluate_single_condition(cond, data) for cond in or_conditions):
            return False

    return True

def evaluate_single_condition(condition, data):
    """
    Evaluate a single condition against the provided data.
    :param condition: A dictionary with attributes such as attribute, operator, and value or comparison.
    :param data: Dictionary representing the data object.
    :return: True if the condition is met, else False.
    """
    # Extract relevant fields from the condition
    attribute = condition.get("attribute")
    operator = condition.get("operator")
    rule_compare = condition.get("rule_compare")

    # Handle "complex" rule comparison by resolving nested attributes
    if rule_compare == "complex":
        compare_class = condition.get("compare_class")
        compare_attribute = condition.get("compare_attribute")
        compare_value = resolve_nested_attribute(data, compare_class, compare_attribute)
        if compare_value is None:
            return False
        value = compare_value
    else:
        value = condition.get("value")

    # Resolve the current attribute's value from the data
    current_value = resolve_nested_attribute(data, condition.get("class"), attribute)

    if current_value is None:
        return False

    # Perform condition evaluation based on the operator
    if operator == "equals":
        return current_value == value
    elif operator == "not_equals":
        return current_value != value
    elif operator == "greater_than":
        return current_value > value
    elif operator == "less_than":
        return current_value < value
    elif operator == "in":
        return current_value in value
    elif operator == "not_in":
        return current_value not in value
    elif operator == "between":
        return value[0] <= current_value <= value[1]
    else:
        return False

def resolve_nested_attribute(data, class_name, attribute):
    """
    Resolve nested attributes for a given class and attribute from the data object.
    :param data: Dictionary representing the data object.
    :param class_name: The name of the class containing the attribute.
    :param attribute: The attribute name within the class.
    :return: The resolved value of the attribute, or None if not found.
    """
    current_value = data.get(class_name, {})
    return current_value.get(attribute, None)

def apply_actions(actions, data):
    """
    Apply a set of actions to the data object based on the rules.
    :param actions: List of action dictionaries with type, attribute, operation, and value.
    :param data: Dictionary representing the data object.
    :return: Modified data object or specific return values.
    """
    for action in actions:
        action_type = action["type"]

        if action_type == "operation":
            class_name = action["class"]
            attribute = action["attribute"]
            operation = action["operation"]
            value = action["value"]

            # Resolve nested attributes (e.g., "Product.price")
            if class_name in data and attribute in data[class_name]:
                if operation == "add":
                    data[class_name][attribute] += value
                elif operation == "multiply":
                    data[class_name][attribute] *= value
                elif operation == "constant":
                    # Set the attribute to the constant value provided
                    data[class_name][attribute] = value

        elif action_type == "return":
            # Return the specified constant or value
            return action["value"]

    return data

def lambda_handler(event, context):
    """
    AWS Lambda function to execute rules on input data.
    :param event: JSON object containing "rules" and "data".
    :param context: Lambda context object.
    :return: Result of rule execution as a JSON response.
    """
    try:
        rules = event.get("rules", [])
        data = event.get("data", {})

        # Debug: Print loaded rules and data
        print("Loaded Rules:", rules)
        print("Input Data:", data)

        results = []

        for rule in rules:
            conditions = rule.get("conditions", [])
            actions = rule.get("actions", [])

            # Debug: Print conditions and actions for each rule
            print(f"Evaluating Rule: {rule.get('rule_id')}")
            print("Conditions:", conditions)
            print("Actions:", actions)

            # Evaluate conditions and apply actions if conditions are met
            if evaluate_conditions(conditions, data):
                result = apply_actions(actions, data)
                results.append({"rule_id": rule["rule_id"], "executed": True, "result": result})
                print(f"Rule {rule.get('rule_id')} executed successfully.")
            else:
                results.append({"rule_id": rule["rule_id"], "executed": False})
                print(f"Rule {rule.get('rule_id')} did not meet conditions.")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "results": results,
                "modified_data": data
            })
        }

    except Exception as e:
        print("Error occurred:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


# import json

# def evaluate_conditions(conditions, data):
#     """
#     Evaluate all conditions based on their type (AND/OR) and the provided data.
#     :param conditions: List of condition dictionaries with type, attribute, operator, and value or comparison.
#     :param data: Dictionary representing the data object.
#     :return: True if conditions are met, else False.
#     """
#     and_conditions = [
#         cond for cond in conditions if cond.get("type") == "AND"
#     ]
#     or_conditions = [
#         cond for cond in conditions if cond.get("type") == "OR"
#     ]

#     # Evaluate AND conditions (all must be true)
#     for condition in and_conditions:
#         if not evaluate_single_condition(condition, data):
#             return False

#     # Evaluate OR conditions (at least one must be true)
#     if or_conditions:
#         if not any(evaluate_single_condition(cond, data) for cond in or_conditions):
#             return False

#     return True

# def evaluate_single_condition(condition, data):
#     """
#     Evaluate a single condition against the data.
#     :param condition: A dictionary with attribute, operator, and value or comparison.
#     :param data: Dictionary representing the data object.
#     :return: True if the condition is met, else False.
#     """
#     attribute = condition.get("attribute")
#     operator = condition.get("operator")
#     rule_compare = condition.get("rule_compare")

#     if rule_compare == "complex":
#         compare_class = condition.get("compare_class")
#         compare_attribute = condition.get("compare_attribute")
#         # Resolve nested attributes for comparison
#         compare_value = resolve_nested_attribute(data, compare_class, compare_attribute)
#         if compare_value is None:
#             return False
#         value = compare_value
#     else:
#         value = condition.get("value")

#     # Resolve nested attributes (e.g., "Product.price")
#     current_value = resolve_nested_attribute(data, condition.get("class"), attribute)

#     if current_value is None:
#         return False

#     # Perform condition evaluation
#     if operator == "equals":
#         return current_value == value
#     elif operator == "not_equals":
#         return current_value != value
#     elif operator == "greater_than":
#         return current_value > value
#     elif operator == "less_than":
#         return current_value < value
#     elif operator == "in":
#         return current_value in value
#     elif operator == "not_in":
#         return current_value not in value
#     elif operator == "between":
#         return value[0] <= current_value <= value[1]
#     else:
#         return False

# def resolve_nested_attribute(data, class_name, attribute):
#     """
#     Resolve nested attributes for a given class and attribute.
#     :param data: Dictionary representing the data object.
#     :param class_name: Class name in the data object.
#     :param attribute: Attribute name within the class.
#     :return: The resolved value of the attribute.
#     """
#     current_value = data.get(class_name, {})
#     return current_value.get(attribute, None)

# def apply_actions(actions, data):
#     """
#     Apply actions to the data object.
#     :param actions: List of action dictionaries.
#     :param data: Dictionary representing the data object.
#     :return: Modified data object or specific return values.
#     """
#     for action in actions:
#         action_type = action["type"]

#         if action_type == "operation":
#             attribute = action["attribute"]
#             operation = action["operation"]
#             value = action["value"]

#             # Resolve nested attributes (e.g., "Product.price")
#             keys = attribute.split('.')
#             current = data
#             for key in keys[:-1]:
#                 current = current.get(key)
#             final_key = keys[-1]

#             # Perform the action
#             if operation == "add":
#                 current[final_key] += value
#             elif operation == "multiply":
#                 current[final_key] *= value

#         elif action_type == "return":
#             # Return the specified constant or value
#             return action["value"]

#     return data

# def lambda_handler(event, context):
#     """
#     AWS Lambda function to execute rules on input data.
#     :param event: JSON object containing "rules" and "data".
#     :param context: Lambda context object.
#     :return: Result of rule execution.
#     """
#     try:
#         rules = event.get("rules", [])
#         data = event.get("data", {})

#         results = []

#         for rule in rules:
#             conditions = rule.get("conditions", [])
#             actions = rule.get("actions", [])

#             if evaluate_conditions(conditions, data):
#                 result = apply_actions(actions, data)
#                 results.append({"rule_id": rule["rule_id"], "executed": True, "result": result})
#             else:
#                 results.append({"rule_id": rule["rule_id"], "executed": False})

#         return {
#             "statusCode": 200,
#             "body": json.dumps({
#                 "results": results,
#                 "modified_data": data
#             })
#         }

#     except Exception as e:
#         return {
#             "statusCode": 500,
#             "body": json.dumps({"error": str(e)})
#         }
