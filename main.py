import json
from web3 import Web3
from flask import Flask, request, jsonify

app = Flask(__name__)

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545')) # points to the URL provided by Ganache
w3.eth.defaultAccount = w3.eth.accounts[0]

# TODO: add code to connect to contracts

@app.route('/list', methods=['POST'])
def listing():
    # grab contract
    
    sku = request.args.get('sku')
    item_name = request.args.get('item_name')
    category = request.args.get('category')
    price = request.args.get('price')
    seller_id = request.args.get('seller_id')

    # pass information to solidity and get results

    return jsonify({'data': 'none'}), 200

@app.route('/buy', methods=['POST'])
def buy():
    # grab contract

    item_name = request.args.get('item_name')
    quantity = request.args.get('quantity')
    seller_id = request.args.get('seller_id')
    buyer_id = request.args.get('buyer_id')

    # pass information to solidity and get results

    return jsonify({'data': 'none'}), 200

@app.route('/show', methods=['GET'])
def show():
    # grab contract

    # pass information to solidity and get results
    
    return jsonify({'data': 'none'}), 200
