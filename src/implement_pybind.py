from quantsim_core_engine import OrderBookRecordType, OrderBookRecord

r = OrderBookRecord(
    1,
    1223,
    100,
    3431.44,
    OrderBookRecordType.BID
)

r.displayContents()
