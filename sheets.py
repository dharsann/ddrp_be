import os
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'backend/service_account.json')

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    return service

def append_order_to_sheet(order_id, customer_name, customer_phone, product_name, quantity, order_date):
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_ORDERS_SPREADSHEET_ID')
    if not spreadsheet_id:
        print("Google Sheets spreadsheet ID not set")
        return

    service = get_sheets_service()

    if isinstance(order_date, datetime):
        formatted_date = order_date.strftime('%Y-%m-%d')
    else:
        formatted_date = str(order_date).split(' ')[0]

    values = [[order_id, customer_name, customer_phone, product_name, quantity, formatted_date]]
    body = {'values': values}
    range_name = 'Orders'

    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        print(f"✅ Appended {result.get('updates').get('updatedRows')} rows to Google Sheets")
    except Exception as e:
        print("❌ Error appending to Google Sheets:", e)

def append_inventory_to_sheet(order_id, batch_no, recipe_no, quantity, rubber_type, arrival_date):
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_INVENTORY_SPREADSHEET_ID')
    if not spreadsheet_id:
        print("Google Sheets inventory spreadsheet ID not set")
        return

    service = get_sheets_service()

    if isinstance(arrival_date, datetime):
        formatted_date = arrival_date.strftime('%Y-%m-%d')
    else:
        formatted_date = str(arrival_date).split(' ')[0]

    values = [[order_id, batch_no, recipe_no, quantity, rubber_type, formatted_date]]
    body = {'values': values}
    range_name = 'Inventory'

    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        print(f"✅ Appended inventory data for order {order_id} to Google Sheets")
    except Exception as e:
        print("❌ Error appending inventory to Google Sheets:", e)
