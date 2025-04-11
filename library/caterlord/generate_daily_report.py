import os

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import settings.settings as settings
from library.utils.excelUtils import ExcelUtils

UG_template_file = settings.UG_TEMPLATE
FILES4PARSE = settings.FILES4PARSE
excel_output = settings.EXCEL_OUTPUT
mysql_engine = create_engine(f"mysql+pymysql://{settings.DATABASES['sharetea_mysql']['USER']}:{settings.DATABASES['sharetea_mysql']['PASSWORD']}@{settings.DATABASES['sharetea_mysql']['HOST']}:{settings.DATABASES['sharetea_mysql']['PORT']}/{settings.DATABASES['sharetea_mysql']['DBNAME']}")
weekday_map = {
        0: "周一",  # Monday
        1: "周二",  # Tuesday
        2: "周三",  # Wednesday
        3: "周四",  # Thursday
        4: "周五",  # Friday
        5: "周六",  # Saturday
        6: "周日",  # Sunday
    }

shop_map = {
    '6401': '忠孝-C',
    '6426': '虎林-D',
    '6444': '永吉-E',
    '6481': '南陽-G',
    '6524': '羅東-F',
    '6525': '林口-J',
    '6526': '大巨蛋-I',
    '6527': '士林-H',
}
def generate_daily_report(year: int, month: int, excel_path: str = UG_template_file, output_path: str = excel_output):
    os.listdir()
    today = datetime.now().strftime("%Y-%m-%d")        
    try:
        rocYear = year - 1911
        monthStartDate = datetime(year, month, 1)
        if month == 12:
            monthEndDate = datetime(year + 1, 1, 1)
        else:
            monthEndDate = datetime(year, month + 1, 1)
        monthEndDate = monthEndDate - timedelta(days=1)
        queryStart = f"{rocYear}/{monthStartDate.strftime('%m/%d')}"
        queryEnd = f"{rocYear}/{monthEndDate.strftime('%m/%d')}"
        lastDate = int(monthEndDate.strftime('%d'))
        params = {'queryStart': queryStart, 'queryEnd': queryEnd}
        sql = "select * from tlps_daily_report where txDate between %(queryStart)s and %(queryEnd)s  order by txDate "
        df = pd.read_sql(
            sql,
            mysql_engine,
            params=params)
        txDates = list(df['txDate'])
        last_tx_date = txDates[len(txDates) - 1]
        lastTxDate = int(last_tx_date.split('/')[2])

        excel = ExcelUtils(excel_path)

        # 找出日期並整理
        date_array = [f"{month}月{i}日" for i in range(1, lastDate + 1)]
        weekday_array = []
        for i in range(1, lastDate + 1):
            weekday = datetime(year, month, i).weekday()
            weekday_array.append(weekday_map[weekday])
        date_array.append(f"{month}月合計")

        last_date_dict = {}
        shop_dict = {}
        for index, row in df.iterrows():
            row_dict = row.to_dict()
            shop_id = row_dict["shopId"]
            if not shop_dict.get(shop_id):
                shop_dict[shop_id] = []
            shop_dict[shop_id].append(row_dict)
            if row_dict["txDate"] == last_tx_date:
                last_date_dict[shop_id] = row_dict
            # print(row_dict)
            # column_letter, data, wsIndex=None, start_row=2, wsNewName=None
        shop_attr_dict = {}

        for key in shop_dict.keys():
            month_data = shop_dict[key]
            attr_dict = {'cup_amt_avg': [], 'order_amt_avg': [], 'cups_avg': [], 'ub_percent': [], 'fp_percent': [], 'all_discount': [], 'all_discount_percent': []}
            # 設置每一欄要填的值
            for day_dict in month_data:
                for k, v in day_dict.items():
                    if not attr_dict.get(k):
                        attr_dict[k] = []
                    attr_dict[k].append(v)
                if not last_date_dict[key].get("totalAmt"):
                    last_date_dict[key]["totalAmt"] = 0
                last_date_dict[key]["totalAmt"] += day_dict["noDiscountAmt"]
                attr_dict["cup_amt_avg"].append(
                    round((day_dict["noDiscountAmt"] if day_dict["noDiscountAmt"] else 0 ) / day_dict["cups"], 2))
                attr_dict["order_amt_avg"].append(
                    round((day_dict["noDiscountAmt"] if day_dict["noDiscountAmt"] else 0) / day_dict["orders"], 2))
                attr_dict["cups_avg"].append(
                    round((day_dict["cups"] if day_dict["cups"] else 0) / day_dict["orders"], 2))
                attr_dict["ub_percent"].append(
                    round((day_dict["ubCups"]  if day_dict["ubCups"]  else 0) / day_dict["cups"], 2))
                # attr_dict["ub_percent"].append(0)
                attr_dict["fp_percent"].append(
                    round((day_dict["fpCups"] if day_dict["fpCups"] else 0) / day_dict["cups"], 2))
                # attr_dict["fp_percent"].append(0)
                attr_dict["all_discount"].append(day_dict["conflictDiscount"] + day_dict["allOrderDiscount"])
                attr_dict["all_discount_percent"].append(
                    (day_dict["conflictDiscount"] + day_dict["allOrderDiscount"]) * -1 / day_dict["noDiscountAmt"])

            shop_attr_dict[key] = attr_dict
            excel.setWs(shop_map[key][:-2])
            # column_letter, data, start_row = 2, wsIndex = None, wsNewName = None):
            excel.fillColumn('C', attr_dict['noDiscountAmt'], start_row=3)
            excel.fillColumn('F', attr_dict['cups'], start_row=3)
            excel.fillColumn('I', attr_dict['orders'], start_row=3)
            excel.fillColumn('N', attr_dict['order_amt_avg'], start_row=3)
            excel.fillColumn('O', attr_dict['cup_amt_avg'], start_row=3)
            excel.fillColumn('P', attr_dict['cups_avg'], start_row=3)
            excel.fillColumn('S', attr_dict['ubCups'], start_row=3)
            excel.fillColumn('T', attr_dict['ub_percent'], start_row=3)
            excel.fillColumn('U', attr_dict['fpCups'], start_row=3)
            excel.fillColumn('V', attr_dict['fp_percent'], start_row=3)
            excel.fillColumn('Y', attr_dict['couponCups'], start_row=3)
            excel.fillColumn('Z', attr_dict['discount5cups'], start_row=3)
            excel.fillColumn('AA', attr_dict['friendCups'], start_row=3)
            excel.fillColumn('AB', attr_dict['all_discount'], start_row=3)
            excel.fillColumn('AC', attr_dict['all_discount_percent'], start_row=3)
            excel.fillColumn('AD', attr_dict['conflictDiscount'], start_row=3)
            excel.fillColumn('AE', attr_dict['allOrderDiscount'], start_row=3)
            excel.fillColumn("A", data=date_array, start_row=3)

            # 先不移除
            # rows_4_remove = []
            # for i in range(lastTxDate + 1, 32):
            #     rows_4_remove.append(i + 2)
            # excel.removeRows(rows_4_remove)
            excel.fillColumn("B", data=weekday_array, start_row=3, wsNewName=f"{shop_map[key][:-2]}-{month}")

        # 先塞日報
        print(last_date_dict[key])
        excel.setWs("日報")
        for shop_id, shop_data in last_date_dict.items():
            column_letter = shop_map[shop_id][-1:]
            # column_letter, row, value, wsIndex=None
            excel.fillCell(column_letter, 8, shop_data["noDiscountAmt"])
            excel.fillCell(column_letter, 9, shop_data["allOrderDiscount"] + shop_data["conflictDiscount"])
            excel.fillCell(column_letter, 10,
                        f"{(shop_data['allOrderDiscount'] + shop_data['conflictDiscount']) / shop_data['noDiscountAmt']:.2%}")
            excel.fillCell(column_letter, 11, shop_data["netAmount"])
            excel.fillCell(column_letter, 12, shop_data["cups"])
            excel.fillCell(column_letter, 13, round(shop_data["noDiscountAmt"] / shop_data["cups"], 2))
            excel.fillCell(column_letter, 14, round(shop_data["noDiscountAmt"] / shop_data["orders"], 2))
            excel.fillCell(column_letter, 15, shop_data["totalAmt"])
            excel.fillCell(column_letter, 19, shop_data["ubCups"])
            excel.fillCell(column_letter, 21, shop_data["fpCups"])
            excel.fillCell(column_letter, 26, shop_data["orders"])
            excel.fillCell(column_letter, 27, round(shop_data["cups"] / shop_data["orders"], 2))
            # 三窨十五茉券
            excel.fillCell(column_letter, 31, shop_data["couponCups"])
            excel.fillCell(column_letter, 32, shop_data["discount5cups"])
            excel.fillCell(column_letter, 33, shop_data["friendCups"])

        # fill data to excel

        excel.save(output_path)
        return True
    except:
        print(f"{today} excel generate error")
        return False    


