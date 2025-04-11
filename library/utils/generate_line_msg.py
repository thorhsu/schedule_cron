import openpyxl
from datetime import date
from linebot.models import FlexSendMessage, TextSendMessage


def generate_store_status_flex(stores):
    contents = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": "📊 每日營業報表：統計至2025/4/9(三)",
                    "wrap": True,
                    "weight": "bold",
                    "size": "md",
                    "color": "#d32f2f"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "md",
                    "margin": "md",
                    "contents": [
                        {"type": "text", "text": "門市類型", "weight": "bold", "size": "sm", "flex": 2},
                        {"type": "text", "text": "店名", "weight": "bold", "size": "sm", "flex": 3},
                        {"type": "text", "text": "當日業績", "weight": "bold", "size": "sm", "flex": 3},
                        {"type": "text", "text": "當日杯數", "weight": "bold", "size": "sm", "flex": 2}
                    ]
                }
            ]
        }
    }

    # 加入每家店的狀態列
    # for store in stores:
    #     contents["body"]["contents"].append({
    #         "type": "box",
    #         "layout": "horizontal",
    #         "contents": [
    #             {"type": "text", "text": store["name"], "size": "sm", "flex": 2},
    #             {"type": "text", "text": store["status"], "size": "sm", "flex": 3}
    #         ]
    #     })

    return FlexSendMessage(
        alt_text="今日營業狀況",
        contents=contents
    )

def generate_daily_report_text(data, report_date=None):
    if not report_date:
        report_date = date.today().strftime('%Y/%m/%d')

    lines = [f"📊 每日業績（{report_date}）\n"]
    total_cups = 0
    total_amount = 0

    for row in data:
        lines.append(f"{row['店名']}：")
        lines.append(
            f"杯數 {row['杯數']:,}｜金額 {row['金額']:,}｜杯單 ${row['杯單']:.1f}｜客單 ${row['客單']:.0f}｜折扣率 {row['折扣率']:.1f}%\n"
        )
        total_cups += row['杯數']
        total_amount += row['金額']

    lines.append("總計：")
    lines.append(f"杯數 {total_cups:,}｜金額 {total_amount:,}")

    return TextSendMessage(text="\n".join(lines))

