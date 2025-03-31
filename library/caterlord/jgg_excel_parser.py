import pandas as pd
import os
from tqdm import tqdm
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import settings.settings as settings

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
mysql_engine = create_engine(f"mysql+pymysql://{settings.DATABASES['sharetea_mysql']['USER']}:{settings.DATABASES['sharetea_mysql']['PASSWORD']}@{settings.DATABASES['sharetea_mysql']['HOST']}:{settings.DATABASES['sharetea_mysql']['PORT']}/{settings.DATABASES['sharetea_mysql']['DBNAME']}")

def update_shop_id(folder_path: str="C:/Users/thorhsu/temp/"):
    # print('mysql',
    #       f"mysql+pymysql://{settings.DATABASES['sharetea_mysql']['USER']}:{settings.DATABASES['sharetea_mysql']['PASSWORD']}@{settings.DATABASES['sharetea_mysql']['HOST']}:{settings.DATABASES['sharetea_mysql']['PORT']}/{settings.DATABASES['sharetea_mysql']['DBNAME']}")

    file = os.path.join(folder_path, "JGG_ID.xlsx")
    df = pd.DataFrame(data=shop_data)
    if not os.path.exists(file):
        print(f"File {file} does not exist. Skipping the process.")
    else:
        df = pd.read_excel(file)

    with mysql_engine.connect() as conn:
        conn.begin()
        for index, row in tqdm(df.iterrows(), total=len(df), desc="Migrating Data"):
            try:
                row_dict = row.to_dict()
                nam_custs = row_dict["ShopName"]
                shop_id = row_dict["ShopId"]
                # update cust and set shopId

                sql = text(f"UPDATE cust SET ps3 = :ShopId WHERE nam_custs = 'UG-{nam_custs}'")
                print(sql)
                conn.execute(sql, row_dict)
            except Exception as e:
                print(f"{file} Row {index} skipped due to error: {repr(e)}")
                return False
        conn.commit()

    print(f"Updated completed successfully!")
    return True
