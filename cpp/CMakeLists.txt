cmake_minimum_required(VERSION 3.15...4.0)
project(quantsim_core_engine LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(quantsim_core_engine 
    pybind_module.cpp
    src/lob/order_book.cpp
)

target_include_directories(quantsim_core_engine
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include
)

install(TARGETS quantsim_core_engine DESTINATION .)
