from datetime import datetime, timedelta
from decimal import Decimal
from db import delete_order, get_last_order, getAllBids, getAllOffers, getAllTrades, insert_order, insert_trade
from flask import Flask, request, jsonify, make_response
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
#app.run(use_reloader=False) # Needed because of scheduler running twice in debug mode
latest_trade_price = None
scheduler = None

schedulerInterval = 60 * 60 # in seconds

def init_price_scheduler(): 
    # fetch first price
    fetch_last_trade_price()

    # start scheduler for upcoming reloads
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=fetch_last_trade_price, trigger="interval", seconds=schedulerInterval)
    scheduler.start()
    current_time = datetime.now()
    scheduledTime = current_time + timedelta(seconds=schedulerInterval)
    print(f'Scheduler started at {current_time} and scheduled for {scheduledTime}')

def fetch_last_trade_price():
    global latest_trade_price
    url = "https://api.marketdata.app/v1/stocks/quotes/AAPL"
    response = requests.get(url)
    if response.status_code == 203 or response.status_code == 200:
        data = response.json()
        last_price = data.get("last")[0]  # Extracting the last traded price
        print(f'Last price fetched at {datetime.now()} and is {last_price}')
        latest_trade_price = last_price
        
init_price_scheduler()

@app.route('/')
def hello_group5():
    return 'Hello, group 5!\n Pipelines working!\n' + ' the price is currently ' + str(latest_trade_price)


@app.route('/order', methods=['POST'])
def order():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400

    order_type = request.json.get('type')
    price = request.json.get('price')
    quantity = request.json.get('quantity')

    if order_type not in ['Bid', 'Offer']:
        return jsonify({"error": "Invalid order type"}), 400

    if not priceValidation(price, latest_trade_price):
        return jsonify({"error": "Invalid price. Deviation exceeds allowed range"}), 400

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Invalid quantity"}), 400

    data = request.get_json()

    handleOrders(data)

    return jsonify({"message": "Order received", "type": order_type, "price": price, "quantity": quantity}), 201


@app.route('/trades')
def trades():
    try:
        results = getAllTrades()

        responseMessage = jsonify(results)

        response = make_response(responseMessage, 200)
        response.charset = "UTF-8"
        response.mimetype = "application/json"
        return response
    except Exception as error:
        print(f'General error when getting orders: {error}')
        response = make_response(jsonify(
            {'status': 'failure', 'message': f'General error when getting orders: {error}'}), 500)
        response.charset = "UTF-8"
        return response


@app.route('/offers')
def offers():
    try:
        results = getAllOffers()

        responseMessage = jsonify(results)

        response = make_response(responseMessage, 200)
        response.charset = "UTF-8"
        response.mimetype = "application/json"
        return response
    except Exception as error:
        print(f'General error when getting orders: {error}')
        response = make_response(jsonify(
            {'status': 'failure', 'message': f'General error when getting orders: {error}'}), 500)
        response.charset = "UTF-8"
        return response


@app.route('/bids')
def bids():
    try:
        results = getAllBids()

        responseMessage = jsonify(results)

        response = make_response(responseMessage, 200)
        response.charset = "UTF-8"
        response.mimetype = "application/json"
        return response
    except Exception as error:
        print(f'General error when getting orders: {error}')
        response = make_response(jsonify(
            {'status': 'failure', 'message': f'General error when getting orders: {error}'}), 500)
        response.charset = "UTF-8"
        return response


def priceValidation(tradeAskPrice, last_price):
    if last_price is None:
        print("Failed to fetch last traded price.")
        return False

    max_deviation = last_price * 0.10
    deviation = last_price - tradeAskPrice

    if abs(deviation) <= max_deviation:
        return True
    else:
        return False


def handleOrders(data):
    matching_Order = None
    data_dict = dict(data[0]) if isinstance(
        data, list) and len(data) > 0 else data

    data_price = Decimal(str(data_dict['price']))
    data_quantity = Decimal(str(data_dict['quantity']))

    if data_dict['type'] == "Bid":
        all_offers = getAllOffers()
        for offer in all_offers:
            if Decimal(str(offer['price'])) == data_price and Decimal(str(offer['quantity'])) == data_quantity:
                matching_Order = offer
                break
    else:
        all_bids = getAllBids()
        for bid in all_bids:
            if Decimal(str(bid['price'])) == data_price and Decimal(str(bid['quantity'])) == data_quantity:
                matching_Order = bid
                break

    if matching_Order:
        # Process the trade
        processTrade(matching_Order, data_price, data_quantity, data_dict['type'])
    else :
        # No match, save the offer
        orderId = insert_order(data)
        print(f'Order inserted with ID : {orderId}')


def processTrade(match, price, quantity, order_type):
    traded_time = datetime.now()
    print(f"Processing trade for {order_type}: ", traded_time, price, quantity)

    try:
        # Add trade to trade log
        insert_trade(traded_time, price, quantity)
        delete_order(match)
        print("Trade processed successfully")
    except Exception as e:
        print(f"Error processing trade: {e}")


atexit.register(lambda: scheduler.shutdown() if scheduler else print('Scheduler not defined, closing'))
