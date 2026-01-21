#include "include/quantsim/lob/Order_book.hpp"
#include <pybind11/pybind11.h>
#include <ctime>
#include <quantsim/lob/Order_book.hpp>
//#include "include/quantsim/lob/Order_book.hpp"

namespace py = pybind11;

PYBIND11_MODULE(quantsim_core_engine, module_handle, py::mod_gil_not_used()) {
    module_handle.doc() = "Core engine for Quantsim project - for Limit Order Book implementation";
    
    py::enum_<OrderSide>(module_handle, "OrderSide", "Represents the side of the Order")
        .value("BID", OrderSide::BID)
        .value("ASK", OrderSide::ASK)
        .export_values();
    
    py::enum_<OrderState>(module_handle, "OrderState", "Represents the state of the order")
        .value("NEW", OrderState::NEW)
        .value("PARTIALLY_FILLED", OrderState::PARTIALLY_FILLED)
        .value("FILLED", OrderState::FILLED)
        .value("CANCELLED", OrderState::CANCELLED)
        .export_values();
    
    py::enum_<OrderValidationError>(module_handle, "OrderValidationError", "Stores the validation error type in Order")
        .value("NONE", OrderValidationError::NONE)
        .value("INVALID_PRICE", OrderValidationError::INVALID_PRICE)
        .value("INVALID_QUANTITY", OrderValidationError::INVALID_QUANTITY)
        .value("OVERFILLED", OrderValidationError::OVERFILLED)
        .value("INVALID_SIDE", OrderValidationError::INVALID_SIDE)
        .value("INVALID_STATE", OrderValidationError::INVALID_STATE)
        .value("TIME_STAMP_IN_FUTURE", OrderValidationError::TIME_STAMP_IN_FUTURE)
        .export_values();
    
    py::class_<Order>(module_handle, "Order")
        .def(py::init<int, std::string, long long, int, float, OrderSide, std::string, int, int, OrderState>())
        .def("validate", &Order::validate)
        .def("is_valid", &Order::isValid);
}

