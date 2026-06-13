import mysql.connector as mys
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
from getpass import getpass
import sys
import os
from dotenv import load_dotenv
load_dotenv()

try:
    import bcrypt
except ImportError:
    print("ERROR: bcrypt is required. Run: pip install bcrypt")
    sys.exit(1)

# FIX: removed all global db usage — db is now passed as a parameter

def view(db):
    cu = db.cursor()
    print("1-products report, 2-staff report, 3-storage report, 4-Customer Order Report, 5-Yearly Report")
    i = input("Enter your choice : ")
    if i == "1":
        cu.execute("select * from Products")
        header = cu.column_names
        cu = cu.fetchall()
        if cu == []:
            print("No Data Present in this table")
            return
        table = pd.DataFrame(cu)
        table.columns = header
        print(table)
    elif i == "2":
        cu.execute("select Idno,Name,UserType from Users")
        header = cu.column_names
        cu = cu.fetchall()
        if cu == []:
            print("No Data Present in this table")
            return
        table = pd.DataFrame(cu)
        table.columns = header
        print(table)
    elif i == "3":
        cu.execute("select * from Storage")
        header = cu.column_names
        cu = cu.fetchall()
        if cu == []:
            print("No Data Present in this table")
            return
        table = pd.DataFrame(cu)
        table.columns = header
        print(table)
    elif i == "4":
        cu.execute("select * from CustomerOrder")
        header = cu.column_names
        cu = cu.fetchall()
        if cu == []:
            print("No Data Present in this table")
            return
        table = pd.DataFrame(cu)
        table.columns = header
        print(table)
    elif i == "5":
        data = {}
        cu.execute("select Year(Purchasedate) as year, SUM(purchasecost*pqty) as cp from Storage s,Products p where s.productname=p.productname group by year")
        cp = cu.fetchall()
        cu = db.cursor()
        cu.execute("select year(Saledate) as year,sum(quantity*saleprice) as sp from CustomerOrder c,Products p where p.productname=c.productname group by year")
        sp = cu.fetchall()
        for i in cp:
            t = int(i[0])
            data[t] = [i[1], 0]
        for i in sp:
            t = int(i[0])
            if t in data:
                data[t][1] = i[1]
            else:
                data[t] = [0, i[1]]
        print(data)
        year = list(data.keys())
        year.sort()
        cp = []
        sp = []
        p = []
        for i in year:
            cp.append(data[i][0])
            sp.append(data[i][1])
            p.append(data[i][1] - data[i][0])
        br1 = np.arange(len(year))
        br2 = [x + 0.2 for x in br1]
        br3 = [x + 0.2 for x in br2]
        fig = plt.figure(figsize=(10, 5))
        ax = plt.subplot()
        p1 = ax.bar(br1, sp, color='r', width=0.2, edgecolor='grey', label='Sale')
        p2 = ax.bar(br2, cp, color='g', width=0.2, edgecolor='grey', label='Cost')
        p3 = ax.bar(br3, p, color='b', width=0.2, edgecolor='grey', label='Profit')
        ax.axhline(y=0, color="k")
        plt.xlabel("Products")
        plt.ylabel("Sales")
        plt.title("Yearly Report")
        plt.xticks([r + 0.2 for r in range(len(year))], year)
        plt.legend((p1[0], p2[0], p3[0]), ("Sale", "Cost", "Profit"))
        plt.show()

def remove_employee(db):
    cu = db.cursor()
    i = input("Enter name of employee: ")
    # FIX: parameterized query
    cu.execute("SELECT * FROM Users WHERE Name = %s", (i,))
    result = cu.fetchall()
    if result == []:
        print("Employee Name Incorrect/Does not exist")
        return
    cu.execute("DELETE FROM Users WHERE Name = %s", (i,))
    db.commit()

