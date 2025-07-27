def celsius_to_fahrenheit(celsius: int | float) -> int | float:
    return round((celsius * (9 / 5)) + 32)


def try_get_value(delta: dict, state: dict, key: str, default=any):
    if key in delta:
        return delta.get(key, default)

    if key in state:
        return state.get(key, default)

    return default
