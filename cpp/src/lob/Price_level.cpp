#include <pybind11/pybind11.h>
#include <csignal>
#include <quantsim/lob/Price_level.hpp>
#include <queue>
#include <stdexcept>
#include <iostream>

namespace py = pybind11;

PriceLevel::PriceLevel(
    float price
    )
        : price(price)
    {}
    
void PriceLevel::addOrder(Order order) {
    // adds an order to the price level
    // only valid orders are to be added to the Price Level queue
    if (order.validate() != OrderValidationError::NONE) {
        throw std::invalid_argument("Order is not valid. Check the order again!");
    }
    std::cout << "Adding order to the queue \n";
    fifo_order_container_queue_by_price_level.push(order);
    std::cout << "Order has been successfully added to the queue \n";
    aggregateQuantity = aggregateQuantity + order.getOriginalQuantity();
}

