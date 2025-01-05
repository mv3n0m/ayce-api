def ayce_conversion_rate(price, exchange_commission_percentage, ayce_buffer_percentage, payer_fees_percentage=0):

    effective_price = price / (1 + exchange_commission_percentage)

    exchange_commission = price * exchange_commission_percentage
    ayce_buffer = effective_price * ayce_buffer_percentage
    payer_fees = effective_price * payer_fees_percentage

    conversion_rate = price + ayce_buffer + payer_fees

    print(effective_price, exchange_commission)

    return {
        "conversion_rate": conversion_rate,
        "ayce_buffer": ayce_buffer,
        "payer_fees": payer_fees
    }


print(ayce_conversion_rate(26604.18, 0.006, 0.004))