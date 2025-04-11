"""
Connects to a SQL database using pyodbc
"""
import pyodbc
SERVER = '192.168.1.12'
DATABASE = 'POSLF'
USERNAME = 'sa'
PASSWORD = 'dsc@80676602'

connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Encrypt=no;TrustServerCertificate=no;Connection Timeout=30;'
print(connectionString)
conn = pyodbc.connect(connectionString)

