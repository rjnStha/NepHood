import requests
import json
from datetime import datetime

class NRBForexAPI(object):
    def __init__(self):
         # NOTE the NRB endpoint response data has DATE not in order
        self.US_exchange_rate_dict = {}
    
    # TODO validate from and to date
    # Specify the lower ceiling
    def get_US_Rate(self, date_from=None, date_to=None):
        if date_from is None and date_to is None:
            date_from = datetime.today().date()
            date_to = datetime.today().date()
        page = 1
        per_page = 100 # Value range from 1 to 100
        endpoint = f'https://www.nrb.org.np/api/forex/v1/rates?from={date_from}&to={date_to}&per_page={per_page}&page={page}'
        self.get_Page_Data(endpoint)
        print(self.US_exchange_rate_dict)
        return self.US_exchange_rate_dict

    # Recursive function to get all the pages of the data
    def get_Page_Data(self, endpoint):
        try:
            response = requests.get(endpoint)
            # convert bytes to json string then to dictionary
            response_dict = json.loads(response._content.decode('utf-8'))
            
            status_code = response_dict["status"]["code"]
            # Validate successful response
            if  status_code == 200:
                payload = response_dict["data"]["payload"]

                # NOTE: Data struct {"data": {"payload":[{"rates":[{"buy":"US_exchange_rate"}]}]}}
                # Loop through payload
                for rates_dict in payload:
                    date = rates_dict["date"]
                    # US rate second item of the list
                    US_exchange_rate = rates_dict["rates"][1]["buy"]
                    self.US_exchange_rate_dict[str(date)] = US_exchange_rate
                    
            else:
                error = response_dict["errors"]
                raise Exception(f"NRB endpoint request status {status_code} \n Error: {error}  ")
            
            # Get the next page endpoint
            next_page_endpoint = response_dict["pagination"]["links"]["next"]
            # Validate None and recurse to get data from next page
            if next_page_endpoint is not None:
                self.get_Page_Data(next_page_endpoint)
        
        except requests.exceptions.RequestException as e:
            print('Request cancelled or failed:', e)
        except BaseException as e:
            print(e)

        return

# Testing
if __name__ == '__main__':
    s = NRBForexAPI()
    s.get_US_Rate()
