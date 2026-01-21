#include <pybind11/pybind11.h>
#include <cstdint>
#include <cmath>
#include <iostream>
#include <quantsim/lob/Order_book.hpp>
#include <string>

namespace py = pybind11;

Order::Order(
    int orderId, 
    std::string ticker, 
    uint64_t time, 
    int volume, 
    float price, 
    OrderSide side, 
    std::string client,
    int originalQuantity,
    int remainingQuantity,
    OrderState state
    )
        : orderId(orderId)
        , ticker(ticker)
        , time(time)
        , volume(volume)
        , price(price)
        , side(side)
        , client(client)
        , originalQuantity(originalQuantity)
        , remainingQuantity(remainingQuantity)
        , state(state)
    {}

OrderValidationError Order::validate() const noexcept {
    if (price <= 0.0) { return OrderValidationError::INVALID_PRICE; }
    if (originalQuantity <=0) { return OrderValidationError::INVALID_QUANTITY; }
    if (remainingQuantity < 0 || remainingQuantity > originalQuantity) { return OrderValidationError::OVERFILLED; }
    if (side != OrderSide::BID and side != OrderSide::ASK) { return OrderValidationError::INVALID_SIDE; }
    if (state == OrderState::CANCELLED && remainingQuantity != originalQuantity) { return OrderValidationError::INVALID_STATE; }
    return OrderValidationError::NONE;
}

bool Order::isValid() const noexcept {
    return Order::validate() == OrderValidationError::NONE;
}