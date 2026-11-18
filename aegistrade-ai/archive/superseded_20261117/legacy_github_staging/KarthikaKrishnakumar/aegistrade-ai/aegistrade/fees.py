"""Fixed screenshot-based NSE equity-delivery cost assumptions, not a broker tariff feed."""
# Percentage-of-turnover components; brokerage is fixed at zero delivery brokerage.
STT_BPS = 10.0                 # Both sides: 0.1%
STAMP_BUY_BPS = 1.5            # Buy only: 0.015%
EXCHANGE_BPS = 0.307           # Screenshot NSE: 0.00307%
SEBI_BPS = 0.01                # Rs 10/crore: 0.0001%
GST_RATE = 0.18                # Brokerage + exchange + SEBI; excludes STT/stamp
BUY_FEE_BPS = STT_BPS + STAMP_BUY_BPS + (EXCHANGE_BPS + SEBI_BPS)*(1+GST_RATE)
SELL_FEE_BPS = STT_BPS + (EXCHANGE_BPS + SEBI_BPS)*(1+GST_RATE)
FEE_MODEL = 'nse-delivery-screenshot-zero-brokerage-v1'


def charge_breakdown(turnover, side):
    if side not in ('BUY', 'SELL'): raise ValueError('Expected BUY or SELL')
    if turnover < 0: raise ValueError('Turnover must be nonnegative')
    exchange=turnover*EXCHANGE_BPS/10000; sebi=turnover*SEBI_BPS/10000
    result={'brokerage':0.,'stt':turnover*STT_BPS/10000,
            'stamp_duty':turnover*STAMP_BUY_BPS/10000 if side=='BUY' else 0.,
            'exchange':exchange,'sebi':sebi,'gst':(exchange+sebi)*GST_RATE}
    return {**result,'total':sum(result.values())}
