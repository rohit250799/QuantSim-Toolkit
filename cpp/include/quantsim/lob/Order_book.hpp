#include <pybind11/pybind11.h>

namespace py = pybind11;

#pragma once

#include <string>

enum class OrderSide {
    BID,
    ASK
};

enum class OrderState {
    NEW,
    PARTIALLY_FILLED,
    FILLED,
    CANCELLED
};

class Order {
    public:
        void displayContents() const;
        bool checkValidity(Order order);
        
    private:
        int orderId;
        std::string ticker;
        long long time;
        int volume;
        float price;
        OrderSide side;
        std::string client;
        int originalQuantity;
        int remainingQuantity;
        OrderState state;
        
        Order(
            int orderId,
            std::string ticker, 
            long long time, 
            int volume, 
            float price, 
            enum OrderSide side,
            std::string client,
            int originalQuantity,
            int remainingQuantity,
            enum OrderState state
        );
};
