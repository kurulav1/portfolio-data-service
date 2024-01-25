from flask import Flask, jsonify, request
import yfinance as yf

app = Flask(__name__)

def fetch_treasury_yield(maturity='10y'):
    maturity_symbols = {
        '1m': '^IRX',  # 1 month
        '2y': '^FVX',  # 2 years
        '5y': '^FVX',  # 5 years
        '10y': '^TNX',  # 10 years
        '30y': '^TYX'  # 30 years
    }

    symbol = maturity_symbols.get(maturity, '^TNX')  # Default to 10-year if maturity not found
    history = yf.download(symbol, period='5d')

    if not history.empty:
        last_yield = history['Close'].iloc[-1]
        risk_free_rate = last_yield / 100
        return risk_free_rate
    else:
        return None


def fetch_option_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    exp_dates = ticker.options
    first_exp_date = exp_dates[0]
    options_data = ticker.option_chain(first_exp_date)

    relevant_data = []
    for i, exp_date in enumerate(exp_dates):
        if i >= 50:
            break

        for df in [options_data.calls, options_data.puts]:
            for _, row in df.iterrows():
                option_details = {
                    "stockOption": ticker_symbol,
                    "optionType": "call" if df is options_data.calls else "put",
                    "strikePrice": row['strike'],
                    "expirationDate": exp_date,
                    "marketPrice": row['lastPrice'],
                    "impliedVolatility": row['impliedVolatility'],  # Added implied volatility
                    "quantity": None,
                    "optionValue": None
                }
                relevant_data.append(option_details)

    return relevant_data

@app.route('/options/<ticker_symbol>')
def options(ticker_symbol):
    data = fetch_option_data(ticker_symbol.upper())
    return jsonify(data)

@app.route('/treasury_yield')
def treasury_yield_endpoint():
    maturity = request.args.get('maturity', '1m')  # Defaults to 10 years if not provided
    yield_data = fetch_treasury_yield(maturity)

    if yield_data is not None:
        return jsonify({"maturity": maturity, "treasury_yield": yield_data})
    else:
        return jsonify({"error": "Yield data not available for this maturity"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
