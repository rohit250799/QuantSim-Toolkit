"""
Core engine for Quantsim project - for Limit Order Book implementation
"""
from __future__ import annotations
import typing
__all__: list[str] = ['ASK', 'BID', 'CANCELLED', 'FILLED', 'INVALID_PRICE', 'INVALID_QUANTITY', 'INVALID_SIDE', 'INVALID_STATE', 'NEW', 'NONE', 'OVERFILLED', 'Order', 'OrderSide', 'OrderState', 'OrderValidationError', 'PARTIALLY_FILLED', 'TIME_STAMP_IN_FUTURE']
class Order:
    def __init__(self, arg0: typing.SupportsInt, arg1: str, arg2: typing.SupportsInt, arg3: typing.SupportsInt, arg4: typing.SupportsFloat, arg5: OrderSide, arg6: str, arg7: typing.SupportsInt, arg8: typing.SupportsInt, arg9: OrderState) -> None:
        ...
    def is_valid(self) -> bool:
        ...
    def validate(self) -> OrderValidationError:
        ...
class OrderSide:
    """
    Represents the side of the Order
    
    Members:
    
      BID
    
      ASK
    """
    ASK: typing.ClassVar[OrderSide]  # value = <OrderSide.ASK: 1>
    BID: typing.ClassVar[OrderSide]  # value = <OrderSide.BID: 0>
    __members__: typing.ClassVar[dict[str, OrderSide]]  # value = {'BID': <OrderSide.BID: 0>, 'ASK': <OrderSide.ASK: 1>}
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
class OrderState:
    """
    Represents the state of the order
    
    Members:
    
      NEW
    
      PARTIALLY_FILLED
    
      FILLED
    
      CANCELLED
    """
    CANCELLED: typing.ClassVar[OrderState]  # value = <OrderState.CANCELLED: 3>
    FILLED: typing.ClassVar[OrderState]  # value = <OrderState.FILLED: 2>
    NEW: typing.ClassVar[OrderState]  # value = <OrderState.NEW: 0>
    PARTIALLY_FILLED: typing.ClassVar[OrderState]  # value = <OrderState.PARTIALLY_FILLED: 1>
    __members__: typing.ClassVar[dict[str, OrderState]]  # value = {'NEW': <OrderState.NEW: 0>, 'PARTIALLY_FILLED': <OrderState.PARTIALLY_FILLED: 1>, 'FILLED': <OrderState.FILLED: 2>, 'CANCELLED': <OrderState.CANCELLED: 3>}
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
class OrderValidationError:
    """
    Stores the validation error type in Order
    
    Members:
    
      NONE
    
      INVALID_PRICE
    
      INVALID_QUANTITY
    
      OVERFILLED
    
      INVALID_SIDE
    
      INVALID_STATE
    
      TIME_STAMP_IN_FUTURE
    """
    INVALID_PRICE: typing.ClassVar[OrderValidationError]  # value = <OrderValidationError.INVALID_PRICE: 3>
    INVALID_QUANTITY: typing.ClassVar[OrderValidationError]  # value = <OrderValidationError.INVALID_QUANTITY: 1>
    INVALID_SIDE: typing.ClassVar[OrderValidationError]  # value = <OrderValidationError.INVALID_SIDE: 4>
    INVALID_STATE: typing.ClassVar[OrderValidationError]  # value = <OrderValidationError.INVALID_STATE: 5>
    NONE: typing.ClassVar[OrderValidationError]  # value = <OrderValidationError.NONE: 0>
    OVERFILLED: typing.ClassVar[OrderValidationError]  # value = <OrderValidationError.OVERFILLED: 2>
    TIME_STAMP_IN_FUTURE: typing.ClassVar[OrderValidationError]  # value = <OrderValidationError.TIME_STAMP_IN_FUTURE: 6>
    __members__: typing.ClassVar[dict[str, OrderValidationError]]  # value = {'NONE': <OrderValidationError.NONE: 0>, 'INVALID_PRICE': <OrderValidationError.INVALID_PRICE: 3>, 'INVALID_QUANTITY': <OrderValidationError.INVALID_QUANTITY: 1>, 'OVERFILLED': <OrderValidationError.OVERFILLED: 2>, 'INVALID_SIDE': <OrderValidationError.INVALID_SIDE: 4>, 'INVALID_STATE': <OrderValidationError.INVALID_STATE: 5>, 'TIME_STAMP_IN_FUTURE': <OrderValidationError.TIME_STAMP_IN_FUTURE: 6>}
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
ASK: OrderSide  # value = <OrderSide.ASK: 1>
BID: OrderSide  # value = <OrderSide.BID: 0>
CANCELLED: OrderState  # value = <OrderState.CANCELLED: 3>
FILLED: OrderState  # value = <OrderState.FILLED: 2>
INVALID_PRICE: OrderValidationError  # value = <OrderValidationError.INVALID_PRICE: 3>
INVALID_QUANTITY: OrderValidationError  # value = <OrderValidationError.INVALID_QUANTITY: 1>
INVALID_SIDE: OrderValidationError  # value = <OrderValidationError.INVALID_SIDE: 4>
INVALID_STATE: OrderValidationError  # value = <OrderValidationError.INVALID_STATE: 5>
NEW: OrderState  # value = <OrderState.NEW: 0>
NONE: OrderValidationError  # value = <OrderValidationError.NONE: 0>
OVERFILLED: OrderValidationError  # value = <OrderValidationError.OVERFILLED: 2>
PARTIALLY_FILLED: OrderState  # value = <OrderState.PARTIALLY_FILLED: 1>
TIME_STAMP_IN_FUTURE: OrderValidationError  # value = <OrderValidationError.TIME_STAMP_IN_FUTURE: 6>
