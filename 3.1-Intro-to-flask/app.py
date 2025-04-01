from fastapi import FastAPI, HTTPException, Query
import yfinance as yf
from pydantic import BaseModel
from datetime import date
from typing import List
import uvicorn

app = FastAPI()


class HistoricalDataRequest(BaseModel):
    symbol: str
    start_date: date
    end_date: date


# 1. Company Information Endpoint
@app.get("/company/{symbol}")
def get_company_info(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
    except:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "name": info.get("longName"),
        "summary": info.get("longBusinessSummary"),
        "industry": info.get("industry"),
        "sector": info.get("sector"),
        "officers": info.get("companyOfficers", [])
    }


# 2. Stock Market Data Endpoint
@app.get("/market/{symbol}")
def get_stock_market_data(symbol: str):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    if data.empty:
        raise HTTPException(status_code=404, detail="Stock data not available")
    return {
        "market_price": data["Close"].iloc[-1],
        "price_change": data["Close"].iloc[-1] - data["Open"].iloc[-1],
        "percentage_change": ((data["Close"].iloc[-1] - data["Open"].iloc[-1]) / data["Open"].iloc[-1]) * 100,
    }


# 3. Historical Market Data Endpoint
@app.post("/historical/")
def get_historical_data(request: HistoricalDataRequest):
    stock = yf.Ticker(request.symbol)
    data = stock.history(start=request.start_date, end=request.end_date)
    if data.empty:
        raise HTTPException(status_code=404, detail="Historical data not found")
    return data.to_dict()


# 4. Analytical Insights Endpoint
@app.post("/analysis/")
def get_analytical_insights(request: HistoricalDataRequest):
    stock = yf.Ticker(request.symbol)
    data = stock.history(start=request.start_date, end=request.end_date)
    if data.empty:
        raise HTTPException(status_code=404, detail="No data for analysis")

    avg_price = data['Close'].mean()
    volatility = data['Close'].std()
    trend = "Bullish" if data['Close'].iloc[-1] > data['Close'].iloc[0] else "Bearish"

    return {
        "average_price": avg_price,
        "volatility": volatility,
        "trend": trend
    }
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)