def add_user(db):
    cu = db.cursor()
    a = input("Admin/Manager: ").lower()
    u = input("Enter username: ")
    p = getpass("Enter password: ")
    # FIX: hash password with bcrypt before storing
    # FIX: parameterized query + AUTO_INCREMENT handles IdNo
    hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
    cu.execute(
        "INSERT INTO Users (Name, UserType, password) VALUES (%s, %s, %s)",
        (u, a, hashed)
    )
    db.commit()

def admin(u, db):
    print("")
    print("1-view stats, 2-remove employee, 3-Add User, 4-exit")
    i = input("Enter your choice : ")
    if i == "1":
        view(db)
    elif i == "2":
        remove_employee(db)
    elif i == "3":
        add_user(db)
    elif i == "4":
        return True
    return False

def manager(u, db):
    print("")
    print("1-Add Product, 2-Edit Product, 3-Customer Order, 4-View Details, 5-Exit")
    i = input("Enter your choice : ")
    if i == "1":
        add_product(db)
    elif i == "2":
        edit_product(db)
    elif i == "3":
        customerorder(db)
    elif i == "4":
        view(db)
    elif i == "5":
        return True
    return False

def migrate_db(db):
    cu = db.cursor()
    try:
        cu.execute("""
            SELECT EXTRA FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'Users'
            AND COLUMN_NAME = 'IdNo'
        """)
        result = cu.fetchone()
        if result and 'auto_increment' not in result[0].lower():
            cu.execute("SET @r = 0")
            cu.execute("UPDATE Users SET IdNo = (@r := @r + 1) ORDER BY IdNo")
            db.commit()
            cu.execute("ALTER TABLE Users MODIFY COLUMN IdNo INT PRIMARY KEY AUTO_INCREMENT")
            db.commit()
    except Exception as e:
        print(f"Schema migration warning: {e}")

def users(db):
    print("Login-L, quit-q")
    x = input("Enter your choice : ").lower()
    print("")
    if x == "l":
        cu = db.cursor()
        cu.execute("select * from Users")
        rows = cu.fetchall()
        if rows == []:
            print("No admin assigned. Create admin first.")
            add_user(db)
            users(db)
            return
        u = input("Enter username: ")
        p = getpass("Enter password: ")
        cu = db.cursor()
        cu.execute("SELECT Name, password, UserType FROM Users WHERE Name = %s", (u,))
        user = cu.fetchone()
        if user is None:
            print("Invalid username/password")
            return
        stored_pwd = user[1]
        authenticated = False
        if stored_pwd.startswith('$2b$') or stored_pwd.startswith('$2a$'):
            authenticated = bcrypt.checkpw(p.encode(), stored_pwd.encode())
        else:
            # Legacy plain text password — migrate to bcrypt on successful login
            if p == stored_pwd:
                authenticated = True
                hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
                cu2 = db.cursor()
                cu2.execute("UPDATE Users SET password = %s WHERE Name = %s", (hashed, u))
                db.commit()
        if authenticated:
            if user[2] == "admin":
                while True:
                    quit = admin(u, db)
                    if quit:
                        break
            else:
                while True:
                    quit = manager(u, db)
                    if quit:
                        break
        else:
            print("Invalid username/password")
    elif x == 'q':
        sys.exit(0)

def storage(db, p_name, purchase_cost, pqty, pid):
    cu = db.cursor()
    purchase_date = input("Enter purchase date(YYYY-MM-DD): ")
    year, month, day = map(int, purchase_date.split("-"))
    purchase_date = datetime.date(year, month, day)
    # FIX: parameterized query
    cu.execute(
        "INSERT INTO Storage VALUES (%s, %s, %s, %s, %s, %s)",
        (pid, p_name, purchase_cost, pqty, pqty, purchase_date)
    )
    db.commit()

