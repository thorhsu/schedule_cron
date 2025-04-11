import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import settings.settings as settings
from smbclient import register_session, scandir, open_file, delete_session

mysql_engine = create_engine(f"mysql+pymysql://{settings.DATABASES['sharetea_mysql']['USER']}:{settings.DATABASES['sharetea_mysql']['PASSWORD']}@{settings.DATABASES['sharetea_mysql']['HOST']}:{settings.DATABASES['sharetea_mysql']['PORT']}/{settings.DATABASES['sharetea_mysql']['DBNAME']}")

def get_remote_files():
    df = []
    df = pd.read_sql(text("select distinct filename from sales_detail"), con=mysql_engine)
    file_names = df['filename'].to_list()

    df_a = pd.read_sql(text("select distinct filename from tlps_a"), con=mysql_engine)
    file_names.extend(df_a['filename'].to_list())

    df_e = pd.read_sql(text("select distinct filename from tlps_e"), con=mysql_engine)
    file_names.extend(df_e['filename'].to_list())

    df_f = pd.read_sql(text("select distinct filename from tlps_f"), con=mysql_engine)
    file_names.extend(df_f['filename'].to_list())

    df_h = pd.read_sql(text("select distinct filename from tlps_h"), con=mysql_engine)
    file_names.extend(df_h['filename'].to_list())

    # SMB server details
    server_name = settings.SMB_SERVER_NAME  # Replace with your SMB server IP/hostname
    server_port = 445
    username = settings.SMB_USERNAME
    password = settings.SMB_PASSWORD
    share_name = settings.SMB_SHARE_NAME
    # file_path = "example.txt"  # File to read from the shared folder

    # Establish connection
    register_session(server_name, username=username, password=password)
    date = datetime.now()
    today = date.strftime("%Y-%m-%d")
    print(file_names)
    for folder in filter(lambda f: f.is_dir(), scandir(f"//{server_name}/{share_name}")):
        print(folder.name,  folder.path, folder.smb_info.last_write_time)
        for file in filter(lambda f: f.is_file() and f.name not in file_names and f.smb_info.last_write_time.strftime("%Y-%m-%d") != today,
                           scandir(folder.path)):
            print(file.name, file.path, f"{settings.FILES4PARSE}{file.name}")

            with open_file(file.path, mode="rb", share_access='rw') as remote_file:
                with open(f"{settings.FILES4PARSE}{file.name}", "wb") as local_file:
                    local_file.write(remote_file.read())

    delete_session(server_name)