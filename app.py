from flask import Flask, request, jsonify
import alpaca_trade_api as tradeapi
import os

app = Flask(__name__)

API_KEY = os.environ['ALPACA_API_KEY']
SECRET_KEY = os.environ['ALPACA_SECRET_KEY']
BASE_URL = 'https://paper-api.alpaca.markets'  # Use live version later

api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received alert:", data)

    symbol = data.get('symbol')
    action = data.get('action')
    amount = float(data.get('amount', 100))

    try:
        if action == 'buy':
            api.submit_order(
                symbol=symbol,
                notional=amount,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
            return jsonify({"message": f"BUY ${amount} of {symbol} submitted."})

        elif action == 'sell':
            position = api.get_position(symbol)
            qty = position.qty
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
            return jsonify({"message": f"SOLD all ({qty}) shares of {symbol}."})

        else:
            return jsonify({"error": "Invalid action"}), 400

    except tradeapi.rest.APIError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(port=5000)
