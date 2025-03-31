import os, sys

from datetime import datetime
from library.caterlord.get_remote_files import get_remote_files
from library.caterlord.migrate_from_erp import migrate_from_erp
from library.caterlord.receive_gmail import download_mail_attach
from library.caterlord.tlp_csv_parser import data_importer
from library.caterlord.detail_excel_parser import excel_data_importer
from library.caterlord.generate_daily_report import daily_report as daily_db
from library.caterlord.generate_daily_report import generate_daily_report
import settings.settings as settings

def test():
    print("test")
    # print("test")

# 把檔案由餐飲王中繼主機抓來
def get_files_from_middleware_server():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f" {now} get_files_from_middleware_server:")
    get_remote_files()


# 把db由ERP複製過來
def migrate():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f" {now} migrate:")
    migrate_from_erp()

# 解析餐飲王csv
def csv_data_import(folder_path=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if folder_path is None:
        folder_path = settings.FILES4PARSE
    print(f" {now} csv_data_import: {folder_path}")
    data_importer(folder_path)

def receive_mail():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f" {now} receive_mail:")
    download_mail_attach()

# 解析餐飲王excel
def excel_data_import(folder_path=None):
    if folder_path is None:
        folder_path = settings.FILES4PARSE
    excel_data_importer(folder_path)

# 產生日報表（在db中）
def daily_report(arg1=None):
    daily_db()

# 產生excel日報表
def daily_excel_report():
    generate_daily_report()

# def copy_file(file_path):


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('請指定要執行的動作')
    else:
        thismodule = sys.modules[__name__]
        args = []
        if len(sys.argv) > 2:
            args = sys.argv[2:]


        getattr(thismodule, sys.argv[1])(*(args))
        try:
            pass
            # send_mail() 不寄email了，沒意義
        except Exception as error:
            print("Error while sending email ", error)





