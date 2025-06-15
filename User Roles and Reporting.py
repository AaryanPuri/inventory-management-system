import mysql.connector as mys
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
import sys


def view():
    global db
    cu=db.cursor()
    print("1-products report, 2-staff report, 3-storage report, 4-Customer Order Report,5-Yearly Report")
    i=input("Enter your choice : ")
    if i=="1":
        cu.execute("select * from products")
        header=cu.column_names
        cu=cu.fetchall()
        if cu == []:
            print("No Data Present in this table")
            return
        table=pd.DataFrame(cu)
        table.columns=header
        print(table)
    elif i=="2":
        cu.execute("select Idno,Name,usertype from users")
        header=cu.column_names
        cu=cu.fetchall()
        if cu == []:
            print("No Data Present in this table")
            return
        table=pd.DataFrame(cu)
        table.columns=header
        print(table)
    elif i=="3":
        cu.execute("select * from storage")
        header=cu.column_names
        cu=cu.fetchall()
        if cu == []:
            print("No Data Present in this table")
            return
        table=pd.DataFrame(cu)
        table.columns=header
        print(table)
    elif i=="4":
        cu.execute("select * from customerorder")
        header=cu.column_names
        cu=cu.fetchall()
        if cu == []:
            print("No Data Present in this table")
            return
        table=pd.DataFrame(cu)
        table.columns=header
        print(table)
    elif i=="5":
        data={}
        cu.execute(" select Year(Purchasedate) as year,(purchasecost*pqty) as cp from storage s,products p where s.productname=p.productname group by year")
        cp=cu.fetchall()
        cu=db.cursor()
        cu.execute("select year(Saledate) as year,sum(quantity*saleprice) as sp from customerorder c,products p where p.productname=c.productname group by year")
        sp=cu.fetchall()
        for i in cp:
              t=int(i[0])
              data[t]=[i[1],0]
        for i in sp:
            t=int(i[0])
            if t in data:
                data[t][1]=i[1]
            else:
                data[t]=[0,i[1]]
        print(data)
        year=list(data.keys())
        year.sort()
        cp=[]
        sp=[]
        p=[]
        for i in year:
            cp.append(data[i][0])
            sp.append(data[i][1])
            p.append(data[i][1]-data[i][0])
        br1 = np.arange(len(year)) 
        br2 = [x + 0.2 for x in br1] 
        br3 = [x + 0.2 for x in br2]
        fig = plt.figure(figsize = (10, 5))
        ax = plt.subplot()
        p1=ax.bar(br1, sp, color ='r', width = 0.2,edgecolor ='grey', label ='Sale') 
        p2=ax.bar(br2, cp, color ='g', width = 0.2,edgecolor ='grey', label ='Cost') 
        p3=ax.bar(br3, p, color ='b', width = 0.2, edgecolor ='grey', label ='Profit') 
        ax.axhline(y=0 ,color="k")
        plt.xlabel("Products") 
        plt.ylabel("Sales") 
        plt.title("Yearly Report")
        plt.xticks([r + 0.2 for r in range(len(year))], year) 
        plt.legend((p1[0],p2[0],p3[0]),("Sale","Cost","Profit"))
        plt.show()
        
    
def remove_employee():
    global db
    cu=db.cursor()
    i=input("Enter name of employee: ")

    cu.execute("Select * from Users where name = '%s'" %(i))
    result = cu.fetchall()

    if result == []:
        print("Employee Name Incorrect/Does not exist")
        return

    cu.execute("delete from users where name='%s'"%i)

def add_user():
    global db
    cu=db.cursor()
    a=input("Admin/Manager: ").lower()
    u=input("Enter username: ")
    p=input("Enter password: ")
    cu.execute("select count(*) from Users")
    r_count=cu.fetchone()[0]
    if r_count<0:
            r_count=0
    cu.execute("insert into Users values({0},'{1}','{2}','{3}')".format(r_count+1,u,a,p))
    db.commit()

def admin(u):
    print("")
    print("1-view stats, 2-remove employee, 3-Add User,4-exit")
    i=input("Enter your choice : ")
    if i=="1":
        view()
    elif i=="2":
        remove_employee()
    elif i=="3":
        add_user()
    elif i=="4":
        return True
    return False

def manager(u):
    print("")
    print("1-Add Product, 2-Edit Product, 3-Customer Order, 4-View Details, 5-Exit")
    i=input("Enter your choice : ")
    if i=="1":
        add_product()
    elif i=="2":
        edit_product()
    elif i=="3":
        customerorder()
    elif i=="4":
        view()
    elif i=="5":
        return True
    return False
    
