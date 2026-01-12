#pragma once

#include <string>
#include <vector>

enum class OrderBookRecordType {
    BID,
    ASK
};

class OrderBookRecord {
    public:
        int id;
        long long time;
        int volume;
        float price;
        OrderBookRecordType recordType;
        
        OrderBookRecord(
            int id, 
            long long time, 
            int volume, 
            float price, 
            enum OrderBookRecordType recordType
        );
        
        void displayContents() const;
};

class AskPrices {
    public:
        OrderBookRecordType type = OrderBookRecordType::ASK;
        std::vector<OrderBookRecord> askPricesRecords;
        AskPrices(std::string s);
        int size();
};

class BidPrices {
    public:
        enum OrderBookRecordType type = OrderBookRecordType::BID;
        std::vector<OrderBookRecord> bidPricesRecords;
        BidPrices(std::string s);
        int size();
};