def daily_report():
    # 來客數及杯數
    params = {'bot': 'BOT', 'cup':'CUP'}
    sql = "select t.txDate txDate, t.shopId shopId, count(t.txId) orders, round(sum(t.amount), 1) cupAmount, sum(t.cups) cups from (select txDate, shopId, txId , sum(amount) amount, sum(qty) cups from tlps_a a inner join item i on substring(a.itemCode, 1, 9) = i.cod_item where (i.unt_stk = %(cup)s or i.unt_stk = %(bot)s) and a.isParsed = 0 group by a.txDate, a.shopId, a.txId ) as t group by t.txDate, t.shopId"
    # print("sql", sql)
    df1 = pd.read_sql(
        sql,
        mysql_engine,
        params=params)
    # print(df.head())
    # 營業額和實際營收
    df2 = pd.read_sql(
        "select txDate, shopId,sum(price * qty) grossAmount, round(sum(amount), 1) netAmount from tlps_a a where a.isParsed = 0 group by a.txDate, a.shopId",
        con=mysql_engine)
    # 扣除價格為負的（折扣）
    df2_1 = pd.read_sql(
        "select txDate, shopId,sum(price * qty) noDiscountAmt, round(sum(amount), 1) noDiscountNetAmt from tlps_a a where a.price >= 0 and a.isParsed = 0 group by a.txDate, a.shopId",
        con=mysql_engine)
    # 折五元
    df3 = pd.read_sql(
        text("select txDate, shopId, sum(qty) discount5cups, round(sum(amount), 1) discount5Amount from tlps_a a where a.isParsed = 0 and (a.itemName like '%折%' or a.itemName like '%扣%' or a.itemName like '%抵%' or a.itemName like '%優惠%') and a.itemName like '%5元%' and a.itemName not like '%15元%' group by txDate, shopId"),
        con=mysql_engine)
    # 三窨十五茉券
    df4 = pd.read_sql(
        text("select txDate, shopId, sum(qty) couponCups, round(sum(amount), 1) couponAmount from tlps_a a where a.isParsed = 0 and a.itemName like '%三窨十五茉%' and  a.itemName like '%券%' group by txDate, shopId"),
        con=mysql_engine)
    # 好友兌換15券
    df5 = pd.read_sql(
        text("select txDate, shopId, sum(qty) friendCups, round(sum(amount), 1) friendAmount from tlps_a a where a.itemName like '%好友%' and a.itemName like '%15%' and a.isParsed = 0 group by txDate, shopId"),
        con=mysql_engine)

    # 全單折扣
    df6 = pd.read_sql(
        "select txDate, shopId, round(sum(amount), 1) allOrderDiscount from tlps_a  where  price < 0 and isParsed = 0 group by txDate, shopId",
        con=mysql_engine)
    # 撞餐折扣
    df7 = pd.read_sql(
        "select txDate, shopId, round(sum(amount) - sum(price * qty), 1) conflictDiscount from tlps_a where isParsed = 0 group by txDate, shopId",
        con=mysql_engine)
    # 外帶，外送杯數
    df8_1 = pd.read_sql(
        text("select txDate, shopId, round(sum(qty), 1) takeoutCups from tlps_f f inner join item i on substring(f.itemCode, 1, 9) = i.cod_item where (i.unt_stk = 'CUP' or i.unt_stk = 'BOT') and (f.useType = '1' or f.useType = '2') and f.isParsed = 0 group by f.txDate, f.shopId"),
        con=mysql_engine)
    df8_2 = pd.read_sql(
        text(
            "select txDate, shopId, round(sum(amount), 1) takeoutAmount from tlps_f f where  f.useType = '1' or f.useType = '2' and f.isParsed = 0 group by f.txDate, f.shopId"),
        con=mysql_engine)
    df8_3 = pd.read_sql(
        text(
            "select txDate, shopId, round(sum(qty), 1) deliveryCups from tlps_f f inner join item i on substring(f.itemCode, 1, 9) = i.cod_item where (i.unt_stk = 'CUP' or i.unt_stk = 'BOT') and f.useType = '3' and f.isParsed = 0 group by f.txDate, f.shopId"),
        con=mysql_engine)
    df8_4 = pd.read_sql(
        text(
            "select txDate, shopId, round(sum(amount), 1) deliveryAmount from tlps_f f where  f.useType = '3' and f.isParsed = 0 group by f.txDate, f.shopId"),
        con=mysql_engine)

    # FP 及 UB 杯數
    # UB cups
    df9_1 = pd.read_sql(
        "select txDate, shopId, sum(qty) ubCups from sales_detail where category = 'UBEREATS' and isParsed = 0 group by txDate, shopId ",
        con=mysql_engine)
    # FP cups
    df9_2 = pd.read_sql(
        "select txDate, shopId, sum(qty) fpCups from sales_detail where category = 'Foodpanda' and isParsed = 0 group by txDate, shopId",
        con=mysql_engine)
    txDates = set(df1['txDate'])
    # 產生sql parameter
    placeholders = ", ".join([f":txDate{i}" for i in range(len(txDates))])
    params = {f"txDate{i}": value for i, value in enumerate(txDates)}

    df1 = df1.merge(df2, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df2_1, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df3, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df4, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df5, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df6, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df7, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df8_1, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df8_2, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df8_3, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df8_4, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df9_1, on=['txDate', 'shopId'], how='left')
    df1 = df1.merge(df9_2, on=['txDate', 'shopId'], how='left')

    with mysql_engine.connect() as conn:
        conn.begin()
        try:
            df1.to_sql(f"tlps_daily_report", mysql_engine, if_exists="append", index=False)
            sql = text(f"UPDATE tlps_a SET isParsed = 1 WHERE isParsed = 0")
            conn.execute(sql)
            sql = text(f"UPDATE tlps_e SET isParsed = 1 WHERE isParsed = 0 and txDate in ({placeholders})")
            conn.execute(sql, params)
            sql = text(f"UPDATE tlps_f SET isParsed = 1 WHERE isParsed = 0 and txDate in ({placeholders})")
            conn.execute(sql, params)
            sql = text(f"UPDATE tlps_h SET isParsed = 1 WHERE isParsed = 0 and txDate in ({placeholders})")
            conn.execute(sql, params)
            sql = text(f"UPDATE sales_detail SET isParsed = 1 WHERE isParsed = 0 and txDate in ({placeholders})")
            conn.execute(sql, params)
            conn.commit()
        except Exception as e:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{current_time} daily DB report error: {repr(e)}")
            return False

    return True