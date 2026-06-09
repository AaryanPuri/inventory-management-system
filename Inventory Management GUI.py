import mysql.connector as mys
import pandas as pd
import datetime
import sys
try:
    import bcrypt
except ImportError:
    print("ERROR: bcrypt is required. Run: pip install bcrypt")
    sys.exit(1)
from tkinter import *
from tkinter import messagebox
from pandastable import Table
from tkcalendar import DateEntry
import os
from dotenv import load_dotenv
load_dotenv()

class gui:
    def __init__(self):
        try:  # FIX: bare except replaced with specific exception
            self.db = mys.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                passwd=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_DATABASE")
            )
        except Exception as e:
            self.database_create()
        self.migrate_db()
        self.work = True
        self.window = Tk()
        self.window.protocol("WM_DELETE_WINDOW", lambda: exit(0))
        self.window.title("Inventory Management System")
        self.window.geometry("600x600")
        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.after(1000, self.loginscreen)
        self.window.mainloop()

    def database_create(self):
        self.db = mys.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            passwd=os.getenv("DB_PASSWORD")
        )
        self.cu = self.db.cursor()
        self.cu.execute("create database inventory;")
        self.db = mys.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            passwd=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE")
        )
        self.cu = self.db.cursor()
        # FIX: Added PRIMARY KEY AUTO_INCREMENT to IdNo
        self.cu.execute("create table Users (IdNo int PRIMARY KEY AUTO_INCREMENT, Name varchar(20), UserType varchar(15), password varchar(300))")
        self.cu.execute("create table Products (P_Id int primary key, ProductName varchar(20), SalePrice int, SupplierName varchar(15))")
        self.cu.execute("create table Storage (P_Id int, ProductName varchar(20), PurchaseCost int, pqty int, Currentquantity int, Purchasedate date, FOREIGN KEY (P_Id) REFERENCES Products (P_Id) ON DELETE CASCADE)")
        self.cu.execute("create table CustomerOrder (P_Id int, ProductName varchar(20), Name varchar(20), BillNo int, Quantity int, SaleDate date, Total int, foreign key(P_Id) references Products(P_Id))")
        # FIX: Removed hardcoded dhruv/dhruv default admin
        self.db.commit()

    def migrate_db(self):
        cu = self.db.cursor()
        try:
            cu.execute("""
                SELECT EXTRA FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'Users'
                AND COLUMN_NAME = 'IdNo'
            """)
            result = cu.fetchone()
            if result and 'auto_increment' not in result[0].lower():
                # Fix any duplicate IdNo values before adding PRIMARY KEY
                cu.execute("SET @r = 0")
                cu.execute("UPDATE Users SET IdNo = (@r := @r + 1) ORDER BY IdNo")
                self.db.commit()
                cu.execute("ALTER TABLE Users MODIFY COLUMN IdNo INT PRIMARY KEY AUTO_INCREMENT")
                self.db.commit()
        except Exception as e:
            print(f"Schema migration warning: {e}")

    def loginscreen(self):
        self.f = Frame(self.window)
        self.f.grid(row=0, column=0)
        l1 = Label(self.f, text="Inventory Management System")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, padx=50)

        l2 = Label(self.f, text="Login")
        l2.configure(font=("Arial", 22))
        l2.grid(row=1, column=0, columnspan=2, sticky="S", pady=50)
        self.f.grid_rowconfigure(1, minsize=300)

        l3 = Label(self.f, text="Username")
        l3.configure(font=("Arial", 14))
        l3.grid(row=2, column=0, sticky="E", pady=10)

        l4 = Label(self.f, text="Password")
        l4.configure(font=("Arial", 14))
        l4.grid(row=3, column=0, sticky="E")

        self.v = StringVar()
        self.e1 = Entry(self.f, width=30, textvariable=self.v)
        self.e1.grid(row=2, column=1, sticky="W", padx=20)

        self.v2 = StringVar()
        self.e2 = Entry(self.f, width=30, textvariable=self.v2, show="*")
        self.e2.grid(row=3, column=1, sticky="W", padx=20)

        f1 = Frame(self.f)
        f1.grid(row=4, columnspan=2)

        b = Button(f1, text="Sign In", width=20, command=self.users)
        b.grid(row=0, column=0, sticky="E", pady=20, columnspan=2)

        self.l4 = Label(self.f, text="", fg="red")
        self.l4.configure(font=("Arial", 14))
        self.l4.grid(row=5, column=0, columnspan=2)

    def users(self):
        username = self.e1.get()
        password = self.e2.get()
        cu = self.db.cursor()
        # FIX: If no users exist, redirect to first admin setup
        cu.execute("SELECT COUNT(*) FROM Users")
        count = cu.fetchone()[0]
        if count == 0:
            self.f.destroy()
            self.create_first_admin()
            return
        self.checklogin(username, password)

    def create_first_admin(self):
        # FIX: Replaces hardcoded dhruv/dhruv — prompts user to create first admin
        self.f_setup = Frame(self.window)
        self.f_setup.grid(row=0, column=0)
        self.f_setup.grid_rowconfigure(0, minsize=200)
        self.window.grid_columnconfigure(0, weight=1)

        l1 = Label(self.f_setup, text="Create Admin Account")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, sticky="N")

        l2 = Label(self.f_setup, text="Username")
        l2.configure(font=("Arial", 14))
        l2.grid(row=1, column=0, sticky="E", pady=10)
        v1 = StringVar()
        e1 = Entry(self.f_setup, width=30, textvariable=v1)
        e1.grid(row=1, column=1, sticky="W", padx=20)

        l3 = Label(self.f_setup, text="Password")
        l3.configure(font=("Arial", 14))
        l3.grid(row=2, column=0, sticky="E", pady=10)
        v2 = StringVar()
        e2 = Entry(self.f_setup, width=30, textvariable=v2, show="*")
        e2.grid(row=2, column=1, sticky="W", padx=20)

        l_err = Label(self.f_setup, text="", fg="red")
        l_err.configure(font=("Arial", 14))
        l_err.grid(row=4, column=0, columnspan=2, pady=10)

        def create():
            name = v1.get().strip()
            pwd = v2.get()
            if not name:
                l_err.config(text="Username required")
                return
            if not pwd:
                l_err.config(text="Password required")
                return
            hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
            cu = self.db.cursor()
            cu.execute(
                "INSERT INTO Users (Name, UserType, password) VALUES (%s, %s, %s)",
                (name, 'admin', hashed)
            )
            self.db.commit()
            self.f_setup.destroy()
            self.loginscreen()

        b1 = Button(self.f_setup, text="Create Admin", height=3, width=20, command=create)
        b1.grid(row=3, column=0, columnspan=2, pady=20)

    def checklogin(self, username, password):
        cu = self.db.cursor()
        cu.execute("SELECT Name, password, UserType FROM Users WHERE Name = %s", (username,))
        user = cu.fetchone()
        if user is None:
            self.l4.config(text="Invalid username/password")
            self.e1.delete(0, END)
            self.e2.delete(0, END)
            return
        stored_pwd = user[1]
        authenticated = False
        if stored_pwd.startswith('$2b$') or stored_pwd.startswith('$2a$'):
            authenticated = bcrypt.checkpw(password.encode(), stored_pwd.encode())
        else:
            # Legacy plain text password — migrate to bcrypt on successful login
            if password == stored_pwd:
                authenticated = True
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                cu2 = self.db.cursor()
                cu2.execute("UPDATE Users SET password = %s WHERE Name = %s", (hashed, username))
                self.db.commit()
        if authenticated:
            if user[2] == "admin":
                self.f.destroy()
                self.adminscreen()
            else:
                self.f.destroy()
                self.employeescreen()
        else:
            self.l4.config(text="Invalid username/password")
            self.e1.delete(0, END)
            self.e2.delete(0, END)

    def adminscreen(self):
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=100)
        self.window.grid_columnconfigure(0, weight=1)
        l1 = Label(self.f2, text="Admin Menu")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, sticky="N")
        b1 = Button(self.f2, text="View Stats", height=3, width=40, command=lambda: [self.f2.destroy(), self.view_stats(0)])
        b1.grid(row=1, column=0, sticky="E", pady=20, columnspan=2)
        b2 = Button(self.f2, text="Remove Employee", height=3, width=40, command=lambda: [self.f2.destroy(), self.remove_employeescreen()])
        b2.grid(row=2, column=0, sticky="E", pady=20, columnspan=2)
        b3 = Button(self.f2, text="Add User", height=3, width=40, command=lambda: [self.f2.destroy(), self.add_userscreen()])
        b3.grid(row=3, column=0, sticky="E", pady=20, columnspan=2)
        b4 = Button(self.f2, text="Log Out", height=3, width=40, command=lambda: [self.f2.destroy(), self.loginscreen()])
        b4.grid(row=4, column=0, sticky="E", pady=20, columnspan=2)

    def productreport(self, p):
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=100)
        self.window.grid_columnconfigure(0, weight=1)
        b5 = Button(self.f2, text="Back", height=3, width=20, command=lambda: [self.f2.destroy(), self.view_stats(p)])
        b5.grid(row=4, column=0, sticky="E", pady=20, columnspan=2)
        self.cu = self.db.cursor()
        self.cu.execute("select * from products")
        header = list(self.cu.column_names)
        self.cu = self.cu.fetchall()
        if self.cu != []:
            table = pd.DataFrame(self.cu)
            table.columns = header
        else:
            table = pd.DataFrame(columns=header)
            s = pd.Series([None for i in range(len(header))])
            print(s)
            pd.concat([table, s], axis=0)
            print(table)
        pt = Table(self.f2, dataframe=table, showtoolbar=True, showstatusbar=True)
        pt.grid(row=0, rowspan=3)
        pt.show()

    def staffreport(self, p):
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=100)
        self.window.grid_columnconfigure(0, weight=1)
        b5 = Button(self.f2, text="Back", height=3, width=20, command=lambda: [self.f2.destroy(), self.view_stats(p)])
        b5.grid(row=4, column=0, sticky="E", pady=20, columnspan=2)
        self.cu = self.db.cursor()
        self.cu.execute("select Idno,Name,usertype from users")
        header = list(self.cu.column_names)
        self.cu = self.cu.fetchall()
        if self.cu != []:
            table = pd.DataFrame(self.cu)
            table.columns = header
        else:
            table = pd.DataFrame(columns=header)
            s = pd.Series([None for i in range(len(header))])
            print(s)
            pd.concat([table, s], axis=0)
            print(table)
        pt = Table(self.f2, dataframe=table, showtoolbar=True, showstatusbar=True)
        pt.grid(row=0, rowspan=3)
        pt.show()

    def customer_orderreport(self, p):
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=100)
        self.window.grid_columnconfigure(0, weight=1)
        b5 = Button(self.f2, text="Back", height=3, width=20, command=lambda: [self.f2.destroy(), self.view_stats(p)])
        b5.grid(row=4, column=0, sticky="E", pady=20, columnspan=2)
        self.cu = self.db.cursor()
        self.cu.execute("select * from customerorder")
        header = list(self.cu.column_names)
        self.cu = self.cu.fetchall()
        if self.cu != []:
            table = pd.DataFrame(self.cu)
            table.columns = header
        else:
            table = pd.DataFrame(columns=header)
            s = pd.Series([None for i in range(len(header))])
            print(s)
            pd.concat([table, s], axis=0)
            print(table)
        pt = Table(self.f2, dataframe=table, showtoolbar=True, showstatusbar=True)
        pt.grid(row=0, rowspan=3)
        pt.show()

    def storagereport(self, p):
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=100)
        b5 = Button(self.f2, text="Back", height=3, width=20)
        b5.grid(row=4, column=0, sticky="E", pady=20, columnspan=2)
        if (p == 2):
            b5.config(command=lambda: [self.f2.destroy(), self.edit_product()])
        else:
            b5.config(command=lambda: [self.f2.destroy(), self.view_stats(p)])
        self.window.grid_columnconfigure(0, weight=1)
        self.cu = self.db.cursor()
        self.cu.execute("select * from storage")
        header = list(self.cu.column_names)
        self.cu = self.cu.fetchall()
        if self.cu != []:
            table = pd.DataFrame(self.cu)
            table.columns = header
        else:
            table = pd.DataFrame(columns=header)
            s = pd.Series([None for i in range(len(header))])
            print(s)
            pd.concat([table, s], axis=0)
            print(table)
        pt = Table(self.f2, dataframe=table, showtoolbar=True, showstatusbar=True)
        pt.grid(row=0, rowspan=3)
        pt.show()

    def view_stats(self, p):
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=100)
        self.window.grid_columnconfigure(0, weight=1)
        l1 = Label(self.f2, text="REPORTS")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, sticky="N")
        b1 = Button(self.f2, text="Product Report", height=3, width=40, command=lambda: [self.f2.destroy(), self.productreport(p)])
        b1.grid(row=1, column=0, sticky="E", pady=20, columnspan=2)
        b2 = Button(self.f2, text="Staff Report", height=3, width=40, command=lambda: [self.f2.destroy(), self.staffreport(p)])
        b2.grid(row=2, column=0, sticky="E", pady=20, columnspan=2)
        b3 = Button(self.f2, text="Storage Report", height=3, width=40, command=lambda: [self.f2.destroy(), self.storagereport(p)])
        b3.grid(row=3, column=0, sticky="E", pady=20, columnspan=2)
        b4 = Button(self.f2, text="Customer Order Report", height=3, width=40, command=lambda: [self.f2.destroy(), self.customer_orderreport(p)])
        b4.grid(row=4, column=0, sticky="E", pady=20, columnspan=2)
        b5 = Button(self.f2, text="Back", height=3, width=40)
        if (p == 1):
            b5.config(command=lambda: [self.f2.destroy(), self.employeescreen()])
        else:
            b5.config(command=lambda: [self.f2.destroy(), self.adminscreen()])
        b5.grid(row=5, column=0, sticky="E", pady=20, columnspan=2)

    def add_userscreen(self):
        self.cu = self.db.cursor()
        self.f4 = Frame(self.window)
        self.f4.grid(row=0, column=0)
        self.f4.grid_rowconfigure(0, minsize=200)
        self.window.grid_columnconfigure(0, weight=1)
        l1 = Label(self.f4, text="Add User")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, sticky="N")

        l2 = Label(self.f4, text="User name")
        l2.configure(font=("Arial", 14))
        l2.grid(row=1, column=0, sticky="E", pady=10)

        v1 = StringVar()
        e1 = Entry(self.f4, width=30, textvariable=v1)
        e1.grid(row=1, column=1, sticky="W", padx=20)

        l3 = Label(self.f4, text="User Password")
        l3.configure(font=("Arial", 14))
        l3.grid(row=2, column=0, sticky="E", pady=10)

        v2 = StringVar()
        e2 = Entry(self.f4, width=30, textvariable=v2, show="*")
        e2.grid(row=2, column=1, sticky="W", padx=20)

        l4 = Label(self.f4, text="User type")
        l4.configure(font=("Arial", 14))
        l4.grid(row=3, column=0, sticky="E", pady=10)

        clicked = StringVar(value="")
        o = OptionMenu(self.f4, clicked, *["             Admin               ", "               Employee               "])
        o.config(width=20)
        o.grid(row=3, column=1, sticky="W", padx=20)

        l5 = Label(self.f4, text="", fg="red")
        l5.configure(font=("Arial", 14))
        l5.grid(row=5, column=0, pady=10, columnspan=2)

        b1 = Button(self.f4, text="Add User", height=3, width=20, command=lambda: self.add_user(e1, e2, clicked, l5))
        b1.grid(row=4, column=0, pady=20)
        b2 = Button(self.f4, text="Back", height=3, width=20, command=lambda: [self.f4.destroy(), self.adminscreen()])
        b2.grid(row=4, column=1, pady=20)

    def remove_employeescreen(self):
        self.cu = self.db.cursor()
        self.f3 = Frame(self.window)
        self.f3.grid(row=0, column=0)
        self.f3.grid_rowconfigure(0, minsize=200)
        self.window.grid_columnconfigure(0, weight=1)
        l1 = Label(self.f3, text="Remove Employee")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, sticky="N")
        l3 = Label(self.f3, text="Employee name")
        l3.configure(font=("Arial", 14))
        l3.grid(row=1, column=0, sticky="E", pady=10)

        v = StringVar()
        e1 = Entry(self.f3, width=30, textvariable=v)
        e1.grid(row=1, column=1, sticky="W", padx=20)

        l4 = Label(self.f3, text="", fg="red")
        l4.configure(font=("Arial", 14))
        l4.grid(row=3, column=0, pady=10, columnspan=2)

        b1 = Button(self.f3, text="Remove Employee", height=3, width=20, command=lambda: self.remove_employee(e1, l4))
        b1.grid(row=2, column=0, pady=20)
        b2 = Button(self.f3, text="Back", height=3, width=20, command=lambda: [self.f3.destroy(), self.adminscreen()])
        b2.grid(row=2, column=1, pady=20)

    def remove_employee(self, e1, l4):
        name = e1.get()
        # FIX: parameterized query — prevents SQL injection
        cu = self.db.cursor()
        cu.execute("SELECT * FROM Users WHERE Name = %s", (name,))
        result = cu.fetchall()
        if result == []:
            l4.config(text="No user exists")
        else:
            r = messagebox.askquestion("Form", "Do you want to Continue", icon="info")
            if r == "yes":
                cu.execute("DELETE FROM Users WHERE Name = %s", (name,))
                self.db.commit()
                l4.config(text="User removed")
        e1.delete(0, END)

    def employeescreen(self):
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=100)
        self.window.grid_columnconfigure(0, weight=1)
        l1 = Label(self.f2, text="Employee Menu")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, sticky="N")
        b1 = Button(self.f2, text="Add Product", height=3, width=40, command=lambda: [self.f2.destroy(), self.add_product()])
        b1.grid(row=1, column=0, sticky="E", pady=20, columnspan=2)
        b2 = Button(self.f2, text="Edit Product", height=3, width=40, command=lambda: [self.f2.destroy(), self.edit_product()])
        b2.grid(row=2, column=0, sticky="E", pady=20, columnspan=2)
        b3 = Button(self.f2, text="Customer Order", height=3, width=40, command=lambda: [self.f2.destroy(), self.customerorder()])
        b3.grid(row=3, column=0, sticky="E", pady=20, columnspan=2)
        b4 = Button(self.f2, text="View Stats", height=3, width=40, command=lambda: [self.f2.destroy(), self.view_stats(1)])
        b4.grid(row=4, column=0, sticky="E", pady=20, columnspan=2)
        b5 = Button(self.f2, text="Log Out", height=3, width=40, command=lambda: [self.f2.destroy(), self.loginscreen()])
        b5.grid(row=5, column=0, sticky="E", pady=20, columnspan=2)

    def validate1(self, value):
        # FIX: parameterized query
        cu = self.db.cursor()
        if not value.isnumeric():
            self.l9.config(text="Product Id must be integer")
            self.work = False
            return False
        cu.execute("SELECT * FROM Products WHERE P_Id = %s", (int(value),))
        if cu.fetchone() is not None:
            self.l9.config(text="Product Id exists")
            self.work = False
            return False
        self.l9.config(text="")
        self.work = True
        return True

    def validate2(self, value):
        # FIX: parameterized query
        cu = self.db.cursor()
        if not value.isnumeric():
            self.l10.config(text="Product Id must be integer")
            self.work = False
            return False
        cu.execute("SELECT * FROM Products WHERE P_Id = %s", (int(value),))
        if cu.fetchone() is None:
            self.l10.config(text="Product Id does not exist")
            self.work = False
            return False
        self.l10.config(text="")
        self.work = True
        return True

    def add_product(self):
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=200)
        self.window.grid_columnconfigure(0, weight=1)
        valid1 = (self.window.register(self.validate1), "%P")

        l1 = Label(self.f2, text="New Product")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, sticky="N")
        l2 = Label(self.f2, text="Product Id")
        l2.configure(font=("Arial", 14))
        l2.grid(row=1, column=0, sticky="E")
        v1 = StringVar()
        self.e1 = Entry(self.f2, validate='focusout', width=30, textvariable=v1, validatecommand=valid1)
        self.e1.grid(row=1, column=1, sticky="W", padx=20)

        l3 = Label(self.f2, text="Product Name")
        l3.configure(font=("Arial", 14))
        l3.grid(row=2, column=0, sticky="E")
        v2 = StringVar()
        self.e2 = Entry(self.f2, width=30, textvariable=v2)
        self.e2.grid(row=2, column=1, sticky="W", padx=20)

        l4 = Label(self.f2, text="Supplier Name")
        l4.configure(font=("Arial", 14))
        l4.grid(row=3, column=0, sticky="E")
        v3 = StringVar()
        self.e3 = Entry(self.f2, width=30, textvariable=v3)
        self.e3.grid(row=3, column=1, sticky="W", padx=20)

        l5 = Label(self.f2, text="Quantity")
        l5.configure(font=("Arial", 14))
        l5.grid(row=4, column=0, sticky="E")
        v4 = StringVar()
        self.e4 = Spinbox(self.f2, width=30, from_=0, to=10000000, textvariable=v4)
        self.e4.grid(row=4, column=1, sticky="W", padx=20)

        l6 = Label(self.f2, text="Product Cost")
        l6.configure(font=("Arial", 14))
        l6.grid(row=5, column=0, sticky="E")
        v5 = StringVar()
        self.e5 = Entry(self.f2, width=30, textvariable=v5)
        self.e5.grid(row=5, column=1, sticky="W", padx=20)

        l7 = Label(self.f2, text="MRP")
        l7.configure(font=("Arial", 14))
        l7.grid(row=6, column=0, sticky="E")
        v6 = StringVar()
        self.e6 = Entry(self.f2, width=30, textvariable=v6)
        self.e6.grid(row=6, column=1, sticky="W", padx=20)

        l8 = Label(self.f2, text="Purchase date")
        l8.configure(font=("Arial", 14))
        l8.grid(row=7, column=0, sticky="E")
        v7 = StringVar()
        cal = DateEntry(self.f2, selectmode='day', textvariable=v7, width=15)
        cal.grid(row=7, column=1, padx=15, sticky="W")

        b1 = Button(self.f2, text="Add Product", height=3, width=20, command=lambda: [self.addprod(v1, v2, v3, v4, v5, v6, cal)])
        b1.grid(row=8, column=0, sticky="E", pady=50)

        b2 = Button(self.f2, text="Back", height=3, width=20, command=lambda: [self.f2.destroy(), self.employeescreen()])
        b2.grid(row=8, column=1, sticky="E", pady=50)
        self.l9 = Label(self.f2, text="", fg="red")
        self.l9.configure(font=("Arial", 14))
        self.l9.grid(row=9, column=0, columnspan=2)

    def addprod(self, v1, v2, v3, v4, v5, v6, cal):
        if self.work:
            cu = self.db.cursor()
            # FIX: use v6 (MRP) as SalePrice — was incorrectly using v5 (Purchase Cost)
            # FIX: parameterized query
            cu.execute(
                "INSERT INTO Products VALUES (%s, %s, %s, %s)",
                (int(v1.get()), v2.get(), int(v6.get()), v3.get())
            )
            self.db.commit()
            self.storage(v1, v2, v4, v5, cal)
        else:
            self.l9.config(text="Invalid Product Id")

    def storage(self, v1, v2, v4, v5, cal):
        cu = self.db.cursor()
        purchase_date = "{0}".format(cal.get_date())
        year, month, day = map(int, purchase_date.split("-"))
        purchase_date = datetime.date(year, month, day)
        # FIX: parameterized query
        cu.execute(
            "INSERT INTO Storage VALUES (%s, %s, %s, %s, %s, %s)",
            (int(v1.get()), v2.get(), int(v5.get()), int(v4.get()), int(v4.get()), purchase_date)
        )
        self.db.commit()
        self.l9.config(text="Product Added")

    def edit_product(self):
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=200)
        self.window.grid_columnconfigure(0, weight=1)
        valid1 = (self.window.register(self.validate2), "%P")

        l1 = Label(self.f2, text="Edit Product")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, sticky="N")

        l2 = Label(self.f2, text="Product Id")
        l2.configure(font=("Arial", 14))
        l2.grid(row=1, column=0, sticky="E")
        v1 = StringVar()
        self.e1 = Entry(self.f2, validate='focusout', width=30, textvariable=v1, validatecommand=valid1)
        self.e1.grid(row=1, column=1, sticky="W", padx=20)

        l5 = Label(self.f2, text="New Quantity")
        l5.configure(font=("Arial", 14))
        l5.grid(row=4, column=0, sticky="E")
        v4 = StringVar()
        self.e4 = Spinbox(self.f2, width=30, from_=0, to=10000000, textvariable=v4)
        self.e4.grid(row=4, column=1, sticky="W", padx=20)

        b1 = Button(self.f2, text="Edit Product", height=3, width=20, command=lambda: [self.edit(v1, v4)])
        b1.grid(row=8, column=0, pady=20)

        b2 = Button(self.f2, text="Show Products", height=3, width=20, command=lambda: [self.f2.destroy(), self.storagereport(2)])
        b2.grid(row=8, column=1, pady=20)

        b3 = Button(self.f2, text="Delete Product", height=3, width=20, command=lambda: [self.deleteprod(v1)])
        b3.grid(row=9, column=0, pady=20)

        b3 = Button(self.f2, text="Back", height=3, width=20, command=lambda: [self.f2.destroy(), self.employeescreen()])
        b3.grid(row=9, column=1, pady=20)

        self.l10 = Label(self.f2, text="", fg="red")
        self.l10.configure(font=("Arial", 14))
        self.l10.grid(row=10, column=0, columnspan=2)

    def edit(self, v1, v4):
        if self.work:
            cu = self.db.cursor()
            # FIX: parameterized query
            cu.execute(
                "UPDATE Storage SET CurrentQuantity = CurrentQuantity + %s WHERE P_Id = %s",
                (int(v4.get()), int(v1.get()))
            )
            self.db.commit()
            self.l10.config(text="Quantity Updated")
        else:
            self.l10.config(text="Invalid Product Id")

    def deleteprod(self, v1):
        if self.work:
            cu = self.db.cursor()
            # FIX: parameterized query + added missing commit
            cu.execute("DELETE FROM Products WHERE P_Id = %s", (int(v1.get()),))
            self.db.commit()
            self.l10.config(text="Product deleted")
        else:
            self.l10.config(text="Invalid Product Id")

    def add_user(self, e1, e2, clicked, l5):
        name = e1.get()
        password = e2.get()
        cu = self.db.cursor()
        t = clicked.get().strip()
        if not name:
            l5.config(text="No name of user")
        elif not t:
            l5.config(text="User type not selected")
        else:
            # FIX: hash password with bcrypt before storing
            # FIX: parameterized query + AUTO_INCREMENT handles IdNo
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cu.execute(
                "INSERT INTO Users (Name, UserType, password) VALUES (%s, %s, %s)",
                (name, t, hashed)
            )
            self.db.commit()
            l5.config(text="User Added")
        e1.delete(0, END)
        e2.delete(0, END)
        clicked.set("")

    def customerorder(self):
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=200)
        self.window.grid_columnconfigure(0, weight=1)
        valid1 = (self.window.register(self.validate1), "%P")

        l1 = Label(self.f2, text="Order")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, sticky="N")

        l4 = Label(self.f2, text="Customer Name")
        l4.configure(font=("Arial", 14))
        l4.grid(row=3, column=0, sticky="E")
        v6 = StringVar()
        self.e3 = Entry(self.f2, width=30, textvariable=v6)
        self.e3.grid(row=3, column=1, sticky="W", padx=20)

        l5 = Label(self.f2, text="Number of products")
        l5.configure(font=("Arial", 14))
        l5.grid(row=4, column=0, sticky="E")
        v4 = StringVar()
        self.e4 = Spinbox(self.f2, width=30, from_=0, to=10000000, textvariable=v4)
        self.e4.grid(row=4, column=1, sticky="W", padx=20)

        l8 = Label(self.f2, text="Sale date")
        l8.configure(font=("Arial", 14))
        l8.grid(row=5, column=0, sticky="E")
        v5 = StringVar()
        cal = DateEntry(self.f2, selectmode='day', textvariable=v5, width=15)
        cal.grid(row=5, column=1, padx=15, sticky="W")

        b1 = Button(self.f2, text="Order", height=3, width=20, command=lambda: [self.order(v6, v4, cal)])
        b1.grid(row=6, column=0, sticky="E", pady=50)

        b2 = Button(self.f2, text="Back", height=3, width=20, command=lambda: [self.f2.destroy(), self.employeescreen()])
        b2.grid(row=6, column=1, sticky="E", pady=50)
        self.l9 = Label(self.f2, text="", fg="red")
        self.l9.configure(font=("Arial", 14))
        self.l9.grid(row=9, column=0, columnspan=2)

    def order(self, v6, v4, cal):
        cal = cal.get_date()
        n = int(v4.get())
        self.f2.destroy()
        self.f2 = Frame(self.window)
        self.f2.grid(row=0, column=0)
        self.f2.grid_rowconfigure(0, minsize=200)
        self.window.grid_columnconfigure(0, weight=1)
        l1 = Label(self.f2, text="Order")
        l1.configure(font=("Arial", 26))
        l1.grid(row=0, column=0, columnspan=2, sticky="N")
        v1 = [None for i in range(n)]
        v3 = [None for i in range(n)]
        valid1 = (self.window.register(self.validate2), "%P")
        for i in range(1, n + 1):
            l2 = Label(self.f2, text="Product Id")
            l2.configure(font=("Arial", 14))
            l2.grid(row=i, column=0, sticky="E")
            v1[i - 1] = StringVar()
            e1 = Entry(self.f2, validate='focusout', width=20, textvariable=v1[i - 1], validatecommand=valid1)
            e1.grid(row=i, column=1, sticky="W", padx=20)

            l5 = Label(self.f2, text="Quantity")
            l5.configure(font=("Arial", 14))
            l5.grid(row=i, column=2, sticky="E")
            v3[i - 1] = StringVar()
            e4 = Spinbox(self.f2, width=20, from_=0, to=10000000, textvariable=v3[i - 1])
            e4.grid(row=i, column=3, sticky="W", padx=20)

        b1 = Button(self.f2, text="Add Bill", height=3, width=20, command=lambda: [self.addbill(v1, v3, n, cal, v6)])
        b1.grid(row=n + 1, column=0, sticky="E", pady=50, columnspan=2)

        b2 = Button(self.f2, text="Back", height=3, width=20, command=lambda: [self.f2.destroy(), self.employeescreen()])
        b2.grid(row=n + 1, column=2, sticky="W", pady=50, columnspan=2, padx=15)
        self.l10 = Label(self.f2, text="", fg="red")
        self.l10.configure(font=("Arial", 14))
        self.l10.grid(row=9, column=0, columnspan=2)

    def addbill(self, v1, v3, n, cal, v6):
        cu = self.db.cursor()
        cu.execute("SELECT MAX(BillNo) FROM CustomerOrder")
        r_count = cu.fetchone()[0]
        billno = 1 if r_count is None else r_count + 1
        total1 = 0
        for i in range(n):
            quantity = int(v3[i].get())
            productid = int(v1[i].get())
            user_id = v6.get()
            saledate = "{0}".format(cal)
            year, month, day = map(int, saledate.split("-"))
            saledate = datetime.date(year, month, day)

            cu = self.db.cursor()
            # FIX: stock validation — prevent negative stock
            cu.execute("SELECT CurrentQuantity FROM Storage WHERE P_Id = %s", (productid,))
            row = cu.fetchone()
            if row is None or row[0] < quantity:
                self.l10.config(text=f"Insufficient stock for product {productid}")
                return

            # FIX: parameterized queries
            cu.execute("SELECT ProductName FROM Products WHERE P_Id = %s", (productid,))
            pname = cu.fetchone()[0]
            cu.execute("SELECT SalePrice FROM Products WHERE P_Id = %s", (productid,))
            total = cu.fetchone()[0] * quantity
            total1 += total
            cu.execute(
                "INSERT INTO CustomerOrder VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (productid, pname, user_id, billno, quantity, saledate, total)
            )
            cu.execute(
                "UPDATE Storage SET CurrentQuantity = CurrentQuantity - %s WHERE P_Id = %s",
                (quantity, productid)
            )
            self.db.commit()
        self.l10.config(text=f"Total = {total1}")


print("INVENTORY MANAGEMENT SYSTEM")
g = gui()
