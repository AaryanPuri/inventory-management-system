# 📦 Inventory Management System

## Table of Contents
- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [User Roles](#user-roles)
- [Author](#author-)


## About the Project
An Inventory Management System built using Python and MySQL, designed to streamline and simplify inventory tracking, product management, order handling, and user role management for retail businesses or organizations.

## Features
1. User Authentication (Admin & Manager/Employee roles)
2. Add / Edit / Delete Products
3. Track Inventory Levels with stock validation
4. Customer Billing and Order Management
5. View Detailed Reports:
   - Products Report
   - Staff Report
   - Storage Report
   - Customer Order Report
   - Yearly Profit/Loss Analysis (Graphical)
6. Graphical User Interface (GUI) using tkinter
7. Command-line Interface (CLI) option for flexibility

## Tech Stack
1. Python 3.7+
2. MySQL (via mysql-connector-python)
3. tkinter (GUI)
4. pandas (Data handling)
5. numpy (Numerical operations)
6. matplotlib (Graphical reporting)
7. tkcalendar, pandastable (GUI enhancements)
8. bcrypt (Password hashing)
9. python-dotenv (Environment variable management)

## Installation
1. **Prerequisites** — Python 3.7 or higher, MySQL server

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure credentials** — Create a `.env` file in the project root:
   ```
   DB_HOST=localhost
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_DATABASE=inventory
   ```

4. **Setup database** — Run the program once. If the `inventory` database does not exist, it will be created automatically with the required tables:
   - Users
   - Products
   - Storage
   - CustomerOrder

5. **Run the application**
   - GUI: `python "Inventory Management GUI.py"`
   - CLI: `python "User Roles and Reporting.py"`

## User Roles
1. **Admin** — View reports, add/remove users, manage employees
2. **Employee/Manager** — Add/edit products, process customer orders, view inventory reports


## Author 👤
**Aaryan Puri**  
[LinkedIn](https://www.linkedin.com/in/aaryan-puri-04923a228/?profileId=ACoAADj8zrkBa2y9Dzyvyl3sUsCqr-4P-RhcAgA) • [GitHub](https://github.com/AaryanPuri) • [Email](mailto:aaryanpuri75@gmail.com)
