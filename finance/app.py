import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
db.execute("CREATE TABLE IF NOT EXISTS 'transactions' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'user_id' INTEGER, 'symbol' TEXT, 'shares' INTEGER, 'price' NUMERIC, 'time' DATETIME);")
db.execute("CREATE TABLE IF NOT EXISTS 'shares' ('id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 'user_id' INTEGER, 'symbol' TEXT, 'shares' INTEGER, 'price' NUMERIC, 'time' DATETIME);")


# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Get user id from session
    user_id = session["user_id"]

    sharesdb = db.execute("SELECT symbol, shares FROM shares WHERE user_id = ?", user_id)
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]['cash']

    # Update dictionary sharesdb for full name and price of share and count sum of all assets
    sum = 0
    for i in range(len(sharesdb)):
        dictmp = lookup(sharesdb[i]['symbol'])
        name = dictmp['name']
        price = dictmp['price']

        sharesdb[i]['name'] = name
        sharesdb[i]['price'] = price
        sharesdb[i]['total'] = price * sharesdb[i]['shares']
        sum += sharesdb[i]['total']
    sum += cash
    return render_template("index.html", sharesdb=sharesdb, cash=cash, sum=sum)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")

    # Sym = symbol of share, sha = number of shares
    sym = request.form.get("symbol")
    sha = request.form.get("shares")

    for c in sha:
        if c not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            return apology("Invalid number of shares")

    # If lookup funciton cannot find symbol it doesn't exist
    dicts = lookup(sym)
    if not dicts:
        return apology("Invalid symbol")

    name = dicts["name"]
    price = dicts["price"]
    symbol = dicts["symbol"]

    # Get user id from session
    user_id = session["user_id"]

    # Getting price of desired purschache and cash of user
    price = price * float(sha)
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]['cash']

    if price > cash:
        return apology("Insufficient funds")

    cash = cash - price
    db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, user_id)
    date = datetime.datetime.now()

    sha = int(sha)
    price = float(price)
    current_share_db = db.execute("SELECT shares, price FROM shares WHERE user_id = ? AND symbol = ?", user_id, symbol)
    if len(current_share_db) > 0:
        db.execute("UPDATE shares SET shares = ?, price = ? WHERE user_id = ? AND symbol = ?",
                   (int(current_share_db[0]['shares']) + sha), (float(current_share_db[0]['price']) + price), user_id, symbol)
    else:
        db.execute("INSERT INTO shares (user_id, symbol, shares, price) VALUES(?, ?, ?, ?)", user_id, symbol, sha, price)
    db.execute("INSERT INTO transactions(user_id, symbol, shares, price, time) VALUES(?, ?, ?, ?, ?)", user_id, symbol, sha, price, date)
    return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]

    transactionsdb = db.execute("SELECT symbol, shares, time FROM transactions WHERE user_id = ?", user_id)
    for i in range(len(transactionsdb)):
        pricedb = lookup(transactionsdb[i]['symbol'])
        price = pricedb['price']
        transactionsdb[i]['price'] = price
    return render_template("history.html", transactionsdb=transactionsdb)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # If method is get display the website
    if request.method == "GET":
        return render_template("quote.html")

    sym = request.form.get("symbol")
    quote = lookup(sym)
    if quote == None:
        return apology("Stock symbol doesn't exist")
    return render_template("quotedisplay.html", name=quote["name"], symbol=quote["symbol"], price=quote["price"])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if username == "" or len(db.execute('SELECT username FROM users WHERE username = ?', username)) > 0:
        return apology("Invalid Username")
    if password == "":
        return apology("Invalid password")
    elif password != confirmation:
        return apology("Passwords don't match")

    db.execute('INSERT INTO users (username, hash) VALUES(?, ?)', username, generate_password_hash(password))
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)
    session["user_id"] = rows[0]["id"]
    # Redirect user to home page
    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # Get user id from session
    user_id = session["user_id"]

    # Find what stocks user has
    sharesdb = db.execute("SELECT symbol FROM shares WHERE user_id = ?", user_id)
    if request.method == "GET":
        return render_template("sell.html", sharesdb=sharesdb)

    # Get user's input
    stock = request.form.get("symbol")
    number = request.form.get("shares")

    # See how many shars of stock user has and check if he wants to sell more and see how much cash user has
    sdb = db.execute("SELECT shares, price FROM shares WHERE user_id = ? AND symbol = ?", user_id, stock)
    udb = db.execute("SELECT cash FROM users WHERE id = ?", user_id)

    if int(sdb[0]['shares']) < int(number):
        return apology("You don't have enough stocks")

    tmpdict = lookup(stock)
    price = tmpdict["price"]
    transaction = float(price) * float(number)

    db.execute("UPDATE shares SET shares = ?, price = ? WHERE user_id = ? AND symbol = ?",
               (int(sdb[0]['shares']) - int(number)), (float(sdb[0]['price']) - float(transaction)), user_id, stock)
    db.execute("UPDATE users SET cash = ? WHERE id = ?", (float(udb[0]['cash']) + float(transaction)), user_id)
    date = datetime.datetime.now()
    db.execute("INSERT INTO transactions (user_id, symbol, shares, price, time) VALUES(?, ?, ?, ?, ?)",
               user_id, stock, 0 - int(number), price, date)

    return redirect("/")
