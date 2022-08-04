from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle




class GoogleSheet:
    SPREADSHEET_ID = '1SpNRAZrxVcPNwAgjubglVfhie6iTi7hPVM3SjKg_HEQ'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None
    
    def __init__(self):
       
        creds = None
      
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
      
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
           
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def updateRangeValues(self, range_sheet, values):
        data = [{
            'range': range_sheet,
            'values': values
        }]

        body = {
            'valueInputOption': 'RAW',
            'data': data
        }

        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID, body=body).execute()
        print('Ячеек обновлено: {0} '.format(result.get('totalUpdatedCells')))

    def appendRangeValues(self, range_sheet, values):
        
        body = {'values': values}
        
        result = self.service.spreadsheets().values().append(spreadsheetId=self.SPREADSHEET_ID, 
            range=range_sheet, valueInputOption='USER_ENTERED', body=body).execute()
        print('Ячеек обновлено: {0} '.format(result.get('updates')))
        

    def record_cancel(self, range_sheet):
                        
        result = self.service.spreadsheets().values().clear(spreadsheetId=self.SPREADSHEET_ID, 
            range=range_sheet).execute()
        
    def free_time(self, free_date, range_sheet):
        
        freetime =[]
        result = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID, 
            majorDimension='ROWS', range=range_sheet).execute().get('values',[])
        for data in range(0, len(result), 1):
            if data != 0:
                if result[data][0] == free_date:
                    for times in range(1, len(result[data]), 1):            
                        if times > 0:
                            if result[data][times] == '--:--':
                                freetime.append(result[0][times])
        return freetime

    def free_date(self, range_sheet):
      
        result = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID, 
            majorDimension='ROWS', range=range_sheet).execute().get('values',[])
        list_date = []
        for date in range(0, len(result), 1):    
            if date != 0:                
                if '--:--' in result[date][1:13]:
                    list_date.append(result[date][0])
            
        return list_date

    def read_sheet(self, range_sheet):
        result = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID, 
            majorDimension='ROWS', range=range_sheet).execute().get('values',[])
        return result
                    
        
        
    