def add_product(db):
    try:
        pid = input("enter product id: ")
        p_name = input("Enter product name: ")
        supp_name = input("Enter supplier name: ")
        pqty = input("Enter Purchase qty: ")
        product_cost = int(input("Enter product cost: "))
        saleprice = int(input("enter sale price: "))
        cu = db.cursor()
        # FIX: parameterized query
        cu.execute(
            "INSERT INTO Products VALUES (%s, %s, %s, %s)",
            (pid, p_name, saleprice, supp_name)
        )
        db.commit()
        storage(db, p_name, product_cost, pqty, pid)
    except mys.IntegrityError:
        print("Product already exists")

def edit_product(db):
    cu = db.cursor()
    p_name = input("Enter product name : ")
    pid = input("Enter product id: ")
    # FIX: parameterized query
    cu.execute(
        "SELECT * FROM Products WHERE ProductName = %s AND P_Id = %s",
        (p_name, pid)
    )
    result = cu.fetchall()
    if result == []:
        print("Product does not exist")
        return
    add_quantity = input("Enter how much quantity to add: ")
    cu.execute(
        "UPDATE Storage SET CurrentQuantity = CurrentQuantity + %s WHERE ProductName = %s",
        (add_quantity, p_name)
    )
    db.commit()

def customerorder(db):
    cu = db.cursor()
    productname = input("Enter product name: ")
    pid = int(input("enter product id: "))
    # FIX: parameterized query
    cu.execute(
        "SELECT * FROM Products WHERE ProductName = %s AND P_Id = %s",
        (productname, pid)
    )
    result = cu.fetchall()
    if result == []:
        print("Product does not exist")
        return

    quantity = int(input("Enter quantity: "))

    cu.execute(
        "SELECT CurrentQuantity FROM Storage WHERE ProductName = %s",
        (productname,)
    )
    current_quantity = cu.fetchall()[0][0]

    if current_quantity == 0:
        print("Sorry this item is not available")
        return

    while quantity > current_quantity:
        print("Quantity is greater than available %d" % (current_quantity))
        quantity = int(input("Enter Updated quantity : "))

    user_id = input("Enter customer name: ")
    billno = int(input("Enter bill no: "))

    saledate = input("Enter sale date(YYYY-MM-DD): ")
    year, month, day = map(int, saledate.split("-"))
    saledate = datetime.date(year, month, day)

    cu = db.cursor()
    cu.execute("SELECT SalePrice FROM Products WHERE P_Id = %s", (pid,))
    total = (cu.fetchall()[0][0]) * quantity
    # FIX: parameterized queries
    cu.execute(
        "INSERT INTO CustomerOrder VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (pid, productname, user_id, billno, quantity, saledate, total)
    )
    cu.execute(
        "UPDATE Storage SET CurrentQuantity = CurrentQuantity - %s WHERE ProductName = %s",
        (quantity, productname)
    )
    db.commit()

def database_create():
    db = mys.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        passwd=os.getenv("DB_PASSWORD")
    )
    cu = db.cursor()
    cu.execute("create database inventory;")
    db = mys.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        passwd=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )
    cu = db.cursor()
    # FIX: Added PRIMARY KEY AUTO_INCREMENT to IdNo
    cu.execute("create table Users (IdNo int PRIMARY KEY AUTO_INCREMENT, Name varchar(20), UserType varchar(15), password varchar(300))")
    cu.execute("create table Products (P_Id int primary key, ProductName varchar(20), SalePrice int, SupplierName varchar(15))")
    cu.execute("create table Storage (P_Id int, ProductName varchar(20), PurchaseCost int, pqty int, Currentquantity int, Purchasedate date, foreign key(P_Id) references Products(P_Id))")
    cu.execute("create table CustomerOrder (P_Id int, ProductName varchar(20), Name varchar(20), BillNo int, Quantity int, SaleDate date, Total int, foreign key(P_Id) references Products(P_Id))")
    db.commit()
    return db

print("                   INVENTORY MANAGEMENT SYSTEM")
print("--------------------------------------------------------------------------------")
print("")
try:
    db = mys.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        passwd=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )
except Exception as e:
    print(f"Database connection failed: {e}")
    db = database_create()

migrate_db(db)

while True:
    users(db)
