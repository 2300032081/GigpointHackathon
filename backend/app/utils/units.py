UNIT_ALIASES = {
    "piece": {"piece", "pieces", "pc", "pcs", "packet", "packets"},
    "kg": {"kg", "kgs", "kilo", "kilos", "kilogram", "kilograms", "kilo"},
    "g": {"g", "gram", "grams"},
    "bag": {"bag", "bags"},
    "carton": {"carton", "cartons"},
    "box": {"box", "boxes"},
    "dozen": {"dozen", "dozens"},
    "litre": {"litre", "litres", "liter", "liters", "l", "liters"},
    "quintal": {"quintal", "quintals"},
}


def normalize_unit(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.strip().lower()
    for canonical, aliases in UNIT_ALIASES.items():
        if candidate in aliases:
            return canonical
    return candidate
