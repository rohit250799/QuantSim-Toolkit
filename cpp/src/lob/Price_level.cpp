#include <pybind11/pybind11.h>
#include <quantsim/lob/Price_level.hpp>
#include <queue>

namespace py = pybind11;

PriceLevel::PriceLevel(
    float price,
    std::queue<Order> fifo_order_container_by_price_level,
    int aggregateQuantity
    )
        : price(price)
        , fifo_order_container_by_price_level(fifo_order_container_by_price_level)
        , aggregateQuantity(aggregateQuantity)
    {}
    
PriceLevel::addOrder(Order order) {
    // adds an order to the price level
    fifo_order_container_by_price_level.push(order);
}

