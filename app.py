# import os
#only one user should login at a time

from flask import Flask, flash, jsonify, redirect, render_template, request,session
from flask_session import Session
from flask_mysqldb import MySQL
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date,datetime

from helpers import  login_required
from Send_Emails import Send_email

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#connecting flask application to database
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"]="" 
app.config["MYSQL_DB"] = "cement"
mysql = MySQL(app)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
@app.template_filter("lkr")
def lkr(value):
    """Format value as LKR."""
    return "Rs {:,.2f}".format(value)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


#get today's date in YYYY-MM-DD
today = datetime.today().strftime('%Y-%m-%d')

# #global variable
OTP = 0
user=() #global empty tuple

@app.route("/")
@login_required
def index():
    """Credit list"""
    totalCredit=0
    cur = mysql.connection.cursor()
    #resultValue is an integer representing the number of rows from the query
    resultValue = cur.execute("SELECT CUSTOMER_NAME,SUM(AMOUNT-PAYMENT-SURPLUS) FROM sales WHERE ((AMOUNT-PAYMENT-SURPLUS>0) OR (AMOUNT-PAYMENT-SURPLUS<0 AND CF_invoice IS NULL)) GROUP BY CUSTOMER_NAME")
    #if any rows satisfy the query
    customerDetails = cur.fetchall()
    if resultValue > 0:
        #calculating total credit
        for customerDetail in customerDetails:
            #customerDetail contains two columns indexed 0(name) & 1(sum of receivable)
            totalCredit += customerDetail[1]
    cur.close()
    return render_template("index.html",rows = customerDetails,total=totalCredit)
    

@app.route("/cf_pay", methods=["GET", "POST"])
@login_required
def carry_forward_pay():
    """carry forward"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        cf_from = request.form["excess_invoice"]
        cf_to = request.form["credit_invoice"]
        cf_amt = float(request.form["excess_amount"])
        cust_name = request.form["customer_name"]

        cur = mysql.connection.cursor()
        query = "UPDATE sales SET CF_INVOICE = %s WHERE INVOICE= %s"
        invoice = (cf_to,cf_from)
        cur.execute(query,invoice)
        mysql.connection.commit()

        query = "UPDATE sales SET SURPLUS = SURPLUS + %s WHERE INVOICE= %s"
        invoice = (cf_amt,cf_to)
        cur.execute(query,invoice)
        mysql.connection.commit()

        queryExcess = "SELECT * FROM sales WHERE CUSTOMER_NAME=%s AND AMOUNT < PAYMENT+SURPLUS AND CF_INVOICE IS NULL"
        queryCredit ="SELECT * FROM sales WHERE CUSTOMER_NAME=%s AND AMOUNT > PAYMENT+SURPLUS" 
        name = (cust_name,)

        noOfExcessInvoice=cur.execute(queryExcess,name)
        excess = cur.fetchall()
        
        noOfCreditInvoice=cur.execute(queryCredit,name)
        credit = cur.fetchall()
        cur.close()

        if (noOfExcessInvoice != 0) and (noOfCreditInvoice !=0):
            return render_template("cf_pay.html",excess=excess,credit=credit)
        return redirect ("/payment")

@app.route("/cf_sales", methods=["GET", "POST"])
@login_required
def carry_forward_sales():
    """carry forward"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        cf_from = request.form["excess_invoice"]
        cf_to = request.form["credit_invoice"]
        cf_amt = request.form["excess_amount"]
        cur = mysql.connection.cursor()
        query = "UPDATE sales SET CF_INVOICE = %s WHERE INVOICE= %s"
        invoice = (cf_to,cf_from)
        cur.execute(query,invoice)
        mysql.connection.commit()
        query = "UPDATE sales SET SURPLUS = %s WHERE INVOICE= %s"
        #check if it should be UPDATE sales SET SURPLUS = SURPLUS + %s WHERE INVOICE= %s
        invoice = (cf_amt,cf_to)
        cur.execute(query,invoice)
        mysql.connection.commit()
        cur.close()
        return redirect ("/sales")

