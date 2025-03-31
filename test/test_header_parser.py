import pandas as pd
import os
from datetime import datetime
from sqlalchemy import create_engine
from tqdm import tqdm

dtype = {
  'TxSalesHeaderId': str,
  'AccountId': str,
  'ShopId': str,
  'TxCode': str,
  'ReceiptNo': str,
  'IsCurrentTx': str,
  'Voided': str,
  'Enabled': str,
  'TableId': str,
  'TableCode': str,
  'PreviousTableId': str,
  'PreviousTableCode': str,
  'SectionId': str,
  'SectionName': str,
  'CheckinUserId': str,
  'CheckinUserName': str,
  'CheckoutUserId': str,
  'CheckoutUserName': str,
  'CashierUserId': str,
  'CashierUserName': str,
  'AmountPaid': float,
  'AmountChange': float,
  'AmountSubtotal': float,
  'AmountServiceCharge': float,
  'AmountDiscount': float,
  'AmountTotal': float,
  'AmountRounding': float,
  'TxCompleted': str,
  'TxChecked': str,
  'CreatedBy': str,
  'ModifiedBy': str,
  'IsTakeAway': str,
  'TakeAwayRunningIndex': str,
  'DisabledReasonId': str,
  'DisabledReasonDesc': str,
  'DisabledByUserId': str,
  'DisabledByUserName': str,
  'WorkdayPeriodDetailId': str,
  'WorkdayPeriodName': str,
  'DiscountId': str,
  'DiscountName': str,
  'CashDrawerCode': str,
  'ReceiptPrintCount': str,
  'TxRevokeCount': str,
  'ServiceChargeId': str,
  'ServiceChargeName': str,
  'AmountTips': str,
  'IsTimeLimited': str,
  'TimeLimitedMinutes': str,
  'CusCount': str,
  'DiscountByUserId': str,
  'DiscountByUserName': str,
  'AmountPointTotal': str,
  'MemberPointRemain': str,
  'TaxationId': str,
  'TaxationName': str,
  'AmountTaxation': str,
  'AmountMinChargeOffset': str,
  'IsMinChargeOffsetWaived': str,
  'IsMinChargeTx': str,
  'IsMinChargePerHead': str,
  'MinChargeAmount': str,
  'MinChargeMemberAmount': str,
  'IsPrepaidRechargeTx': str,
  'IsInvoicePrintPending': str,
  'InvoiceNum': str,
  'OrderNum': str,
  'IsDepositTx': str,
  'TotalDepositAmount': str,
  'DepositRemark': str,
  'IsDepositOutstanding': str,
  'IsReturnTx': str,
  'HasReturned': str,
  'ReturnedTxSalesHeaderId': str,
  'NewTxSalesHeaderIdForReturn': str,
  'ApiGatewayRefId': str,
  'ApiGatewayName': str,
  'ApiGatewayRefRemark': str,
  'TableRemark': str,
  'TxSalesHeaderRemark': str,
  'TotalPaymentMethodSurchargeAmount': str,
  'IsNonSalesTx': str,
  'IsNoOtherLoyaltyTx': str,
  'StartWorkdayPeriodDetailId': str,
  'StartWorkdayPeriodName': str,
  'IsTxOnHold': str,
  'IsOdoTx': str,
  'OdoOrderToken': str,
  'AmountOverpayment': str,
  'TxStatusId': str,
  'OverridedChecklistPrinterName': str,
  'OrderSourceTypeId': str,
  'OrderSourceRefId': str,
  'OrderChannelId': str,
  'OrderChannelCode': str,
  'OrderChannelName': str,
  'ApiGatewayRefCode': str,
  'ApiGatewayResponseCode': str
}


def test_heaer_parser(folder_path: str="C:/Users/thorhsu/temp/"):
    # today yyyyMMdd
    this_year = datetime.now().strftime("%Y")
    files = os.listdir(folder_path)
    # only xlsx file
    for file in filter(lambda x: x.endswith(".xlsx") or x.endswith(".csv"), files):
            if "TxSalesHeader" in file:
                print(file)
                file_name = file.split(".")[0]
                today = f"{this_year}{file_name.split("_")[1]}" if len(file_name.split("_")[1]) == 4  else file_name.split("_")[1]
                df = None
                if file.endswith(".xlsx"):
                    df = pd.read_excel(os.path.join(folder_path, file), dtype=dtype)
                else:
                    df = pd.read_csv(os.path.join(folder_path, file), dtype=dtype)
                df['filename'] = file
                df['id'] = df.apply(lambda row: today + "_" + str(row["ShopId"]) + "_" + str(row['TxSalesHeaderId']) , axis=1)
                # 連接 MySQL
                mysql_engine = create_engine("mysql+pymysql://root:root@localhost:3306/caterlordpos")
                error_rows = []  # 儲存錯誤行的索引
                with (mysql_engine.connect() as conn):
                    df_prev = None
                    for index, row in tqdm(df.iterrows(), total=len(df), desc="Parser Header Data"):
                        try:
                            row_dict = row.to_dict()
                            df_single = pd.DataFrame([row_dict])  # 單行 DataFrame
                            # 第二欄沒有值的時候就直接跳過
                            if str(df_single.iloc[0]["AccountId"]) == 'nan':
                                continue
                            # 如果首欄不是數字就是要合併
                            elif not str(df_single.iloc[0]["TxSalesHeaderId"]).isdigit():
                                insert_row = [column for column in df_single.iloc[0, 1:19]]
                                df_prev.loc[0, 'TotalPaymentMethodSurchargeAmount': 'ApiGatewayResponseCode'] = insert_row
                                # print('not skip', str(df_prev.loc[0, 'TotalPaymentMethodSurchargeAmount' : 'ApiGatewayResponseCode']))
                                df_single = df_prev

                            # 如果沒有工作時間，代表被切斷，要合併之後才能送出
                            elif str(df_single.iloc[0]["StartWorkdayPeriodDetailId"]) == 'nan' and str(df_single.iloc[0]["StartWorkdayPeriodName"]) == 'nan':
                                df_prev = df_single
                                continue

                            df_single.to_sql("txsalesheader", conn, if_exists="append", index=False)
                            df_prev = df_single

                        except Exception as e:
                            error_rows.append((index, str(e)))  # 記錄錯誤的行
                            print(f"Row {index} skipped due to error: {e}")

