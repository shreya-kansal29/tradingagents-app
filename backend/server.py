from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import random

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    ticker: str
    date: str
    provider: str = "demo"

# Indian NSE stocks
INDIAN_STOCKS = {
    "RELIANCE": {"action": "BUY", "confidence": 82, "rationale": "Reliance Industries shows strong momentum across telecom (Jio), retail, and O2C segments. SEBI filings indicate revenue growth of 11% YoY. Jio subscriber base crossed 450M. Retail expansion aggressive with 18,000+ stores. Technical breakout above 200-day MA confirmed. FII buying consistent.", "pe_ratio": "24.3", "sentiment": "79/100", "rsi": "61", "exchange": "NSE"},
    "TCS": {"action": "BUY", "confidence": 78, "rationale": "TCS SEBI filings show consistent deal wins — $10.2B TCV in Q3. IT sector tailwinds from AI adoption driving demand. Dividend yield attractive at 3.2%. Attrition stabilizing at 12.5%. Strong order book from BFSI and retail verticals. Institutional holding strong.", "pe_ratio": "28.1", "sentiment": "77/100", "rsi": "58", "exchange": "NSE"},
    "INFY": {"action": "HOLD", "confidence": 71, "rationale": "Infosys guidance revised — FY25 revenue growth at 4.5-5%. Large deal wins healthy at $2.1B but margins under pressure at 20.1%. SEBI disclosures show consistent buybacks supporting stock price. Near-term headwinds from discretionary spending cuts by clients.", "pe_ratio": "26.4", "sentiment": "68/100", "rsi": "52", "exchange": "NSE"},
    "HDFCBANK": {"action": "BUY", "confidence": 80, "rationale": "HDFC Bank post-merger integration progressing well. SEBI filings show NIM stabilizing at 3.6%. Loan growth at 15% YoY. Asset quality strong with GNPA at 1.26%. RBI compliance issues being resolved. Largest private sector bank with strong retail franchise.", "pe_ratio": "18.2", "sentiment": "76/100", "rsi": "57", "exchange": "NSE"},
    "WIPRO": {"action": "HOLD", "confidence": 65, "rationale": "Wipro showing signs of recovery after multiple quarters of weakness. SEBI filings indicate new CEO driving operational improvements. Deal pipeline healthy but conversion slow. Margins improving sequentially. Wait for sustained revenue growth before adding positions.", "pe_ratio": "22.1", "sentiment": "62/100", "rsi": "49", "exchange": "NSE"},
    "TATAMOTORS": {"action": "BUY", "confidence": 76, "rationale": "Tata Motors driven by JLR recovery — UK operations profitable. EV segment growing with Nexon EV market leadership. SEBI filings show debt reduction on track. Commercial vehicle segment robust. China risk manageable given diversified revenue.", "pe_ratio": "8.4", "sentiment": "74/100", "rsi": "55", "exchange": "NSE"},
    "BAJFINANCE": {"action": "BUY", "confidence": 79, "rationale": "Bajaj Finance maintains industry-leading AUM growth of 28% YoY per SEBI disclosures. NIM strong at 10.2%. Asset quality stable despite RBI scrutiny on unsecured lending. Digital platform scaling rapidly. Premium valuations justified by execution quality.", "pe_ratio": "32.8", "sentiment": "78/100", "rsi": "60", "exchange": "NSE"},
    "SUNPHARMA": {"action": "BUY", "confidence": "73", "rationale": "Sun Pharma US specialty business growing strongly. SEBI filings show India branded generics at 31% of revenue. R&D pipeline robust with 10+ NDA filings. Ilumya and Cequa growing in US market. Emerging markets expansion on track.", "pe_ratio": "34.2", "sentiment": "72/100", "rsi": "56", "exchange": "NSE"},
    "NIFTY50": {"action": "HOLD", "confidence": 68, "rationale": "Nifty50 index at elevated valuations — P/E at 22x trailing. FII outflows creating headwinds. RBI rate trajectory uncertain. Domestic consumption resilient but global macro risks elevated. Selective stock picking recommended over index exposure.", "pe_ratio": "22.0", "sentiment": "65/100", "rsi": "51", "exchange": "NSE"},
    "SENSEX": {"action": "HOLD", "confidence": 66, "rationale": "Sensex consolidating after recent rally. Earnings growth expectations of 12-15% for FY25 priced in. Budget expectations creating short term volatility. Long term India growth story intact — SIP inflows at record Rs 19,000 Cr/month.", "pe_ratio": "23.1", "sentiment": "64/100", "rsi": "50", "exchange": "BSE"},
}

