from flask import Flask, jsonify, request
from datetime import datetime, timedelta
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


def fetch_option_data(ticker_symbol, start_date=None, end_date=None):
    ticker = yf.Ticker(ticker_symbol)
    exp_dates = ticker.options

    # Initialize start_date and end_date only if they are valid date strings
    if start_date and start_date != 'undefined':
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = datetime.today()

    if end_date and end_date != 'undefined':
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = start_date + timedelta(days=30)

    # Filter expiration dates within the specified range
    filtered_exp_dates = [date for date in exp_dates if start_date <= datetime.strptime(date, '%Y-%m-%d') <= end_date]

    relevant_data = []
    for exp_date in filtered_exp_dates:
        options_data = ticker.option_chain(exp_date)
        for df in [options_data.calls, options_data.puts]:
            for _, row in df.iterrows():
                option_details = {
                    "stockOption": ticker_symbol,
                    "optionType": "call" if df is options_data.calls else "put",
                    "strikePrice": row['strike'],
                    "expirationDate": exp_date,
                    "marketPrice": row['lastPrice'],
                    "impliedVolatility": row['impliedVolatility'],
                    "quantity": None,
                    "optionValue": None
                }
                relevant_data.append(option_details)

    return relevant_data

@app.route('/options/<ticker_symbol>')
def options(ticker_symbol):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    print("Start Date:", start_date)
    print("End Date:", end_date)

    data = fetch_option_data(ticker_symbol.upper(), start_date=start_date, end_date=end_date)
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
