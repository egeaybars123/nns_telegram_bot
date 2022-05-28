import dropbox
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def check_proposals(old, new):
    count = 0
    message_proposals = []
    id_old = old[0].split(" ")[0]
    for new_prop in new:
        id_new = new_prop.split(" ")[0]
        if id_old == id_new and count != 0:
            message_proposals = new[0: count]
            break
        count += 1
    
    return message_proposals

def download_dropbox(dropbox_path, local_path):
    try:
        dbx = dropbox.Dropbox(TEMP_ACCESS)

        with open(local_path, 'wb') as f:
            metadata, result = dbx.files_download(path=dropbox_path)
            f.write(result.content)
            
    except Exception as e:
        print('Error downloading file from Dropbox: ' + str(e))
        
def upload_dropbox(local_path, dropbox_path):
    try:
        dbx = dropbox.Dropbox(TEMP_ACCESS)
        
        with open(local_path,'rb') as f:
            meta = dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
            return meta
            
    except Exception as e:
        print('Error uploading file to Dropbox: ' + str(e))

def read_previous_proposals():
    current_file = open("proposals.txt", "r", encoding="latin1")
    previous_proposals = []
    for i in current_file:
        previous_proposals.append(i)
        
    current_file.close()
    
    return previous_proposals


def write_to_previous_proposals(current):
    current_file = open("proposals.txt", "w")
    for i in current:
        current_file.write(i)
    current_file.close()
    

def format_message(listp):
    message = str(len(listp)) + " new proposal(s)!\n\n"
    for i in listp:
        i = i.split("///")
        for j in range(len(i)):
            if j == 0:
                i[j] = "<b>Proposal ID-Title:</b> " + i[j] + "\n"
            elif j == 1:
                i[j] = "<b>Status:</b> " + i[j] + "\n"
            elif j == 2:
                i[j] = "<b>Votes:</b> " + i[j] + "\n"
                
        message += "".join(i) 
        
    return message
        

PATH = "C:\Program Files (x86)\chromedriver.exe"
API_KEY = "TELEGRAM_API_KEY"
CHAT_ID = "@icp_proposal_bot"
DROPBOX_REFRESH_TOKEN = "<REFRESH_TOKEN"
app_key = 'APP_KEY'
app_secret = 'APP_SECRET'
wait_xpath = '//*[@id="root"]/div/div[4]/div/div[4]/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[1]/table/tbody/tr[10]'
xpath = '//*[@id="root"]/div/div[4]/div/div[4]/div/div[2]/div/div/div/div/div[1]/div[2]/div/div[1]/table'

f = requests.post("https://api.dropbox.com/oauth2/token\?grant_type=refresh_token&refresh_token=<REFRESH_TOKEN>",
                  auth=(app_key, app_secret))
TEMP_ACCESS = f.json()['access_token']


download_dropbox('/proposals.txt', 'proposals.txt')

previous_list_proposals = read_previous_proposals()
current_list_proposals = []

#chrome_options = webdriver.ChromeOptions()
#chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
#chrome_options.add_argument("--headless")
#chrome_options.add_argument("--disable-dev-shm-usage")
#chrome_options.add_argument("--no-sandbox")
#driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)


driver = webdriver.Chrome(executable_path=PATH)
driver.get("https://dashboard.internetcomputer.org/governance")

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, wait_xpath)))

#retrieve the table element for the proposals with XPath.
proposals = driver.find_element(By.XPATH, xpath)

#obtain the row data for the table.
trs = proposals.find_elements(By.TAG_NAME, 'tr')

for element in trs:
    new_element = element.text
    new_element = new_element.replace("\n", "///") + "\n"
    current_list_proposals.append(new_element)
    
driver.quit()

published_proposals = check_proposals(previous_list_proposals, current_list_proposals)

formatted_message = format_message(published_proposals)
 

if published_proposals != []:
    url_req = "https://api.telegram.org/bot" + API_KEY + "/sendMessage" + "?chat_id=" + CHAT_ID + "&parse_mode=HTML&text=" +formatted_message
    results = requests.get(url_req)
    
    upload_dropbox('proposals.txt', '/proposals.txt')
    print("New proposal is here!")
else:
    print("No new proposals...")
