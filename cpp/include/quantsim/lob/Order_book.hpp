#include <pybind11/pybind11.h>
#include <string>
#include <cstdint>

namespace py = pybind11;

#pragma once

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

enum class OrderValidationError : uint8_t {
    NONE = 0,
    INVALID_QUANTITY,
    OVERFILLED,
    INVALID_PRICE,
    INVALID_SIDE,
    INVALID_STATE,
    TIME_STAMP_IN_FUTURE
};

class Order {
    public:
        Order() = default;
        Order(
            int orderId,
            std::string ticker, 
            uint64_t time, 
            int volume, 
            float price, 
            enum OrderSide side,
            std::string client,
            int originalQuantity,
            int remainingQuantity,
            enum OrderState state
        );
        void displayContents() const;
        OrderValidationError validate() const noexcept;
        bool isValid() const noexcept;
        
    private:
        int orderId = 1;
        std::string ticker = "TCS";
        uint64_t time = 100044;
        int volume = 100;
        float price = 155.45;
        OrderSide side = OrderSide::BID;
        std::string client = "Test Client";
        int originalQuantity = 150;
        int remainingQuantity = 150;
        OrderState state = OrderState::NEW;
};
