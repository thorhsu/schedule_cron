import os
from datetime import datetime
import oracledb
import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm
import settings.settings as settings

# 連接 MySQL
mysql_engine = create_engine(f"mysql+pymysql://{settings.DATABASES['sharetea_mysql']['USER']}:{settings.DATABASES['sharetea_mysql']['PASSWORD']}@{settings.DATABASES['sharetea_mysql']['HOST']}:{settings.DATABASES['sharetea_mysql']['PORT']}/{settings.DATABASES['sharetea_mysql']['DBNAME']}")

# oracle thick mode must point out where is the oracle client
print("oracle client:", settings.ORACLE_CLIENT)
# oracle 11.8
oracledb.init_oracle_client(lib_dir=settings.ORACLE_CLIENT)  # Change path as needed
# 資料庫連線相關參數
host = "192.168.1.25"
port = 1521  # Oracle 的預設連接埠
service_name = "orcl"
username = "querier"
password = "YhBrY23dhMP2"

# 建立連線
dsn = f"{host}:{port}/{service_name}"  # 格式為 主機:連接埠/服務名稱

shop_data = {
        "ShopId":
                ["6401",
                   "6426",
                   "6444",
                   "6481",
                   "6524",
                   "6525",
                   "6526",
                   "6527"
                ],
                "ShopName":
                ["忠孝敦化店",
                   "信義虎林店",
                   "信義永吉店",
                   "南陽店",
                   "羅東民權店",
                   "林口長庚店",
                   "台北大巨蛋店",
                   "士林捷運店"
        ]}
shop_df = pd.DataFrame(data=shop_data)


def migrate_from_erp():
    # 連接 Oracle
    oracle_engine = create_engine(f"oracle+oracledb://{username}:{password}@{host}:{port}/{service_name}")
    df = pd.read_sql("SELECT * FROM lf.item", oracle_engine)
    df2 = pd.read_sql("SELECT * FROM lf.cust", oracle_engine)
    error_rows = []  # 儲存錯誤行的索引
    with mysql_engine.connect() as conn:
        print('df length', len(df))
        conn.begin()
        try:
            sql = text(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'caterlordpos' AND table_name = 'item';")
            result = conn.execute(sql)
            if result.scalar() > 0:
                sql = text(f"delete from item")
                conn.execute(sql)
            sql = text(
                f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'caterlordpos' AND table_name = 'cust';")
            result = conn.execute(sql)
            if result.scalar() > 0:
                sql = text(f"delete from cust")
                conn.execute(sql)

            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"error: {repr(e)}")
            return False

        # cust
        df2.to_sql("cust", conn, if_exists="append", index=False)

        for index, row in tqdm(df.iterrows(), total=len(df), desc="Migrating Item Data"):
            try:
                row_dict = row.to_dict()
                df_single = pd.DataFrame([row_dict])  # 單行 DataFrame
                df_single.to_sql("item", conn, if_exists="append", index=False)
            except Exception as e:
                error_rows.append((index, repr(e)))  # 記錄完整的錯誤行
                print(f"Row {index} skipped due to error: {repr(e)}")


        for index, row in tqdm(shop_df.iterrows(), total=len(shop_df), desc="Update UG Data"):
            try:
                row_dict = row.to_dict()
                nam_custs = row_dict["ShopName"]
                # update cust and set shopId

                sql = text(f"UPDATE cust SET ps3 = :ShopId WHERE nam_custs = 'UG-{nam_custs}'")
                conn.execute(sql, row_dict)
            except Exception as e:
                print(f"error: {repr(e)}")
                return False
        conn.commit()
    # 儲存錯誤行到 CSV，方便後續修復
    if error_rows:
        today = datetime.today().strftime("%Y-%m-%d")
        error_df = pd.DataFrame(error_rows, columns=["Row_Index", "Error_Message"])
        if not os.path.exists(f"{settings.BASE_DIR}/share/"):
            os.mkdir(f"{settings.BASE_DIR}/share/")
        if not os.path.exists(f"{settings.BASE_DIR}/share/log/"):
            os.mkdir(f"{settings.BASE_DIR}/share/log/")
        error_df.to_csv(f"{settings.BASE_DIR}/share/log/migration_erp_errors{today}.csv", index=False)
        print("Some rows failed. Check migration_errors.csv for details.")
    else:
        print("Migration completed successfully!")