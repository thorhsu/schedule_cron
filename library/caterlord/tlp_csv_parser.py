import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime, timedelta
from sqlalchemy import create_engine

import settings.settings as settings

mysql_engine = create_engine(f"mysql+pymysql://{settings.DATABASES['sharetea_mysql']['USER']}:{settings.DATABASES['sharetea_mysql']['PASSWORD']}@{settings.DATABASES['sharetea_mysql']['HOST']}:{settings.DATABASES['sharetea_mysql']['PORT']}/{settings.DATABASES['sharetea_mysql']['DBNAME']}")
# print('mysql', f"mysql+pymysql://{settings.DATABASES['sharetea_mysql']['USER']}:{settings.DATABASES['sharetea_mysql']['PASSWORD']}@{settings.DATABASES['sharetea_mysql']['HOST']}:{settings.DATABASES['sharetea_mysql']['PORT']}/{settings.DATABASES['sharetea_mysql']['DBNAME']}")

a = []
def data_importer(folder_path: str="C:/Users/thorhsu/temp/"):
    today = datetime.today().strftime("%Y%m%d")
    files = os.listdir(folder_path)
    # only txt
    files = [file for file in filter(lambda x: x.endswith(".txt")
                and x.startswith("tlps")
                and x[-13:-5] < today, files)]
    # sort files from a to z
    sorted_files = sorted(files, key=lambda f: f[-13:-4])
    file_reads = {
        "a": ['txDate', 'txTime', 'shopId', 'shopName', 'itemCode', 'itemName', 'price', 'qty', 'amount', 'orderUserId', 'maleCount', 'femaleCount', 'category', 'discountAmount', 'cost', 'txCategory', 'transactionId',],
        "e": ['shopId', 'shopName', 'txDate', 'txTime', 'orderUserId', 'transactionId', 'itemCode', 'qty', 'price', 'amount', 'cash', 'creditCard', 'coupon', 'chipCard', 'payWay5', 'payWay6', 'payWay7', 'payWay8', 'payWayCategory'],
        "f": ['txDate', 'txTime', 'shopId', 'shopName', 'itemCode', 'itemName', 'price', 'qty', 'amount', 'orderUserId', 'maleCount', 'femaleCount', 'category', 'discountAmount', 'cost', 'txCategory', 'transactionId', 'useType',],
        "h": ['txDate', 'txTime', 'shopId', 'shopName', 'itemCode', 'itemName', 'price', 'qty', 'amount', 'orderUserId', 'maleCount', 'femaleCount', 'category', 'discountAmount', 'cost', 'txCategory', 'transactionId',],
    }
    error_rows = []  # 儲存錯誤行的索引
    start = datetime.now()
    for file in sorted_files:
        if datetime.now() > start + timedelta(minutes=50):
            break
        last_char = file[-5:-4]
        df = pd.read_csv(os.path.join(folder_path, file), encoding="cp950", sep=",", names=file_reads[last_char])
        df.sort_values(by=['transactionId', 'txDate', 'txTime'], inplace=True)
        df['txId'] = df.apply(lambda row: str(row['txDate']) + "_" + str(row["shopId"]) + "_" + str(row['transactionId']), axis=1)
        df['txDateTime'] = df.apply(
            lambda row: (str(int(row['txDate'][:3]) + 1911) + row['txDate'][3:]).replace("/", "-") + " " + str(
                row["txTime"]), axis=1)

        df['filename'] = file
        df['isParsed'] = False
        df['createdAt'] = datetime.now()

        with mysql_engine.connect() as conn:
            seq_no = 0
            prev_id = None
            for index, row in tqdm(df.iterrows(), total=len(df), desc=f"{file}"):
                try:
                    seq_no += 1
                    row_dict = row.to_dict()
                    if prev_id != row_dict['transactionId']:
                        seq_no = 0
                    row_dict['seqNo'] = seq_no
                    row_dict['id'] = f"{(str(int(row_dict['txDate'][:3]) + 1911) + row_dict['txDate'][3:]).replace("/", "")}_{row_dict["shopId"]}_{row_dict["transactionId"]}_{seq_no:03}"
                    prev_id = row_dict['transactionId']
                    df_single = pd.DataFrame([row_dict])  # 單行 DataFrame
                    df_single.to_sql(f"tlps_{last_char}", conn, if_exists="append", index=False)
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
        error_df.to_csv(f"csv_parse_errors.csv_{current_time}", index=False)
        print("Some rows failed. Check csv_parse_errors.csv for details.")
    else:
        print("Migration completed successfully!")
    return True