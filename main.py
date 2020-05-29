import json, sys
from web3 import Web3
from flask import Flask, request, jsonify
# from flask_cors import CORS
import numpy as np
from datetime import datetime

app = Flask(__name__)
# CORS(app)

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545')) # points to the URL provided by Ganache
w3.eth.defaultAccount = w3.eth.accounts[0]

account_map = {
    'baddamanu@yahoo.com': w3.eth.accounts[1],
    'Anurag': w3.eth.accounts[2]
}

with open('./build/contracts/Market.json', 'r') as f:
    truffle_file = json.load(f)
    abi = truffle_file['abi']
    bytecode = truffle_file['bytecode']

contract = w3.eth.contract(bytecode=bytecode, abi=abi)
tx_hash = contract.constructor().transact()
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
contract_address = tx_receipt['contractAddress']

def is_fair_price(sku, price):
    # grab contract
    item = w3.eth.contract(address=contract_address, abi=abi)

    price_history = item.functions.priceHistory(sku).call()

    if len(price_history) == 0:
        return True

    max_price = np.max(price_history)
    
    if price < max_price:
        return True

    mean = np.mean(price_history)
    std_dev = np.std(price_history)

    print('price_history: ' + str(price_history))
    print('price: ' + str(price))
    print('mean: ' + str(mean))
    print('std_dev: ' + str(std_dev))

    return price <= mean + 1.5 * std_dev

def is_hoarding(sku, buyer_id, quantity):
    if quantity > 2:
        return True
     # grab contract
    # item = w3.eth.contract(address=contract_address, abi=abi)

    # last_order = item.functions.getBuyerHistory(sku, account_map[buyer_id]).call()

    # last_bought = datetime.strptime(last_order, "%Y-%m-%d %H:%M:%S.%f")
    # current_time = datetime.strptime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")

    # difference = current_time - last_bought

    # return difference.total_seconds() < 10
    return False

@app.route('/list', methods=['POST'])
def listing():
    # grab contract
    item = w3.eth.contract(address=contract_address, abi=abi)
    
    category = request.args.get('category')

    # pass information to solidity and get results
    if category == 'digital':
        ticket_id = request.args.get('ticketId')
        item_name = request.args.get('name')
        price = int(request.args.get('price'))
        seller_id = request.args.get('sellerId')
        is_verified_seller = request.args.get('isVerifiedSeller') == 'true'

        try :
            tx_hash = item.functions.listDigitalGood(
                ticket_id, 
                item_name,
                price,
                account_map[seller_id],
                is_verified_seller).transact()

            w3.eth.waitForTransactionReceipt(tx_hash)

            return jsonify({'data': 'worked'}), 200
        except ValueError as e:
            return jsonify({'data': str(e)}), 200
        
    else:
        sku = request.args.get('sku')
        item_name = request.args.get('name')
        price = int(request.args.get('price'))
        quantity = int(request.args.get('quantity'))
        seller_id = request.args.get('sellerId')
        # print(request.args.get('isVerifiedSeller'))
        is_verified_seller = request.args.get('isVerifiedSeller') == 'true'
        fair_price = bool(is_fair_price(sku, price))

        # item = w3.eth.contract(address=contract_address, abi=abi)

        # price_history = item.functions.priceHistory(sku).call()

        # max_price = np.max(price_history)

        # mean = np.mean(price_history)
        # std_dev = np.std(price_history)

        # app.logger.info('price_history: ' + str(price_history))
        # print('price: ' + str(price))
        # print('mean: ' + str(mean))
        # print('std_dev: ' + str(std_dev))

        # print("is_verified_seller: " + str(is_verified_seller))
        # print("fair_price: " + str(fair_price))
        # print(str(not is_verified_seller and not fair_price))

        # if not is_verified_seller and not fair_price:
        #     return jsonify({'data': 'does not work'}), 200

        # if is_verified_seller:
        try :
            tx_hash = item.functions.listPhysicalGood(
                sku, 
                item_name,
                price,
                quantity,
                account_map[seller_id],
                is_verified_seller,
                fair_price).transact()

            w3.eth.waitForTransactionReceipt(tx_hash)

            return jsonify({'data': 'worked'}), 200
        except ValueError as e:
            return jsonify({'data': str(e)}), 200
        # elif not fair_price:
        #     return jsonify({'data': 'does not work'}), 200

@app.route('/buy', methods=['POST'])
def buy():
    # grab contract
    item = w3.eth.contract(address=contract_address, abi=abi)
    
    category = request.args.get('category')

    curr_time = str(datetime.now())

    # pass information to solidity and get results
    if category == 'digital':
        ticket_id = request.args.get('ticketId')
        buyer_id = request.args.get('buyerId')

        tx_hash = item.functions.buyDigitalGood(
            ticket_id, 
            account_map[buyer_id],
            curr_time).transact()

        w3.eth.waitForTransactionReceipt(tx_hash)
    else:
        sku = request.args.get('sku')
        quantity = int(request.args.get('quantity'))
        buyer_id = request.args.get('buyerId')
        item_name = request.args.get('name')

        if is_hoarding(sku, buyer_id, quantity):
            return jsonify({'data': 'Hoarding is being done.'}), 200

        tx_hash = item.functions.buyPhysicalGood(
            sku,
            item_name,
            quantity,
            account_map[buyer_id],
            curr_time).transact()

        w3.eth.waitForTransactionReceipt(tx_hash)

    return jsonify({'data': 'worked'}), 200

@app.route('/show', methods=['GET'])
def show():
    # grab contract
    item = w3.eth.contract(address=contract_address, abi=abi)

    digital_goods = item.functions.getDigitalGoods().call()
    physical_goods = item.functions.getPhysicalGoods().call()

    # pass information to solidity and get results
    
    return jsonify({'digital_goods': digital_goods, 'physical_goods': physical_goods}), 200
