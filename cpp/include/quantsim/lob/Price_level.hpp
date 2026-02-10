#include <pybind11/pybind11.h>
#include <queue>
#include "Order_book.hpp"

namespace py = pybind11;

pragma once

class PriceLevel {
    // Also known as Limit, Level or Bucket. Every PriceLevel stores a queue of Orders, tracks
    // aggregate quantity, includes add/remove logic and enforces price-level invariants. Every price level is a 
    // queue of orders with the same price 
    public:
        PriceLevel() = default;
        PriceLevel(float price, std::queue<Order> fifo_order_container_by_price_level, int aggregateQuantity);
        void addOrder(Order order);
        void removeOrder(Order order);
        bool checkEmptyPriceLevel();
    
    private:
        float price;
        std::queue<Order> fifo_order_container_queue_by_price_level;
        int aggregateQuantity;
}