# unit converter 

def convert_unit(unit:str=None, value:float=None):
    unitvalue = {
        # metric units
        "m": {"unit": 'ft', "value": value * 3.28084},
        "m2": {"unit": 'ft2', "value": value * 10.7639},
        "m3": {"unit": 'ft3', "value": value * 35.3147},
        # imperial units
        "ft": {"unit": 'm', "value": value * 0.3048},
        "ft2": {"unit": 'm2', "value": value * 0.092903},
        "ft3": {"unit": 'm3', "value": value * 0.0283168},
        # Unit measure
        "Each": {"unit": 'Each', "value": value * 1 },
        "each": {"unit": 'each', "value": value * 1 },
        "ea": {"unit": 'ea', "value": value * 1 },
        "doz": {"unit": 'doz', "value": value * 1 },
        "Day": {"unit": 'Day', "value": value * 1 },
        "day": {"unit": 'day', "value": value * 1 },
        "Daily": {"unit": 'Daily', "value": value * 1 },
        "hr": {"unit": 'hr', "value": value * 1 },
        "length": {"unit": 'length', "value": value * 1 },
        "Length": {"unit": 'length', "value": value * 1 },
        # Weight and Mass units
        "gm": {"unit": 'oz', "value": value * 0.035274 },
        "kg": {"unit": 'lb', "value": value * 2.20462 },
        "oz": {"unit": 'gm', "value": value * 28.3495 },
        "lb": {"unit": 'kg', "value": value * 0.453592 },
    }

    return unitvalue.get(unit)


def convert_price_by_unit(unit:str=None, value:float=None):
    unitvalue = {
        # metric units
        "m": {"unit": 'ft', "value": value / 3.28084},
        "m2": {"unit": 'ft2', "value": value / 10.7639},
        "m3": {"unit": 'ft3', "value": value / 35.3147},
        # imperial units
        "ft": {"unit": 'm', "value": value / 0.3048},
        "ft2": {"unit": 'm2', "value": value / 0.092903},
        "ft3": {"unit": 'm3', "value": value / 0.0283168},
        # Unit measure
        "Each": {"unit": 'Each', "value": value * 1 },
        "each": {"unit": 'each', "value": value * 1 },
        "ea": {"unit": 'ea', "value": value * 1 },
        "doz": {"unit": 'doz', "value": value * 1 },
        "Day": {"unit": 'Day', "value": value * 1 },
        "day": {"unit": 'day', "value": value * 1 },
        "Daily": {"unit": 'Daily', "value": value * 1 },
        "hr": {"unit": 'hr', "value": value * 1 },
        "length": {"unit": 'length', "value": value * 1 },
        "Length": {"unit": 'length', "value": value * 1 },
        # Weight and Mass units
        "gm": {"unit": 'oz', "value": value / 0.035274 },
        "kg": {"unit": 'lb', "value": value / 2.20462 },
        "oz": {"unit": 'gm', "value": value / 28.3495 },
        "lb": {"unit": 'kg', "value": value / 0.453592 },
    }

    return unitvalue.get(unit)

#print(convert_price_by_unit('kg', 306.58))

