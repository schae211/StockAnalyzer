Title: Readme for StockAnalyzer Application:
Description:
This application allows the use to query stock symbols to get
    1. the latest price
    2. a graph of the stocks performance in the given time frame.
As few people know stock symbols, a search functionality is implemented
(using the AlphaVantage Search Endpoint) which allows the user to search
for symbols by typing in the company name

How to use the application:
The Application is based on the AlphaVantage API, therefore a user needs to claim a free API KEY,
which has to be stored in an env. file for this application

Getting Stock Information:
1. Enter Stock Symbol:
    a) Non-US ticker symbols need a suffix according to the country or trade exchange
    b) Example: .DE for germany -> BAYN.DE for Bayer AG, .SWI for switzerland -> NESN.SWI for Nestle S.A.
    c) Symbols for many American and European Stocks are saved in the symbols_2.txt file
     which is fed to the PyQt-Completer (S&P500, XETRA prime standard, FTSE100, CAC40, FTSE MIB, SMI)
    d)List of suffix: Germany: .DE; Great_Britain: .LON, Switzerland: .SWI, France: .PA, Italy: .MIL

2. Following information can be obtained:
    a) Full (legal) name of the company
    b) Latest Price of the stock
    c) Currency in which the stock is listed/traded
    d) When the latest Price b) was updated
    e) Region

3. Displaying stocks performance in a plot
    a) Enter the start date (historical data are available starting from 2000)
    b) Enter the end date (latest date is current date -> cannot predict the future unfortunately)
    c) Change in percent is shown in the box below the graph

4. Searching for Stock Symbols:
    a) Click Search -> Ticker Symbols or shortcut "Ctrl+F"
    b) Enter Query into search field and hit Enter or push "Search" button


