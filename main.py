import json
from web3 import Web3
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from datetime import datetime

app = Flask(__name__)
CORS(app)

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545')) # points to the URL provided by Ganache
w3.eth.defaultAccount = w3.eth.accounts[0]

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
        return true

    mean = np.mean(price_history)
    std_dev = np.std(price_history)

    return price <= mean + 1.5 * std_dev

def is_hoarding(sku, buyer_id):
     # grab contract
    item = w3.eth.contract(address=contract_address, abi=abi)

    last_order = item.functions.getBuyerHistory(sku, buyer_id).call()

    last_bought = datetime.strptime(last_order)
    current_time = datetime.now()

    difference = current_time - last_bought

    return difference.total_seconds() / 3600 < 2

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
        is_verified_seller = bool(request.args.get('isVerifiedSeller'))

        tx_hash = item.functions.listDigitalGood(
            ticket_id, 
            item_name,
            price,
            seller_id,
            is_verified_seller).transact()

        w3.eth.waitForTransactionReceipt(tx_hash)
    else:
        sku = request.args.get('sku')
        item_name = request.args.get('name')
        price = int(request.args.get('price'))
        quantity = int(request.args.get('quantity'))
        seller_id = request.args.get('sellerId')
        is_verified_seller = bool(request.args.get('isVerifiedSeller'))
        fair_price = bool(is_fair_price(sku, price))

        tx_hash = item.functions.listPhysicalGood(
            sku, 
            item_name,
            price,
            quantity,
            seller_id,
            is_verified_seller,
            fair_price).transact()

        w3.eth.waitForTransactionReceipt(tx_hash)

    return jsonify({'data': 'none'}), 200

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
            buyer_id,
            curr_time).transact()

        w3.eth.waitForTransactionReceipt(tx_hash)
    else:
        sku = request.args.get('sku')
        quantity = int(request.args.get('quantity'))
        buyer_id = request.args.get('buyerId')

        if is_hoarding(sku, buyer_id):
            return jsonify({'data': 'none'}), 200

        tx_hash = item.functions.buyPhysicalGood(
            sku,
            quantity,
            buyer_id,
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