@app.route("/add_item", methods=["GET", "POST"])
@login_required
def add_item():
    """add item"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        customer_name = (request.form["customer_name"]).upper()
        location = (request.form["location"]).upper()
        bags = int(request.form["bags"])
        unit_price = int(request.form["unit_price"])
        amount = float(request.form["amount"])
        invoice=request.form["invoice"]

        cur = mysql.connection.cursor()
        query = "SELECT * FROM sales WHERE INVOICE=%s"
        invoiceTuple = (invoice,)
        resultValue = cur.execute(query,invoiceTuple)
        if (resultValue != 0):
            #when adding the other items to existing invoice
            query = "UPDATE sales SET AMOUNT=AMOUNT + %s WHERE INVOICE = %s"
            addSale = (amount,invoice)
            cur.execute(query,addSale)
            mysql.connection.commit()
        else:
            #when adding the first item to invoice
            cur.execute("INSERT INTO sales (DATE,INVOICE,LOCATION,CUSTOMER_NAME,AMOUNT) VALUES(%s,%s,%s,%s,%s)",
                       (today,invoice,location,customer_name,amount))
            mysql.connection.commit()

        query = "SELECT * FROM sales WHERE INVOICE=%s"
        resultValue = cur.execute(query,invoiceTuple)
        salesRecord = cur.fetchone()
        cur.close()
        return render_template("add_sales.html",name=salesRecord[3],invoice=salesRecord[1],location=salesRecord[2])

@app.route("/sales", methods=["GET", "POST"])
@login_required
def sales():
    """Sales"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        customer_name = (request.form["customer_name"]).upper()
        location = (request.form["location"]).upper()
        bags = int(request.form["bags"])
        unit_price = float(request.form["unit_price"])
        amount = float(request.form["amount"])
        invoice=request.form["invoice"]

        cur = mysql.connection.cursor()
        query = "SELECT INVOICE FROM sales WHERE INVOICE=%s"
        invoiceTuple = (invoice,)
        resultValue = cur.execute(query,invoiceTuple)
        cur.close()
        if (resultValue != 0):
            #when adding the last item to existing invoice
            cur = mysql.connection.cursor()
            query = "UPDATE sales SET AMOUNT=AMOUNT + %s WHERE INVOICE = %s"
            addSale = (amount,invoice)
            cur.execute(query,addSale)
            mysql.connection.commit()
            cur.close()
        else:
            #if creating new invoice
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO sales (DATE,INVOICE,LOCATION,CUSTOMER_NAME,AMOUNT,PAYMENT,SURPLUS) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                       (today,invoice,location,customer_name,amount,0,0))
            mysql.connection.commit()
            cur.close()

        #check if that customer has any excessive amount
        #max only one invoice will be in excess for a given customer at a time
        cur = mysql.connection.cursor()
        queryExcess="SELECT * FROM sales WHERE CUSTOMER_NAME = %s AND (AMOUNT-PAYMENT-SURPLUS) < 0 AND CF_INVOICE IS NULL"
        queryCredit = "SELECT * FROM sales WHERE CUSTOMER_NAME = %s AND (AMOUNT-PAYMENT-SURPLUS) > 0"
        name = (customer_name,)
        noOfExcessInvoice=cur.execute(queryExcess,name)
        excess = cur.fetchall()
        noOfCreditInvoice=cur.execute(queryCredit,name)
        credit = cur.fetchall()
        cur.close()
        if noOfExcessInvoice != 0:
            #There is/are excess invoice/s
            return render_template("cf_sales.html",excess=excess,credit=credit)
        else:
            return redirect ("/sales")
    else:
        cur = mysql.connection.cursor()
        query = "SELECT MAX(INVOICE) FROM sales WHERE LOCATION='KIL'"
        resultValue = cur.execute(query)
        #fetch the last KIL invoice number
        kilInvoice = cur.fetchone()
        #the next possible KIL invoice
        kilInvoice = kilInvoice[0]+1
        # print(kilInvoice)
        
        query = "SELECT MAX(INVOICE) FROM sales WHERE LOCATION='MUL'"
        resultValue = cur.execute(query)
        #fetch the last MUL invoice number
        mulInvoice = cur.fetchone()
        #the next possible MUL invoice
        mulInvoice = mulInvoice[0]+1
        # print(mulInvoice)
        

        query = "SELECT * FROM sales WHERE INVOICE=%s"
        if((kilInvoice-1)%100 == 0):
            #new bill book begins
            #check if new bill book is taken
            invoice = (kilInvoice,)
            resultValue=cur.execute(query,invoice)
            # print(resultValue)
            while (resultValue != 0):
                kilInvoice = kilInvoice+100
                invoice = (kilInvoice,)
                resultValue=cur.execute(query,invoice)

        if((mulInvoice-1)%100 == 0):
            #new bill book begins
            #check if new bill book is taken
            invoice = (mulInvoice,)
            resultValue=cur.execute(query,invoice)
            # print(resultValue)
            while (resultValue != 0):
                mulInvoice = mulInvoice+100
                invoice = (mulInvoice,)
                resultValue=cur.execute(query,invoice)

        resultValue = cur.execute("SELECT CUSTOMER_NAME FROM customer ORDER BY CUSTOMER_NAME ASC")
        customerList = cur.fetchall()
        cur.close()
        return render_template("sales.html",customerList=customerList, kilInvoice=kilInvoice, mulInvoice=mulInvoice)

