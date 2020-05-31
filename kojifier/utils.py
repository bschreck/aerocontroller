import yaml


def parse_time(t):
    units = {
        'h': 60 * 60,
        'm': 60,
        's': 1,
    }
    t_with_u = str(t).lower()
    for unit in units:
        try:
            if t_with_u[-1] != unit:
                continue
            t_no_u = t_with_u[:-1]
            return int(t_no_u) * units[unit]
        except Exception:
            continue
    return int(t)


def parse_temp(temp, unit):
    unit = unit.lower()
    temp = temp.lower()
    temp_unit = temp[-1]
    temp = int(temp[:-1])
    if temp_unit == 'f' and unit == 'f':
        return temp
    elif temp_unit == 'f' and unit == 'c':
        return (5/9) * (temp - 32)
    elif temp_unit == 'c' and unit == 'c':
        return temp
    elif temp_unit == 'c' and unit == 'f':
        return (9/5) * temp + 32


def load_config(config_path):
    with open(config_path) as f:
        config = yaml.safe_load(f)
    for k, v in config.items():
        if k.endswith('_time'):
            config[k] = parse_time(v)
        elif k.endswith("_temp"):
            config[k] = parse_temp(v, config.get("unit", "F"))
    return config
