def format_amount_to_display(amount: float) -> float | int:
    if amount - int(amount) == 0:
        amount = int(amount)
    return amount
