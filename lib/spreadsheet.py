import os
import gspread
import json

from oauth2client.service_account import ServiceAccountCredentials 


def get_sheet(sheet_key):
    # Login with OAuth2
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(base_dir, 'cababa/data/spreadsheet_cred.json'), scope)
    gc = gspread.authorize(credentials)

    #共有設定したスプレッドシートのシート1を開く
    worksheet = gc.open_by_key(sheet_key).worksheet("事前登録申し込み者")
    return worksheet

# #A1セルの値を受け取る
# import_value = int(worksheet.acell('A1').value)

# #A1セルの値に100加算した値をB1セルに表示させる
# export_value = import_value+100
# worksheet.update_cell(1,2, export_value)