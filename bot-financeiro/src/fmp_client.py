import os
from dotenv import load_dotenv
import requests


load_dotenv()

key=os.getenv("FMP_API_KEY")

incomestatementurl=f"https://financialmodelingprep.com/stable/income-statement?symbol=AAPL&apikey={key}"

incomestatement=requests.get(incomestatementurl)

dataincomestatement=incomestatement.json()

#print(dataincomestatement)



balancesheeturl=f"https://financialmodelingprep.com/stable/balance-sheet-statement?symbol=AAPL&apikey={key}"

balancesheet=requests.get(balancesheeturl)

databalancesheet=balancesheet.json()

#print(databalancesheet)


marketurl=f"https://financialmodelingprep.com/stable/market-capitalization-batch?symbols=AAPL,MSFT,GOOG&apikey={key}"

market=requests.get(marketurl)

datamarket=market.json()

#print(datamarket)

url_dividendos = f"https://financialmodelingprep.com/stable/dividends?symbol=AAPL&apikey={key}"
resultado_dividendos = requests.get(url_dividendos).json()
#print(resultado_dividendos)

url_screener = f"https://financialmodelingprep.com/stable/company-screener?industry=Software - Application&limit=20&apikey={key}"
resposta_screener = requests.get(url_screener)
print(resposta_screener.status_code)
print(resposta_screener.text)

