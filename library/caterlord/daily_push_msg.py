from linebot import LineBotApi, WebhookHandler
from library.utils.generate_line_msg import generate_store_status_flex, generate_daily_report_text
# enable less secure apps on your google account
# https://myaccount.google.com/lesssecureapps
# 設定你的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = 'iHju3F9bbzaFD2jy8xW1Ei4SlSjZja0T4WyBu8rzpVGUViKPBYDpY2bDqGWJefVcap3w/h7Aaq/yhxozLOe+GvWLf3qYIsaokJ7LSzPq4yrchpa/qDyPJmyWdbcZ9vmcFk3fMFJ1fK56yr0VvexrBAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '2ea026cad044bc121ffa739778b12fc1'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


# daily push message to group
def daily_push_msg():
    user_id = 'U244e17b848d6b118d0f5a8d6f9e26a93'
    group_id = 'C52881ab7d93ff860107f98691836f3f7'
    dest_id = group_id

    stores = [
        {"name": "台北店", "status": "✅ 正常營業"},
        {"name": "台中店", "status": "❌ 維修中"},
        {"name": "高雄店", "status": "⏰ 尚未開店"}
    ]

    data = [
        {"店名": "忠孝敦化店", "杯數": 2072, "金額": 156811, "杯單": 70.5, "客單": 165, "折扣率": 8.2},
        {"店名": "站前南陽店", "杯數": 3073, "金額": 164811, "杯單": 68.5, "客單": 150, "折扣率": 9.0},
        # 其他店...
    ]
    # message = generate_store_status_flex(stores)
    message = generate_daily_report_text(data)
    line_bot_api.push_message(dest_id, message)
    return True