from quantsim_core_engine import Order, OrderSide, OrderState, OrderValidationError, PriceLevel

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

r1 = Order(
    1,
    'INFY',
    1223,
    134,
    3431.44,
    OrderSide.BID,
    "Test Client 1",
    -16,
    10,
    OrderState.NEW
)

err = r.validate()
if err != OrderValidationError.NONE:
    raise ValueError(f'Invalid error: {err}')

print("No validation errors have been encountered!")

test_price_level = PriceLevel(100)

test_price_level.addOrder(r)
test_price_level.addOrder(r1)
