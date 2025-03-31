import oracledb
import pandas as pd
from library.caterlord.migrate_from_erp import migrate_from_erp
from sqlalchemy import create_engine
from tqdm import tqdm

# oracle thick mode must point out where is the oracle client
# oracle 11.8
oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient-basic-windows.x64-23.7.0.25.01\instantclient_23_7")  # Change path as needed
# 資料庫連線相關參數
host = "192.168.1.25"
port = 1521  # Oracle 的預設連接埠
service_name = "orcl"
username = "querier"
password = "YhBrY23dhMP2"

# 建立連線
dsn = f"{host}:{port}/{service_name}"  # 格式為 主機:連接埠/服務名稱
def test_conection():
    migrate_from_erp()