"""
Core engine for Quantsim project - for Limit Order Book implementation
"""
from __future__ import annotations
import typing
__all__: list[str] = ['ASK', 'BID', 'OrderBookRecord', 'OrderBookRecordType', 'quantsim_fn_python_name_add']
class OrderBookRecord:
    def __init__(self, arg0: typing.SupportsInt, arg1: typing.SupportsInt, arg2: typing.SupportsInt, arg3: typing.SupportsFloat, arg4: OrderBookRecordType) -> None:
        ...
    def displayContents(self) -> None:
        ...
class OrderBookRecordType:
    """
    Members:
    
      BID
    
      ASK
    """
    ASK: typing.ClassVar[OrderBookRecordType]  # value = <OrderBookRecordType.ASK: 1>
    BID: typing.ClassVar[OrderBookRecordType]  # value = <OrderBookRecordType.BID: 0>
    __members__: typing.ClassVar[dict[str, OrderBookRecordType]]  # value = {'BID': <OrderBookRecordType.BID: 0>, 'ASK': <OrderBookRecordType.ASK: 1>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
def quantsim_fn_python_name_add(arg0: typing.SupportsInt, arg1: typing.SupportsInt) -> int:
    """
    A function that adds 2 numbers
    """
ASK: OrderBookRecordType  # value = <OrderBookRecordType.ASK: 1>
BID: OrderBookRecordType  # value = <OrderBookRecordType.BID: 0>
