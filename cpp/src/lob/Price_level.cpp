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
    std::cout << "Starting order addition to the queue process.. \n";
    try {
        if (!order.isValid()) {
            throw std::invalid_argument("Order is not valid");
        }
    }
    catch (std::invalid_argument) {
       std::cout << "Since the order is invalid, it cannot be added to Price Level queue. \n";
       std::cout << "Check the order arguments again \n";
       return; 
    }
    fifo_order_container_queue_by_price_level.push(order);
    std::cout << "Order has been successfully added to the queue \n";
    aggregateQuantity = aggregateQuantity + order.getOriginalQuantity();
}

float PriceLevel::getPrice() const {
    return price;
}

int PriceLevel::getAggregateQuantity() {
    return aggregateQuantity;
}

bool PriceLevel::checkEmptyPriceLevel() {
    if (fifo_order_container_queue_by_price_level.size() < 1 or getAggregateQuantity() == 0) {
        return true;
    }
    return false;
}

// Order* PriceLevel::getFrontOrder() {
//     // returns the First order from the start of the queue
//     if (!checkEmptyPriceLevel()) {
//         return *fifo_order_container_queue_by_price_level.front();
//     }
//     std::cout << "The price level is empty. So, there is no order to be returned";
//     return;
// }

void PriceLevel::removeOrder(Order order) {
    // removes an order from the price level
}
