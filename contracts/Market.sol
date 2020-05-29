pragma solidity ^0.5.7;

pragma experimental ABIEncoderV2;

contract Market {
    struct Buyer {
        address id;
        mapping(string => string) orderHistory; // good's Id => time bought
        bool init;
    }

    struct Seller {
        address id;
        bool init;
    }

    mapping(address => Buyer) buyers;
    mapping(address => Seller) sellers;
    mapping(address => Seller) verifiedSellers;

    struct DigitalGood {
        string ticketId;
        string name;
        uint price;
        Seller seller;
        bool init;
    }

    mapping(string => uint) originalDigitalGoodPrice;
    string[] allocatedIds;
    mapping(string => DigitalGood) allocatedDigitalGoods;
    mapping(string => DigitalGood) redeemedDigitalGoods;

    struct PhysicalGood {
        string sku;
        string name;
        uint price;
        uint quantity;
        Seller seller;
        bool init;
    }

    string[] skus;
    mapping(string => PhysicalGood) physicalGoods;
    mapping(string => uint[]) priceHistories;

    function listDigitalGood(string memory _ticketId, string memory _name, uint _price, address sellerId, bool isVerifiedSeller) public {
        require(_price > 0, "Ticket price cannot be negative or zero");

        if (!sellers[sellerId].init) {
            Seller memory _seller = Seller({
                id: sellerId,
                init: true
            });
            if (isVerifiedSeller) {
                verifiedSellers[sellerId] = _seller;
            }

            sellers[sellerId] = _seller;
        }

        if (originalDigitalGoodPrice[_ticketId] == 0) { // the ticketId was never allocated
            originalDigitalGoodPrice[_ticketId] = _price;
            DigitalGood memory dg = DigitalGood({
                ticketId: _ticketId,
                name: _name,
                price: _price,
                seller: sellers[sellerId],
                init: true
            });

            allocatedDigitalGoods[_ticketId] = dg;
            allocatedIds.push(_ticketId);
            // emit event
        } else {
            // require(redeemedDigitalGoods[_ticketId].init, "Ticket was never redeemed.");
            uint originalPrice = originalDigitalGoodPrice[_ticketId];

            require(_price <= originalPrice, "Price is above original ticket price.");
            DigitalGood storage redeemed = redeemedDigitalGoods[_ticketId];

            // require(redeemed.seller.id == sellerId, "Seller ID doesn't match owner's.");

            // uint originalPrice = originalDigitalGoodPrice[_ticketId];

            // require(_price <= originalPrice, "Price is above original ticket price.");

            DigitalGood memory next = DigitalGood({
                ticketId: redeemed.ticketId,
                name: redeemed.name,
                price: _price,
                seller: sellers[sellerId],
                init: true
            });

            delete redeemedDigitalGoods[_ticketId];

            // redeemed.price = _price;

            allocatedDigitalGoods[redeemed.ticketId] = next;
            allocatedIds.push(_ticketId);

            // emit event
        }
    }

    function priceHistory(string memory sku) public returns(uint[] memory) {
        return priceHistories[sku];
    }

    function listPhysicalGood(string memory _sku, string memory _name, uint _price, uint _quantity, address sellerId, bool isVerifiedSeller, bool isFairPrice) public {
        require(_price > 0, "Item price cannot be negative or zero");
        require(_quantity > 0, "Item quantity cannot be negative or zero");

        if (!sellers[sellerId].init) {
            Seller memory _seller = Seller({
                id: sellerId,
                init: true
            });
            if (isVerifiedSeller) {
                verifiedSellers[sellerId] = _seller;
            }

            sellers[sellerId] = _seller;
        }

        if (isVerifiedSeller) {
            PhysicalGood memory item = PhysicalGood({
                sku: _sku,
                name: _name,
                price: _price,
                quantity: _quantity,
                seller: sellers[sellerId],
                init: true
            });

            priceHistories[_sku].push(_price);
            physicalGoods[_sku] = item;
            skus.push(_sku);
        } else {
            require(isFairPrice , "Price is too high to be fair.");
                
            PhysicalGood memory item = PhysicalGood({
                sku: _sku,
                name: _name,
                price: _price,
                quantity: _quantity,
                seller: sellers[sellerId],
                init: true
            });

            physicalGoods[_sku] = item;
            skus.push(_sku);
            // emit event
        }

        // if (physicalGoods[_sku].init) { // the physical good has been seen
        //     PhysicalGood storage item = physicalGoods[_sku];
        //     require(item.price == _price, "Cannot change the price of an existing good.");
        //     require(stringsMatch(item.seller.id, sellerId), "A different seller cannot sell the same item.");
        //     item.quantity += _quantity;

        //     // emit event
        // } else {
        //     if (isVerifiedSeller) {
        //         PhysicalGood memory item = PhysicalGood({
        //             sku: _sku,
        //             name: _name,
        //             price: _price,
        //             quantity: _quantity,
        //             seller: sellers[sellerId],
        //             init: true
        //         });

        //         priceHistories[_sku].push(_price);
        //         physicalGoods[_sku] = item;
        //         skus.push(_sku);

        //         // emit event
        //     } else {
        //         require(isFairPrice, "Price is too high to be fair.");
                
        //         PhysicalGood memory item = PhysicalGood({
        //             sku: _sku,
        //             name: _name,
        //             price: _price,
        //             quantity: _quantity,
        //             seller: sellers[sellerId],
        //             init: true
        //         });

        //         physicalGoods[_sku] = item;
        //         skus.push(_sku);
        //         // emit event
        //     }
        // }
    }

    function buyDigitalGood(string memory ticketId, address buyerId, string memory time) public {
        // require(!allocatedDigitalGoods[ticketId].init, "Ticket was never allocated.");
        // require(!redeemedDigitalGoods[ticketId].init, "Ticket was already redeemed.");

        if (buyers[buyerId].init) {
            redeemedDigitalGoods[ticketId] = allocatedDigitalGoods[ticketId];
            delete allocatedDigitalGoods[ticketId];
            removeFromAllocatedIds(ticketId);

            redeemedDigitalGoods[ticketId].seller = Seller({
                id: buyerId,
                init: true
            });

            Buyer storage buyer = buyers[buyerId];
            buyer.orderHistory[ticketId] = time;
        } else {
            buyers[buyerId] = Buyer({
                id: buyerId,
                init: true
            });

            buyers[buyerId].orderHistory[ticketId] = time;

            redeemedDigitalGoods[ticketId] = allocatedDigitalGoods[ticketId];
            delete allocatedDigitalGoods[ticketId];
            removeFromAllocatedIds(ticketId);

            redeemedDigitalGoods[ticketId].seller = Seller({
                id: buyerId,
                init: true
            });
        }
    }

    function buyPhysicalGood(string memory sku, uint quantity, address buyerId, string memory time) public {
        require(quantity > 0, "Quantity cannot be negative or zero.");
        require(quantity <= 2, "Please take less than 2 items.");

        if (buyers[buyerId].init) {
            PhysicalGood storage good = physicalGoods[sku];
            require(good.quantity >= quantity, "Buying too much quantity");
            
            if (good.quantity == quantity) {
                delete physicalGoods[sku];
                delete priceHistories[sku];
                removeFromSkus(sku);
            } else {
                good.quantity -= quantity;
            }

            Buyer storage buyer = buyers[buyerId];
            buyer.orderHistory[sku] = time;
        } else {
            PhysicalGood storage good = physicalGoods[sku];
            require(good.quantity >= quantity, "Buying too much quantity");
            
            if (good.quantity == quantity) {
                delete physicalGoods[sku];
                delete priceHistories[sku];
                removeFromSkus(sku);
            } else {
                good.quantity -= quantity;
            }

            buyers[buyerId] = Buyer({
                id: buyerId,
                init: true
            });

            buyers[buyerId].orderHistory[sku] = time;
        }
    }

    function removeFromAllocatedIds(string memory toDelete) public {
        uint ind = 0;
        bool found = false;
        for (uint i = 0; i < allocatedIds.length; i++) {
            if (stringsMatch(allocatedIds[i], toDelete)) {
                ind = i;
                found = true;
                break;
            }
        }

        if (found) {
            for (uint i = ind; i < allocatedIds.length - 1; i++) {
                allocatedIds[i] = allocatedIds[i + 1];
            }

            delete allocatedIds[allocatedIds.length - 1];
            allocatedIds.length--;
        }
    }

    function removeFromSkus(string memory toDelete) public {
        uint ind = 0;
        bool found = false;
        for (uint i = 0; i < skus.length; i++) {
            if (stringsMatch(skus[i], toDelete)) {
                ind = i;
                found = true;
                break;
            }
        }

        if (found) {
            for (uint i = ind; i < skus.length - 1; i++) {
                skus[i] = skus[i + 1];
            }

            delete skus[skus.length - 1];
            skus.length--;
        }
    }

    function stringsMatch(string memory a, string memory b) public returns(bool) {
        return keccak256(abi.encodePacked(a)) == keccak256(abi.encodePacked(b)); // as specified with stack overflow
    }

    function getBuyerHistory(string memory sku, address buyerId) public returns(string memory) {
        require(buyers[buyerId].init, "Buyer doesn't exist.");

        return buyers[buyerId].orderHistory[sku];
    }

    function getDigitalGoods() public returns(string[] memory, string[] memory) {
        string[] memory names = new string[](allocatedIds.length);

        for (uint i = 0; i < allocatedIds.length; i++) {
            names[i] = allocatedDigitalGoods[allocatedIds[i]].name;
        }

        return (allocatedIds, names);
    }

    function getPhysicalGoods() public returns(string[] memory, string[] memory) {
        string[] memory names = new string[](skus.length);

        for (uint i = 0; i < skus.length; i++) {
            names[i] = physicalGoods[skus[i]].name;
        }

        return (skus, names);
    }
}