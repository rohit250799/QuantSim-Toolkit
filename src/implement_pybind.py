from quantsim_core_engine import Order, OrderSide, OrderState, OrderValidationError

r = Order(
    1,
    'INFY',
    1223,
    134,
    3431.44,
    OrderSide.BID,
    "Test Client 1",
    29,
    10,
    OrderState.NEW
)

err = r.validate()
if err != OrderValidationError.NONE:
    raise ValueError(f'Invalid error: {err}')

print("No validation errors have been encountered!")