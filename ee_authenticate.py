import ee
import time as t
import json

def authenticate():
    st = t.time()
    print('Authentication Starting ....')
    # try:
    #     ee.Initialize(project = 'ee-workmainulislam2')
    #     print("Earth Engine authentication successful.")
    # except Exception as e:
    #     print("Earth Engine authentication failed. Please authenticate manually.")
    #     print(f"Error: {str(e)}")
    #     ee.Authenticate(auth_mode='localhost')
    #     ee.Initialize(project = 'ee-workmainulislam2')
    service_account = st.secrets['SERVICE_ACCOUNT']
    key_data = st.secrets['KEY_DATA']
    credentials = ee.ServiceAccountCredentials(email = service_account, key_data = key_data)
    ee.Initialize(credentials)
    print('-----DONE------')
    print(f'time taken ........ {t.time() - st}')

if __name__ == "__main__":
    authenticate()
