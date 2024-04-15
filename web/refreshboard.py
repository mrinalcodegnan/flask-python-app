import gspread
import pandas as pd

class GoogleSheetReader:
    def __init__(self, url, sheet_name):
        self.sheet_url = url
        self.sheet_name = sheet_name
        self.client = gspread.authorize(None)  # No authentication needed

    def get(self):
        sheet = self.client.open_by_url(self.sheet_url)
        worksheet = sheet.worksheet(self.sheet_name)
        data = worksheet.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        print(df.head())
        return df