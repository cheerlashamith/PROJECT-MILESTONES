def fraud_detector(expected_cost, contractor_quote):

    if contractor_quote > expected_cost * 1.20:
        return "Warning: Contractor may be overcharging"

    return "Cost looks normal"