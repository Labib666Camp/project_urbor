import ee
import time as t

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
    service_account = 'urbor-serv-acc@project-urbor.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, 'project-urbor-ac472ba741f1.json')
    ee.Initialize(credentials)
    print('-----DONE------')
    print(f'time taken ........ {t.time() - st}')

if __name__ == "__main__":
    authenticate()