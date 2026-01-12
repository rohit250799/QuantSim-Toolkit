#include "include/quantsim/lob/Order_book.hpp"
#include <pybind11/pybind11.h>
#include <ctime>
#include <quantsim/lob/Order_book.hpp>

namespace py = pybind11;

int add(int a, int b) {
    return a + b;
}

PYBIND11_MODULE(quantsim_core_engine, module_handle, py::mod_gil_not_used()) {
    module_handle.doc() = "Core engine for Quantsim project - for Limit Order Book implementation";
    module_handle.def("quantsim_fn_python_name_add", &add, "A function that adds 2 numbers");
    
    py::enum_<OrderBookRecordType>(module_handle, "OrderBookRecordType")
        .value("BID", OrderBookRecordType::BID)
        .value("ASK", OrderBookRecordType::ASK)
        .export_values();
    
    py::class_<OrderBookRecord>(module_handle, "OrderBookRecord")
        .def(py::init<int, long long, int, float, OrderBookRecordType>())
        .def("displayContents", &OrderBookRecord::displayContents);
}

