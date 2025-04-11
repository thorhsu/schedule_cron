import pandas as pd
import os
import pyodbc
from tqdm import tqdm

SERVER = '192.168.1.12'
DATABASE = 'POSLF'
USERNAME = 'sa'
PASSWORD = 'dsc@80676602'

connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};Encrypt=no;TrustServerCertificate=no;Connection Timeout=30;'
print(connectionString)
# conn = pyodbc.connect(connectionString)


def update_shop_franchise(folder_path: str="C:/Users/thorhsu/temp/"):
    file = os.path.join(folder_path, "JGG_ID_FRANCHISE.xlsx")
    df = pd.read_excel(file)

    with pyodbc.connect(connectionString) as conn:
        cursor = conn.cursor()
        for index, row in tqdm(df.iterrows(), total=len(df), desc="Migrating Data"):
            try:
                row_dict = row.to_dict()
                shop_id = row_dict["ShopId"]
                direct = row_dict["direct"]
                sql = "UPDATE POS10 SET direct = ? WHERE POS10003=?"
                print(sql)
                cursor.execute(sql, direct, shop_id)
            except Exception as e:
                print(f"{file} Row {index} skipped due to error: {repr(e)}")
                return False

    print(f"Updated completed successfully!")
    return True

if __name__ == '__main__':
    update_shop_franchise()


