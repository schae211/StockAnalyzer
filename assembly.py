import os
from dotenv import load_dotenv, find_dotenv
import requests
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import csv
from datetime import datetime
from datetime import timedelta

# Find and insert the API KEY ("hiding the API KEY"), 2 different keys for main window and search engine
load_dotenv(find_dotenv())
API_KEY = os.environ.get('OPX_KEY')
IPA_KEY = os.environ.get('QTW_KEY')

def get_day_difference(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    return (end - start).days

def get_graph(symbol, start, end):
    """Function returns a list of all closure prices for a stock (symbol) in the given time frame (start, end)"""
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    difference = (end - start).days
    start = datetime.strftime(start, "%Y-%m-%d")
    end = datetime.strftime(end, "%Y-%m-%d")

    prices = []

    if difference <= 140:
        # Get the json for Times Series Daily Adjusted
        r = requests.get(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={API_KEY}"
        )
        # Catch error if json does not exist
        if "Error Message" in r.json():  # A new way to handle Errors, so I do not have to use try, except!
            print("Symbol does not exist")  # r.json form AlphaVantage contains an "Error Message" I can catch
            return [0]
        elif "Note" in r.json():
            print("API call limit exceeded")
            return [0]
        n = 0
        while n < difference:
            try:
                prices.append(float(r.json()['Time Series (Daily)'][start]['5. adjusted close']))   # Append closure price
            except KeyError:    # Ignoring the KeyError of Non-Trading Days
                pass
            start = datetime.strptime(start, "%Y-%m-%d")    # Change format so I can add a day
            start += timedelta(days=1)                      # Add day
            start = datetime.strftime(start, "%Y-%m-%d")    # Change back format so api can interpret properly
            n += 1
        return prices
    else:
        # Get the json for Times Series Weekly Adjusted
        r = requests.get(
            f"https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={API_KEY}"
        )
        # Catch error if json does not exist
        if "Error Message" in r.json():  # A new way to handle Errors, so I do not have to use try, except!
            print("Symbol does not exist")  # r.json form AlphaVantage contains an "Error Message" I can catch
            return [0]
        elif "Note" in r.json():
            print("API call limit exceeded")
            return [0]
        n = 0
        while n < difference:
            try:
                prices.append(
                    float(r.json()['Weekly Adjusted Time Series'][start]['5. adjusted close']))  # Append closure price
                start = datetime.strptime(start, "%Y-%m-%d")  # Change format so I can add a day
                start += timedelta(days=7)  # Add 7 days to get the value for the next week!
                start = datetime.strftime(start, "%Y-%m-%d")  # Change back format so api can interpret properly
                n += 7  # Adding 7 days to the day counter n
            except KeyError:  # Ignoring the KeyError of Non-Trading Days
                start = datetime.strptime(start, "%Y-%m-%d")  # Change format so I can add a day
                start += timedelta(days=1)  # Add one single day to catch beginning of the week
                start = datetime.strftime(start, "%Y-%m-%d")  # Change back format so api can interpret properly
                n += 1  # Adding 1 day to the day counter n
                pass
        return prices

def get_infos(symbol):
    """Function returns a dictionary with all the important information"""
    # Changed to demo right now!
    r_general = requests.get(
        f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={symbol}&apikey={API_KEY}"
    )
    r_price = requests.get(
        f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    )
    # Catch the errors in both requests:
    if "Error Message" in r_general.json() or "Error Message" in r_price.json():
        return {
            "name": "NA",
            "price": "NA",
            "currency": "NA",
            "updated": "NA",
            "region": "NA",
            "error message": "Ticker Symbol not found!"
        }
    elif r_general.json()['bestMatches'] == []:
        return {
            "name": "NA",
            "price": "NA",
            "currency": "NA",
            "updated": "NA",
            "region": "NA",
            "error message": "Ticker Symbol not found!"
        }
    elif "Note" in r_general.json() or "Note" in r_price.json():
        return {
            "name": "NA",
            "price": "NA",
            "currency": "NA",
            "updated": "NA",
            "region": "NA",
            "error message": "AlphaVantage API Call frequency exceeded!"
        }
    else:
        return {
            "name": r_general.json()['bestMatches'][0]['2. name'],
            "price": round(float(r_price.json()['Global Quote']['05. price']), 2),
            "currency": r_general.json()['bestMatches'][0]['8. currency'],
            "updated": r_price.json()['Global Quote']['07. latest trading day'],
            "region": r_general.json()['bestMatches'][0]['4. region'],
            "error message": ""
        }

def get_search_results(keyword):
    """Function returns a dictionary with all the important information"""
    # Changed to demo right now!
    r = requests.get(
        f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={keyword}&apikey={IPA_KEY}"
    )
    return_list = []
    # Catch the errors in both requests:
    if "Error Message" in r.json():
        return return_list
    elif r.json()['bestMatches'] == []:
        return return_list
    elif "Note" in r.json():
        return return_list
    else:
        for i in range(5):
            row_list = []
            try:
                row_list.append(r.json()['bestMatches'][i]['9. matchScore'])
                row_list.append(r.json()['bestMatches'][i]['2. name'])
                row_list.append(r.json()['bestMatches'][i]['4. region'])
                row_list.append(r.json()['bestMatches'][i]['3. type'])
                row_list.append(r.json()['bestMatches'][i]['1. symbol'])
                # Important to catch IndexErrors as well
            except (KeyError, IndexError):
                break
            return_list.append(row_list)
        return return_list

# Search Window
class Ui_SearchWindow(object):
    def setupUi(self, SearchWindow):
        SearchWindow.setObjectName("SearchWindow")
        SearchWindow.resize(1450, 800)
        SearchWindow.setWindowIcon(QtGui.QIcon('magnifying_glass.png'))
        self.centralwidget = QtWidgets.QWidget(SearchWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(50, 50, 1350, 700))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_description = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label_description.setFont(font)
        self.label_description.setAlignment(QtCore.Qt.AlignCenter)
        self.label_description.setWordWrap(False)
        self.label_description.setObjectName("label_description")
        self.verticalLayout.addWidget(self.label_description)
        self.lineEdit_keyword = QtWidgets.QLineEdit(self.widget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.lineEdit_keyword.setFont(font)
        self.lineEdit_keyword.setObjectName("lineEdit_keyword")
        self.verticalLayout.addWidget(self.lineEdit_keyword)
        self.pushButton_search = QtWidgets.QPushButton(self.widget)
        self.pushButton_search.setObjectName("pushButton_search")
        self.verticalLayout.addWidget(self.pushButton_search)
        self.line = QtWidgets.QFrame(self.widget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.tableWidget_display = QtWidgets.QTableWidget(self.widget)
        self.tableWidget_display.setColumnCount(5)
        self.tableWidget_display.setObjectName("tableWidget_display")
        # Set the column headers
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_display.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_display.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_display.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_display.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_display.setHorizontalHeaderItem(4, item)
        # Set the columns widths
        self.tableWidget_display.setColumnWidth(0, 200)
        self.tableWidget_display.setColumnWidth(1, 500)
        self.tableWidget_display.setColumnWidth(2, 200)
        self.tableWidget_display.setColumnWidth(3, 200)
        self.tableWidget_display.setColumnWidth(4, 200)
        # Add table to the Layout
        self.verticalLayout.addWidget(self.tableWidget_display)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout.addLayout(self.verticalLayout_2)
        SearchWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(SearchWindow)
        QtCore.QMetaObject.connectSlotsByName(SearchWindow)

    def retranslateUi(self, SearchWindow):
        _translate = QtCore.QCoreApplication.translate
        SearchWindow.setWindowTitle(_translate("SearchWindow", "Ticker Symbol Search"))
        self.label_description.setText(_translate("SearchWindow", "AlphaVantage Search Engine:"))
        self.pushButton_search.setText(_translate("SearchWindow", "Search"))
        item = self.tableWidget_display.horizontalHeaderItem(0)
        item.setText(_translate("SearchWindow", "Match_Score"))
        item = self.tableWidget_display.horizontalHeaderItem(1)
        item.setText(_translate("SearchWindow", "Name"))
        item = self.tableWidget_display.horizontalHeaderItem(2)
        item.setText(_translate("SearchWindow", "Region"))
        item = self.tableWidget_display.horizontalHeaderItem(3)
        item.setText(_translate("SearchWindow", "Type"))
        item = self.tableWidget_display.horizontalHeaderItem(4)
        item.setText(_translate("SearchWindow", "Symbol"))
        self.pushButton_search.setShortcut(_translate("MainWindow", "Return"))

        # Call the search_button when the search button is clicked
        self.pushButton_search.clicked.connect(lambda: self.search_button(self.lineEdit_keyword.text()))

    # Method calls the get_search_results function and inserts data into the table
    def search_button(self, keyword):
        self.tableWidget_display.setRowCount(0)
        list_list = get_search_results(keyword)
        list_length = len(list_list)
        self.tableWidget_display.setRowCount(list_length)
        for i in range(list_length):
            for j in range(5):
                self.tableWidget_display.setItem(i,j, QtWidgets.QTableWidgetItem(str(list_list[i][j])))


ticker_list = []
with open("symbols_2.txt", "r") as file:
    csvreader = csv.reader(file, delimiter=",")
    for row in csvreader:
        for ticker in row:
            ticker_list.append(ticker.strip())

# Main Window which is started up when I run the application
class Ui_MainWindow(object):
    """Main Window class"""

    def setupUi(self, MainWindow):
        # Options regarding the main window:
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 800)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        # Setting the WindowIcon to a chart symbol
        MainWindow.setWindowIcon(QtGui.QIcon('chart.png'))
        # Setting up the central widget, which contains everything else
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(50, 50, 1400, 600))
        self.widget.setObjectName("widget")
        # horizontalLayout_3 (contains everything again -> aligning left and right box)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        # verticalLayout (big box on the left)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        # Setting up the "Enter Stock Quote" label (label_description)
        self.label_description = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        self.label_description.setFont(font)
        self.label_description.setAlignment(QtCore.Qt.AlignCenter)
        self.label_description.setObjectName("label_description")
        self.verticalLayout.addWidget(self.label_description)

        # Setting up the text-line field to enter Stock Symbol -> Make Search field here!
        self.lineEdit_quote = QtWidgets.QLineEdit(self.widget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lineEdit_quote.setFont(font)
        self.lineEdit_quote.setObjectName("lineEdit_quote")

        # self.completer uses a list of US, GER stocks at the moment derived from txt field mentioned above
        self.completer = QtWidgets.QCompleter(ticker_list)                      # completer uses ticker_list
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)            # Case insensitive
        self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)  # Styling
        self.lineEdit_quote.setCompleter(self.completer)                        # Set completer so it bleongs to lineEdit
        self.verticalLayout.addWidget(self.lineEdit_quote)

        # Setting up the "Get Quote" Button
        self.pushButton_quote = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.pushButton_quote.setFont(font)
        self.pushButton_quote.setObjectName("pushButton_quote")
        self.verticalLayout.addWidget(self.pushButton_quote)

        # Setting up the result labels:
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label_name = QtWidgets.QLabel(self.widget)
        self.label_name.setObjectName("label_name")
        self.label_name.setFont(font)
        self.label_name.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.label_name)
        self.label_price = QtWidgets.QLabel(self.widget)
        self.label_price.setObjectName("label_price")
        self.label_price.setFont(font)
        self.label_price.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.label_price)
        self.label_cur = QtWidgets.QLabel(self.widget)
        self.label_cur.setObjectName("label_cur")
        self.label_cur  .setFont(font)
        self.label_cur.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.label_cur)
        self.label_updated = QtWidgets.QLabel(self.widget)
        self.label_updated.setObjectName("label_updated")
        self.label_updated.setFont(font)
        self.label_updated.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.label_updated)
        self.label_region = QtWidgets.QLabel(self.widget)
        self.label_region.setObjectName("label_region")
        self.label_region.setFont(font)
        self.label_region.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.label_region)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        # Adding the verticalLayout (left big box) to the horizontalLayout_3
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        # Adding a line between both sides of the application
        self.line = QtWidgets.QFrame(self.widget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_3.addWidget(self.line)

        # Setting up the verticalLayout_3 (right big box)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        # Adding the graphWidget (object of class PlotWidget) + Personalizing
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.graphWidget = pg.PlotWidget(self.widget)
        self.graphWidget.setObjectName("graphWidget")
        self.graphWidget.setLabel("bottom", text="Trading Days")
        self.graphWidget.setLabel("left", text="Price")
        self.verticalLayout_3.addWidget(self.graphWidget)
        # Setting up verticalLayout_2 (righter lower box)
        # and horizontalLayout_2 (top box of that box containing "From/To" Labels
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        # Add "From:" and "To" Labels
        self.label_start = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        self.label_start.setFont(font)
        self.label_start.setAlignment(QtCore.Qt.AlignLeft)
        self.label_start.setObjectName("label_start")
        self.horizontalLayout_2.addWidget(self.label_start)
        self.label_end = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        self.label_end.setFont(font)
        self.label_end.setAlignment(QtCore.Qt.AlignLeft)
        self.label_end.setObjectName("label_end")
        self.horizontalLayout_2.addWidget(self.label_end)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        # dateEdit start
        self.dateEdit_start = QtWidgets.QDateEdit(self.widget)
        self.dateEdit_start.setObjectName("dateEdit_start")
        self.dateEdit_start.setDate(QtCore.QDate(2000, 1, 1))                      # Setting the default Date to 2000
        self.dateEdit_start.setMinimumDate(QtCore.QDate(2000, 1, 1))               # Setting the minimum Date to 2000
        self.horizontalLayout.addWidget(self.dateEdit_start)

        # Change Label in between:
        self.label_change = QtWidgets.QLabel(self.widget)
        self.label_change.setAlignment(QtCore.Qt.AlignCenter)
        self.label_change.setObjectName("label_change")
        self.label_change.setMaximumWidth(150)
        self.label_change.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.horizontalLayout.addWidget(self.label_change)

        # dateEdit end:
        self.dateEdit_end = QtWidgets.QDateEdit(self.widget)
        self.dateEdit_end.setObjectName("dateEdit_end")
        self.dateEdit_end.setDateTime(QtCore.QDateTime.currentDateTime())           # Setting default Date to current Date
        self.dateEdit_end.setMaximumDateTime(QtCore.QDateTime.currentDateTime())    # Setting maximum to current Date

        self.horizontalLayout.addWidget(self.dateEdit_end)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)

        # Get graph PushButton
        self.pushButton_graph = QtWidgets.QPushButton(self.widget)
        self.pushButton_graph.setObjectName("pushButton_graph")
        self.verticalLayout_2.addWidget(self.pushButton_graph)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)

        # Adding the menu bar which has no functionality as of right now.
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 508, 20))
        self.menubar.setObjectName("menubar")
        # Adding the "top buttons"
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuOptions = QtWidgets.QMenu(self.menubar)
        self.menuOptions.setObjectName("menuOptions")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuSearch = QtWidgets.QMenu(self.menubar)
        self.menuSearch.setObjectName("menuSearch")
        MainWindow.setMenuBar(self.menubar)
        # Adding the "sub buttons" e.g. Readme
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionReadme = QtWidgets.QAction(MainWindow)
        self.actionReadme.setShortcut("Ctrl+R")
        self.actionReadme.setObjectName("actionReadme")
        self.menuHelp.addAction(self.actionReadme)
        self.actionTickers = QtWidgets.QAction(MainWindow)
        self.actionTickers.setShortcut("Ctrl+F")
        self.actionTickers.setObjectName("actionTickers")
        self.menuSearch.addAction(self.actionTickers)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menubar.addAction(self.menuSearch.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        # Setting the name of my main window to "StockAnalyzer"
        MainWindow.setWindowTitle(_translate("MainWindow", "StockAnalyzer"))
        # Adding the texts and well as the placeholder for the lineEdit type box
        self.label_description.setText(_translate("MainWindow", "Enter Stock Symbol:"))
        self.lineEdit_quote.setPlaceholderText(_translate("MainWindow", "AAPL"))
        self.pushButton_quote.setText(_translate("MainWindow", "Get Information:"))
        # Adding the "Return" as shortcut -> basically get quote by pressing Enter
        self.pushButton_quote.setShortcut(_translate("MainWindow", "Return"))

        # Adding the rest of the text
        self.label_name.setText(_translate("MainWindow", "Full name"))
        self.label_price.setText(_translate("MainWindow", "Price"))
        self.label_cur.setText(_translate("MainWindow", "Currency"))
        self.label_updated.setText(_translate("MainWindow", "Updated"))
        self.label_region.setText(_translate("MainWindow", "Region"))

        self.label_start.setText(_translate("MainWindow", "        From:"))
        self.label_change.setText(_translate("MainWindow", "± %"))
        self.label_end.setText(_translate("MainWindow", "                   To:"))
        self.pushButton_graph.setText(_translate("MainWindow", "Get Graph"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuOptions.setTitle(_translate("MainWindow", "Options"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionReadme.setText(_translate("MainWindow", "Readme"))
        self.actionTickers.setText(_translate("MainWindow", "Ticker Symbols"))
        self.menuSearch.setTitle(_translate("MainWindow", "Search"))

        # Calling the method clicked_quote (defined below) once the pushButton_quote is pressed
        # arguments (symbol got form lineEdit) for the method have to be passed using a lambda (one line function) why?
        self.pushButton_quote.clicked.connect(lambda: self.clicked_quote(symbol=self.lineEdit_quote.text()))

        # Calling the method clicked_graph (defined below) once the pushButton_graph is pressed
        # Important to use the toPyDate method as it converts a date into a suitable format, which is not a string!
        self.pushButton_graph.clicked.connect(lambda: self.clicked_graph(
            self.lineEdit_quote.text(), str(self.dateEdit_start.date().toPyDate()),
            str(self.dateEdit_end.date().toPyDate())))

        # Calling the Readme method
        self.actionReadme.triggered.connect(lambda: self.readme())

        # Calling the Search Box
        self.actionTickers.triggered.connect(lambda: self.search())

    def readme(self):
        os.system('start readme.txt')


    def search(self):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_SearchWindow()
        self.ui.setupUi(self.window)
        self.window.show()


    def clicked_quote(self, symbol):
        response = get_infos(symbol)
        self.label_name.setText(f" Company: {response['name']}")
        self.label_name.adjustSize()
        self.label_price.setText(f"Price: {str(response['price'])}")
        self.label_price.adjustSize()
        self.label_cur.setText(f" Currency: {response['currency']}")
        self.label_cur.adjustSize()
        self.label_updated.setText(f" Updated: {response['updated']}")
        self.label_updated.adjustSize()
        self.label_region.setText(f" Region: {response['region']}")
        self.label_region.adjustSize()
        # Displaying a warning if API call frequency is exceeded or the symbol cannot be found!
        # Important to pass MainWindow as argument, since window does not come from ui window!
        if response['error message'] != "":
            warning = QtWidgets.QMessageBox.warning(MainWindow, "Warning", response['error message'])


    # Method which plots a list (just x values!) into the graphWidget in colour red (called when button is pressed)
    # Clear="True" clears all plots before displaying new plot
    def clicked_graph(self, symbol, start, end):
        # Adjusting whether days or weeks are displayed (days = default)
        if get_day_difference(start, end) > 140:
            self.graphWidget.setLabel("bottom", text="Trading Weeks")
        graph_list = get_graph(symbol, start, end)
        if graph_list == [0]:
            warning = QtWidgets.QMessageBox.warning(MainWindow, "Warning", "API call limit exceeded ")
        else:
            change_percent = round((graph_list[-1] - graph_list[0])/graph_list[0]*100, 2)
            self.graphWidget.plot(graph_list, pen="r", clear="True")
            self.graphWidget.showGrid(x=True, y=True)
            self.label_change.setText(f"{str(change_percent)} %")

# Starting up the Application + ensuring that it is closed properly!
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