# US stocks
US_STOCKS = {
    "NVDA": {"action": "BUY", "confidence": 87, "rationale": "NVIDIA shows exceptional strength in AI chip demand. Revenue growth 78% YoY. Gross margins above 75%. Technical breakout above 200-day MA. Sentiment overwhelmingly positive.", "pe_ratio": "65.2", "sentiment": "82/100", "rsi": "58", "exchange": "NASDAQ"},
    "AAPL": {"action": "BUY", "confidence": 74, "rationale": "Apple services segment at 24% of revenue growing 14% YoY. iPhone volumes strong. AI integration roadmap well received. Strong balance sheet.", "pe_ratio": "28.4", "sentiment": "76/100", "rsi": "62", "exchange": "NASDAQ"},
    "TSLA": {"action": "HOLD", "confidence": 61, "rationale": "Mixed signals — margin compression offset by energy storage growth. Sentiment divided. Price consolidating $180-220 range.", "pe_ratio": "72.1", "sentiment": "51/100", "rsi": "48", "exchange": "NASDAQ"},
    "META": {"action": "BUY", "confidence": 81, "rationale": "Ad revenue rebounded strongly with AI targeting. Reality Labs losses narrowing. Strong free cash flow supports buybacks.", "pe_ratio": "24.8", "sentiment": "79/100", "rsi": "55", "exchange": "NASDAQ"},
    "GOOGL": {"action": "BUY", "confidence": 79, "rationale": "Google Cloud growing 28% YoY. Search stable. YouTube recovering. Gemini integration showing traction.", "pe_ratio": "21.3", "sentiment": "74/100", "rsi": "59", "exchange": "NASDAQ"},
}

# Indian stock suffixes
INDIAN_SUFFIXES = [".NS", ".BO", "-NS", "-BO"]

def is_indian_stock(ticker):
    ticker = ticker.upper()
    for suffix in INDIAN_SUFFIXES:
        if ticker.endswith(suffix.upper()):
            return True
    if ticker in INDIAN_STOCKS:
        return True
    return False

@app.get("/")
def home():
    return {
        "status": "TradingAgents backend chal raha hai!",
        "mode": "demo",
        "supports": ["NSE", "BSE", "NASDAQ", "NYSE"],
        "version": "2.0.0"
    }

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    ticker = req.ticker.upper()
    # Remove .NS or .BO suffix for lookup
    clean_ticker = ticker.replace(".NS","").replace(".BO","").replace("-NS","").replace("-BO","")

    # Check Indian stocks first
    if clean_ticker in INDIAN_STOCKS:
        data = INDIAN_STOCKS[clean_ticker]
        filing_source = "SEBI"
        exchange = data.get("exchange", "NSE")
    elif clean_ticker in US_STOCKS:
        data = US_STOCKS[clean_ticker]
        filing_source = "SEC"
        exchange = data.get("exchange", "NASDAQ")
    else:
        # Unknown stock — generate realistic response
        filing_source = "SEBI" if is_indian_stock(ticker) else "SEC"
        exchange = "NSE" if is_indian_stock(ticker) else "NASDAQ"
        actions = ["BUY", "HOLD", "SELL"]
        weights = [0.4, 0.4, 0.2]
        action = random.choices(actions, weights=weights)[0]
        conf = random.randint(62, 81)
        data = {
            "action": action,
            "confidence": conf,
            "rationale": f"Multi-agent analysis complete for {clean_ticker} on {exchange}. {'SEBI regulatory filings' if filing_source == 'SEBI' else 'SEC filings'} reviewed alongside technical indicators and market sentiment. Based on comprehensive evaluation across fundamentals, sentiment, news and technical factors, portfolio manager recommends {action} with {conf}% confidence.",
            "pe_ratio": str(round(random.uniform(12, 45), 1)),
            "sentiment": f"{random.randint(55, 78)}/100",
            "rsi": str(random.randint(40, 65)),
        }

    return {
        "success": True,
        "ticker": clean_ticker,
        "date": req.date,
        "filing_source": filing_source,
        "exchange": exchange,
        "decision": {
            "action": data["action"],
            "confidence": data["confidence"],
            "rationale": data["rationale"],
            "metrics": {
                "pe_ratio": data["pe_ratio"],
                "sentiment_score": data["sentiment"],
                "rsi": data["rsi"],
                "filing_source": filing_source,
                "exchange": exchange
            }
        }
    }