def users():
    global db

    print("Login-L,quit-q")
    x=input("Enter your choice : ").lower()
    print("")
    if x=="l":
        cu=db.cursor()
        cu.execute("select * from Users")
        cu=cu.fetchall()
        if cu==[]:
            print("No admin assigned create admin")
            add_user()
            users()
        u=input("Enter username: ")
        p=input("Enter password: ")
        cu=db.cursor()
        cu.execute("select Name, password, usertype from Users;")
        cu=cu.fetchall()
        valid_user=0
        for i in cu:
            if u==i[0] and p==i[1]:
                valid_user=1
                if i[2]=="admin":
                    while True:
                        quit = admin(u)
                        if quit == True:
                            break
                    break
                else:
                    while True:
                        quit = manager(u)
                        if quit == True:
                            break
                    break
        if valid_user==0:
             print("Invalid username/password")
    elif x=='q':
        sys.exit(0)
            
def storage(p_name,purchase_cost,pqty,pid):
    global db
    cu=db.cursor()
    purchase_date=input("Enter purchase date(YYYY-MM-DD): ")
    year,month,day=map(int,purchase_date.split("-"))
    purchase_date=datetime.date(year,month,day)
    cu=db.cursor()
    cu.execute("insert into Storage values({0},'{1}',{2},{3},{4},'{5}')".format(pid,p_name,purchase_cost,pqty,pqty,purchase_date))
    db.commit()

def add_product():
    global db
    try:
       pid=input("enter product id: ")
       p_name=input("Enter product name: ")
       supp_name=input("Enter supplier name: ")
       pqty= input("Enter Purchase qty: ")
       product_cost=int(input("Enter product cost: "))

       saleprice=int(input("enter sale price: "))
       cu=db.cursor()
       cu.execute("insert into Products values({0},'{1}',{2},'{3}')".format(pid,p_name,saleprice,supp_name))
       db.commit()
       storage(p_name,product_cost,pqty,pid)
    except mys.IntegrityError:
        print("Product already exists")

def edit_product():
    global db
    cu=db.cursor()
    p_name=input("Enter product name : ")
    pid=input("Enter product id: ")
    cu.execute("Select * from products where ProductName = '%s' and P_Id=%s" %(p_name,pid))
    result = cu.fetchall()

    if result == []:
        print("Product does not exist")
        return

    add_quantity=input("Enter how much quantity to add: ")
    cu.execute("update storage set CurrentQuantity=CurrentQuantity+%s where Productname = '%s'"%(add_quantity,p_name))

def customerorder():
    global db
    cu=db.cursor()

    productname=input("Enter product name: ")
    pid=int(input("enter product id: "))
    cu.execute("Select * from products where ProductName = '%s' and P_Id=%s" %(productname,pid) )
    result = cu.fetchall()

    if result == []:
        print("Product does not exist")
        return
    
    quantity=int(input("Enter quantity: "))

    cu.execute("Select CurrentQuantity from Storage where Productname = '%s'" %productname)
    current_quantity = cu.fetchall()[0][0]
    
    if current_quantity == 0:
        print("Sorry this item is not available")
        return

    while quantity > current_quantity:
        print("Quantity is greater than available %d" %(current_quantity))
        quantity = int(input("Enter Updated quantity : "))

    user_id=input("Enter cutomer name: ")
    billno=int(input("Enter bill no: "))

    saledate=input("Enter sale date(YYYY-MM-DD): ")
    year,month,day=map(int,saledate.split("-"))
    saledate=datetime.date(year,month,day)
    cu=db.cursor()
    cu.execute("Select saleprice from Products where P_Id = '%s'"%pid)
    total = (cu.fetchall()[0][0])*quantity
    cu.execute("insert into CustomerOrder values({0},'{1}','{2}',{3},{4},'{5}',{6})".format(pid,productname,user_id,billno,quantity,saledate, total))
    cu.execute("update storage set CurrentQuantity=CurrentQuantity-%s where Productname = '%s'"%(quantity,productname))
    db.commit()
    
def database_create():
    global db
    db=mys.connect(host="localhost",user="root",passwd="admin")
    cu=db.cursor()
    cu.execute("create database inventory;")
    db=mys.connect(host="localhost",user="root",passwd="admin",database="inventory")
    cu=db.cursor()
    cu.execute("create table Users (IdNo int,Name varchar(20),UserType varchar(15),password varchar(300))")
    cu.execute("create table Products (P_Id int primary key,ProductName varchar(20),SalePrice int,SupplierName varchar(15))")
    cu.execute("create table Storage (P_Id int,ProductName varchar(20),PurchaseCost int,pqty int,Currentquantity int,Purchasedate date,foreign key(P_Id) references Products(P_Id))")
    cu.execute("create table CustomerOrder (P_Id int,ProductName varchar(20), Name varchar(20), BillNo int, Quantity int, SaleDate date, Total int,foreign key(P_Id) references Products(P_Id))")
    db.commit()

print("                      INVENTORY MANAGEMENT SYSTEM")
print("--------------------------------------------------------------------------------")
print("")
try:
    global db
    db=mys.connect(host="localhost",user="root",passwd="admin",database="inventory")
except:
    
    database_create()
    

while True:
    users()
