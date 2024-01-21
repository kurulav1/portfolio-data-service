from flask import Flask, jsonify
import yfinance as yf

app = Flask(__name__)

def fetch_option_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    exp_dates = ticker.options
    first_exp_date = exp_dates[0]
    options_data = ticker.option_chain(first_exp_date)

    relevant_data = []

    for df in [options_data.calls, options_data.puts]:
        for _, row in df.iterrows():
            option_details = {
                "stockOption": ticker_symbol,
                "optionType": "call" if df is options_data.calls else "put",
                "strikePrice": row['strike'],
                "expirationDate": first_exp_date,
                "marketPrice": row['lastPrice'],
                "quantity": None,
                "optionValue": None
            }
            relevant_data.append(option_details)

    return relevant_data

@app.route('/options/<ticker_symbol>')
def options(ticker_symbol):
    data = fetch_option_data(ticker_symbol.upper())
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
