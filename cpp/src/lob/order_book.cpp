#include <pybind11/pybind11.h>
#include <iostream>
#include <quantsim/lob/Order_book.hpp>

namespace py = pybind11;

static const char* to_string(OrderBookRecordType type) {
    switch (type) {
        case OrderBookRecordType::BID: return "BID";
        case OrderBookRecordType::ASK: return "ASK";
        default: return "UNKNOWN";
    }
}

OrderBookRecord::OrderBookRecord(int id, long long time, int volume, float price, OrderBookRecordType recordType):
    id(id),
    time(time),
    volume(volume),
    price(price),
    recordType(recordType)
{
    
}

void OrderBookRecord::displayContents() const{
    std::cout
        << "ID: " << id
        << ", Time: " << time
        << ", Volume: " << volume
        << ", Price: " << price
        << ", Type: " << to_string(recordType)
        << std::endl;
}

AskPrices::AskPrices(std::string s) {
    std::cout << "This is the first AskPrices List";
}

int AskPrices::size() {
    return askPricesRecords.size();
}

BidPrices::BidPrices(std::string s) {
    std::cout << "This is the first BidPrices List";
}

int BidPrices::size() {
    return bidPricesRecords.size();
}
