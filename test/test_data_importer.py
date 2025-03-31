import pandas as pd
import os
from datetime import datetime
from sqlalchemy import create_engine
from tqdm import tqdm

dtype= {
'TxSalesDetailId': str,
'AccountId': str,
'TxSalesHeaderId': str,
'PreviousTxSalesHeaderId': str,
'SeqNo': str,
'IsSubItem': str,
'IsModifier': str,
'ParentTxSalesDetailId': str,
'SubItemLevel': str,
'ItemPath': str,
'ItemSetRunningIndex': str,
'ItemOrderRunningIndex': str,
'OrderUserId': str,
'OrderUserName': str,
'ItemId': str,
'CategoryId': str,
'ItemCode': str,
'ItemName': str,
'ItemNameAlt2': str,
'Enabled': str,
'Voided': str,
'PrintedKitchen': str,
'PrintedKitchenByUserId': str,
'PrintedKitchenByUserName': str,
'DisabledReasonId': str,
'DisabledReasonDesc': str,
'DisabledByUserId': str,
'DisabledByUserName': str,
'ChaseCount': str,
'ChaseUserId': str,
'ChaseUserName': str,
'CreatedBy': str,
'ModifiedBy': str,
'IsPromoComboItem': str,
'ShopId': str,
'ItemNameAlt': str,
'ItemNameAl3': str,
'ItemNameAl4': str,
'ItemPosName': str,
'ItemPosNameAlt': str,
'DepartmentId': str,
'DepartmentName': str,
'IsPointPaidItem': str,
'AmountPoint': str,
'Point': str,
'IsNonTaxableItem': str,
'IsItemOnHold': str,
'ItemOnHoldUserId': str,
'ItemOnHoldUserName': str,
'IsItemFired': str,
'ItemFiredUserId': str,
'ItemFiredUserName': str,
'TakeawaySurcharge': str,
'IsItemShowInKitchenChecklist': str,
'IsPrepaidRechargeItem': str,
'ApiGatewayName': str,
'ApiGatewayRefId': str,
'ApiGatewayRefRemark': str,
'AmountItemDiscount': str,
'AmountItemTaxation': str,
'AmountItemSurcharge': str,
'PromoHeaderId': str,
'PromoDeductAmount': str,
'PromoQty': str,
'PromoRevenueOffset': str,
'CategoryName': str,
'OrderSourceTypeId': str,
'ItemPublicDisplayName': str,
'ItemPublicDisplayNameAlt': str,
'ItemPublicPrintedName': str,
'ItemPublicPrintedNameAlt': str,
'LinkedItemOrderRunningIndex': str,
'LinkedItemSetRunningIndex': str,
'LinkedItemId': str,
'IsPriceInPercentage': str,
'OrderSourceRefId': str,
'DepartmentRevenueAmount': str,
'PromoCode': str,
'PromoName': str,
'itemCourseIndex': str,
'priceRuleGroupId': str,
'priceRuleGroupCode': str,
'priceRuleGroupName': str,
'OrderBatchTag': str,
'IsTxOnHold': str,
'SubDepartmentId': str,
'SubDepartmentName': str,
'ApiGatewayRefCode': str,
'ApiGatewayResponseCode': str,
'IsVariance': str,
'GroupHeaderId': str,
'GroupBatchName': str,
'DiscountId': str,
'DiscountName': str,
'SOPLookupPath': str,
'IsNonSalesItem': str
}

def test_data_importer(folder_path: str="C:/Users/thorhsu/temp/"):
    # today yyyyMMdd
    this_year = datetime.now().strftime("%Y")
    files = os.listdir(folder_path)
    # only xlsx file
    for file in filter(lambda x: x.endswith(".xlsx") or x.endswith(".csv"), files):
            if "TxSalesDetail" in file:
                print(file)
                file_name = file.split(".")[0]
                today = f"{this_year}{file_name.split("_")[1]}" if len(file_name.split("_")[1]) == 4  else file_name.split("_")[1]
                df = None
                if file.endswith(".xlsx"):
                    df = pd.read_excel(os.path.join(folder_path, file), dtype=dtype)
                else:
                    df = pd.read_csv(os.path.join(folder_path, file), dtype=dtype)
                df['filename'] = file
                df['id'] = df.apply(lambda row: today + "_" + str(row["ShopId"]) + "_" + str(row['TxSalesDetailId']) , axis=1)
                df['TxSalesHeader_id'] = df.apply(lambda row: today + "_" + str(row["ShopId"]) + "_" + str(row['TxSalesHeaderId']) , axis=1)
                # df.insert(1, "created_at", datetime.now(), True)
                # df.insert(2, "updated_at", datetime.now(), True)
                print(df.head())
                # 連接 MySQL
                mysql_engine = create_engine("mysql+pymysql://root:root@localhost:3306/caterlordpos")
                error_rows = []  # 儲存錯誤行的索引
                with mysql_engine.connect() as conn:
                    for index, row in tqdm(df.iterrows(), total=len(df), desc="Migrating Data"):
                        try:
                            row_dict = row.to_dict()
                            df_single = pd.DataFrame([row_dict])  # 單行 DataFrame
                            df_single.to_sql("txsalesdetails", conn, if_exists="append", index=False)
                            # df_single = pd.DataFrame([row_dict])  # 單行 DataFrame
                            # df_single.to_sql("txsalesdetails", conn, if_exists="append", index=False)
                        except Exception as e:
                            error_rows.append((index, str(e)))  # 記錄錯誤的行
                            print(f"Row {index} skipped due to error: {e}")