@app.route("/payment", methods=["GET", "POST"])
@login_required
def payment():
    """Payment"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        payment_invoice=request.form["payment_invoice"]
        amount=request.form["amount"]
        cur = mysql.connection.cursor()
        query = "UPDATE sales SET PAYMENT=PAYMENT + %s WHERE INVOICE= %s"
        pay = (amount,payment_invoice)
        cur.execute(query,pay)
        mysql.connection.commit()

        query = "SELECT * FROM sales WHERE INVOICE= %s"
        pay = (payment_invoice,)
        resultValue=cur.execute(query,pay)
        updatedRecord = cur.fetchone()
        queryExcess = "SELECT * FROM sales WHERE CUSTOMER_NAME=%s AND AMOUNT < PAYMENT+SURPLUS AND CF_INVOICE IS NULL"
        queryCredit ="SELECT * FROM sales WHERE CUSTOMER_NAME=%s AND AMOUNT > PAYMENT+SURPLUS" 
        name = (updatedRecord[3],)

        noOfExcessInvoice=cur.execute(queryExcess,name)
        excess = cur.fetchall()
        
        noOfCreditInvoice=cur.execute(queryCredit,name)
        credit = cur.fetchall()
        cur.close()
        if ((noOfExcessInvoice != 0) and (noOfCreditInvoice !=0)):
            return render_template("cf_pay.html",excess=excess,credit=credit)
        return redirect ("/payment")
    else:
        cur = mysql.connection.cursor()
        resultValue = cur.execute("SELECT * FROM sales WHERE AMOUNT>PAYMENT+SURPLUS ORDER BY CUSTOMER_NAME ASC")
        credits= cur.fetchall()
        cur.close()
        return render_template("payment.html", credits = credits)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add new customer"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        name = (request.form["new_customer"]).upper()
        name=name.replace(" ", "_")
        cur = mysql.connection.cursor()
        query = "SELECT CUSTOMER_NAME FROM customer WHERE CUSTOMER_NAME=%s"
        nameTuple = (name,)
        resultValue = cur.execute(query,nameTuple)
        #design so that user will be asked to confirm when adding new customer name if a similar name already exists in db
        if resultValue == 0:
            cur.execute("INSERT INTO customer (CUSTOMER_NAME) VALUES(%s)",(name,))
            # cur.execute("INSERT INTO customer (name) VALUES(:name)", name=name)
            mysql.connection.commit()
            flash("New Customer Added Successfully!")
            return redirect("/sales")
        else:
            flash("Customer already exists! Try a different name.")
            return redirect("/add")
        cur.close()
    else:
        return render_template("add.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        cur = mysql.connection.cursor()
        # Query database for username
        username=request.form["username"]
        query = "SELECT * FROM users WHERE username = %s"
        usernameTuple = (username,)
        resultValue = cur.execute(query,usernameTuple)
        global user
        # Ensure username exists
        if resultValue == 0:
            #### it might be also bcs incorrect username is entered!!
            flash("Have To Register!")
            return render_template("register.html")
        user = cur.fetchone()
        # Ensure password is correct
        if not (check_password_hash(user[2], request.form["password"])):
            flash("Incorrect Password")
            return render_template("login.html")

        cur.close()
        #send OTP to user
        global OTP
        OTP = Send_email() #later change recipient email to the email id taken from users table
        # Redirect user to otp page
        return render_template("otp.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/otp", methods=["GET", "POST"])
def otp():
    """Verify OTP"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        formOTP = (request.form["1st"])+(request.form["2nd"])+(request.form["3rd"])+(request.form["4th"])+(request.form["5th"])+(request.form["6th"])
        if formOTP == str(OTP):
            global user
            # Remember which user has logged in
            session["user_id"] = user[0]

            #empty the global variable
            user = ()

            return redirect("/")
        else:
            flash("Incorrect OTP Entered. Try Again")
            return render_template("login.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    """Forgot Password"""
    if request.method == "POST":
        cur = mysql.connection.cursor()
        # Ensure  that two passwords match
        if request.form["password"] != request.form["confirmation"]:
            flash("The two passwords do not match!")
            return render_template("forgot.html")

        # Query database for username
        query = "SELECT * FROM users WHERE username = %s"
        username=request.form["username"]
        resultValue = cur.execute(query,(username,))

        # Ensure username exists and password is correct
        if resultValue == 0:
            flash("Invalid Username")
            return render_template("forgot.html")
        user = cur.fetchone()
        if user[3] != request.form["email"]:
            flash("Incorrect Email ID")
            return render_template("forgot.html")
        
        query = "UPDATE users SET hash = %s"
        hashpass = (generate_password_hash(request.form["password"]),)
        cur.execute(query,hashpass)
        mysql.connection.commit()
        cur.close()
        flash("Password Changed Successfully")#this flash does not work. I think flash doesn't work with redirection
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("forgot.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        cur = mysql.connection.cursor()
        # Ensure  that two passwords match
        if request.form["password"] != request.form["confirmation"]:
            flash("The two passwords do not match!")#check!!
            return render_template("register.html")

        # Query database for username
        query = "SELECT * FROM users WHERE username = %s"
        username=request.form["username"]
        resultValue = cur.execute(query,(username,))

        # Ensure username exists and password is correct
        if resultValue != 0:
            flash("The user already exist! Try a different username")
            return render_template("register.html")
        cur.close()

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username,hash,email) VALUES(%s,%s,%s)",(username,generate_password_hash(request.form["password"]), request.form["email"]))
        mysql.connection.commit()
        cur.close()
        flash("User Registered Successfully")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

#ok
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/kil_report")
@login_required
def kil_report():
    day_count={}
    total=0
    date_format = "%Y-%m-%d"
    cur = mysql.connection.cursor()
    query = "SELECT * FROM sales WHERE ((AMOUNT>PAYMENT+SURPLUS) OR (AMOUNT<PAYMENT+SURPLUS AND CF_INVOICE IS NULL)) AND LOCATION=%s ORDER BY CUSTOMER_NAME ASC, INVOICE ASC"
    location = ("KIL",)
    resultValue = cur.execute(query,location)
    if resultValue>0:
        kilRecords = cur.fetchall()
        for row in kilRecords:
            invoiceDate = (row[0]).strftime(date_format)
            invoiceDate = datetime.strptime(invoiceDate, date_format)
            todayDate = datetime.strptime(today, date_format)
            delta = todayDate - invoiceDate
            #day_count is a dictionary
            day_count[row[1]]=delta.days
            total=total+(row[4]-row[6]-row[7])
        return render_template("report.html",result=kilRecords,total=total,day_count=day_count,section="KILINOCHCHI")
    else:
        #if no records to display
        return("No records to display")
    cur.close()

@app.route("/mul_report")
@login_required
def mul_report():
    day_count={}
    total=0
    date_format = "%Y-%m-%d"
    cur = mysql.connection.cursor()
    query = "SELECT * FROM sales WHERE ((AMOUNT>PAYMENT+SURPLUS) OR (AMOUNT<PAYMENT+SURPLUS AND CF_INVOICE IS NULL)) AND LOCATION=%s ORDER BY CUSTOMER_NAME ASC, INVOICE ASC"
    location = ("MUL",)
    resultValue = cur.execute(query,location)
    if resultValue>0:
        mulRecords = cur.fetchall()
        for row in mulRecords:
            invoiceDate = (row[0]).strftime(date_format)
            invoiceDate = datetime.strptime(invoiceDate, date_format)
            todayDate = datetime.strptime(today, date_format)
            delta = todayDate - invoiceDate
            #day_count is a dictionary
            day_count[row[1]]=delta.days
            total=total+(row[4]-row[6]-row[7])
        return render_template("report.html",result=mulRecords,total=total,day_count=day_count,section="MULLAITHIVU")
    else:
        #if no records to display
        return("No records to display")
    cur.close()


@app.route("/all_report")
@login_required
def all():
    day_count={}
    total=0
    date_format = "%Y-%m-%d"
    cur = mysql.connection.cursor()
    query = "SELECT * FROM sales WHERE ((AMOUNT>PAYMENT+SURPLUS) OR (AMOUNT<PAYMENT+SURPLUS AND CF_INVOICE IS NULL)) ORDER BY CUSTOMER_NAME ASC, INVOICE ASC"
    resultValue = cur.execute(query)
    if resultValue>0:
        allRecords = cur.fetchall()
        for row in allRecords:
            invoiceDate = (row[0]).strftime(date_format)
            invoiceDate = datetime.strptime(invoiceDate, date_format)
            todayDate = datetime.strptime(today, date_format)
            delta = todayDate - invoiceDate
            #day_count is a dictionary
            day_count[row[1]]=delta.days
            total=total+(row[4]-row[6]-row[7])
        return render_template("report.html",result=allRecords,total=total,day_count=day_count,section="ALL")
    else:
        #if no records to display
        return("No records to display")
    cur.close()


# def errorhandler(e):
#     """Handle error"""
#     if not isinstance(e, HTTPException):
#         e = InternalServerError()
#     return apology(e.name, e.code)


# Listen for errors
# for code in default_exceptions:
#     app.errorhandler(code)(errorhandler)
    
if __name__ == '__main__':
    app.run()
    # app.run(debug=True)

