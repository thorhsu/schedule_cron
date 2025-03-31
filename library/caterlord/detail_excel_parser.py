import pandas as pd
import os

from tqdm import tqdm
from datetime import datetime
from sqlalchemy import create_engine, text

import settings.settings as settings

mysql_engine = create_engine(f"mysql+pymysql://{settings.DATABASES['sharetea_mysql']['USER']}:{settings.DATABASES['sharetea_mysql']['PASSWORD']}@{settings.DATABASES['sharetea_mysql']['HOST']}:{settings.DATABASES['sharetea_mysql']['PORT']}/{settings.DATABASES['sharetea_mysql']['DBNAME']}")
# print('mysql', f"mysql+pymysql://{settings.DATABASES['sharetea_mysql']['USER']}:{settings.DATABASES['sharetea_mysql']['PASSWORD']}@{settings.DATABASES['sharetea_mysql']['HOST']}:{settings.DATABASES['sharetea_mysql']['PORT']}/{settings.DATABASES['sharetea_mysql']['DBNAME']}")
FILES4PARSE = settings.FILES4PARSE
a = []
df_cust = pd.read_sql(
    text("select ps3 shopId, substring(nam_custs, 4) shopName from cust where nam_custs like '%UG%'"),
    con=mysql_engine)
shop_dict = df_cust.set_index('shopName').to_dict()['shopId']

def get_shop_id(shop_name: str) -> str:
    if shop_dict.get(str(shop_name)):
        return str(shop_dict[str(shop_name)])
    for key, value in shop_dict.items():
        if str(key) in shop_name:
            return str(value)
        return ""


def excel_data_importer(folder_path: str = FILES4PARSE) -> bool:
    files = os.listdir(folder_path)
    # only excel and exclude today's file
    # get today and format to %Y-%m-%d
    today = datetime.today().strftime("%Y-%m-%d")
    files = [file for file in filter(lambda x: x.endswith(".xlsx")
                and x.startswith("SalesDetailReport")
                and x[-15:-5] <= today, files)]
    # sort files from a to z
    sorted_files = sorted(files, key=lambda f: f[-15:-5])
    error_rows = []  # 儲存錯誤行的索引
    for file in sorted_files:
        df_txDate = pd.read_excel(os.path.join(folder_path, file), skiprows=1, nrows=1,
                           usecols='B:B',               names=["txDate",])
        df = pd.read_excel(os.path.join(folder_path, file), skiprows=6,
                           usecols='B:M',
                           names=["shopName", "transactionId", "itemCode", "itemName", "category", "department", "price", "qty", "amount", "codeChange", "orderUser", "orderDateTime"])

        txDate = str(df_txDate['txDate'].values[0].split(":")[1]).strip()
        df['txDate'] = txDate
        df.sort_values(by=['transactionId'], inplace=True)
        df['shopId'] = df.apply(lambda row: get_shop_id(str(row["shopName"])), axis=1)
        df['filename'] = file
        df['isParsed'] = False
        df['createdAt'] = datetime.now()

        with mysql_engine.connect() as conn:
            seq_no = 0
            prev_id = None
            for index, row in tqdm(df.iterrows(), total=len(df), desc="Migrating Data"):
                try:
                    seq_no += 1
                    row_dict = row.to_dict()
                    if row_dict['shopName'] == "總計":
                        continue
                    row_dict['transactionId'] = str(int(row_dict['transactionId']))

                    if prev_id != row_dict['transactionId']:
                        seq_no = 0
                    row_dict['seqNo'] = seq_no
                    tx_date_arr = row_dict['txDate'].split("/")
                    row_dict['id'] = f"{tx_date_arr[0]}{int(tx_date_arr[1]):02}{int(tx_date_arr[2]):02}_{row_dict["shopId"]}_{row_dict["transactionId"]}_{seq_no:03}"
                    row_dict['txDate'] = f"{int(tx_date_arr[0]) - 1911}/{int(tx_date_arr[1]):02}/{int(tx_date_arr[2]):02}"
                    prev_id = row_dict['transactionId']
                    df_single = pd.DataFrame([row_dict])  # 單行 DataFrame
                    df_single.to_sql(f"sales_detail", conn, if_exists="append", index=False)

                except Exception as e:
                    error_rows.append((file, index, repr(e)))  # 記錄完整的錯誤行
                    print(f"{file} Row {index} skipped due to error: {repr(e)}")
        # backup_dir = os.path.join(folder_path, 'backup')

        # Ensure backup directory exists
        # if not os.path.exists(backup_dir):
        #     os.makedirs(backup_dir)

        # Move file to backup directory
        # shutil.move(os.path.join(folder_path, file), os.path.join(backup_dir, file))
        os.remove(os.path.join(folder_path, file))

    # 儲存錯誤行到 CSV，方便後續修復
    if error_rows:
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_df = pd.DataFrame(error_rows, columns=["File", "Row_Index", "Error_Message"])
        error_df.to_csv(f"excel_parse_erro_{current_time}.csv", index=False)
        print(f"Some rows failed. Check excel_parse_errors_{current_time}.csv for details.")
    else:
        print("Migration completed successfully!")
    return True