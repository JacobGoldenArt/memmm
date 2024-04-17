def convert_value(value: str, target_type: type):
    if target_type == bool:
        return value.lower() in ["true", "1", "yes"]
    elif target_type in [int, float]:
        return target_type(value)
    else:
        return value
