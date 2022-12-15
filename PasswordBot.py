from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import emoji
import json
import os
import requests
from requests.auth import HTTPBasicAuth
import subprocess, sys



load_dotenv(find_dotenv())
@dataclass(frozen=True)
class APIkeys:
  accountid: str = os.getenv('zoomacctid')
  clientid: str = os.getenv('zoomclientid')
  clientsecret: str = os.getenv('zoomclientsecret')
  helpdeskep: str = os.getenv('zoomHDep') 



p = subprocess.Popen(["powershell.exe", '.\\UsersNeedPWNotify.ps1'], stdout=sys.stdout)
p.communicate()





base_api_endpoint = "https://zoom.us"
auth_ep = "/oauth/token?grant_type=account_credentials&account_id=" + APIkeys.accountid
ithelpdesk_smsg_ep = APIkeys.helpdeskep


authdata = HTTPBasicAuth(APIkeys.clientid, APIkeys.clientsecret) ##Authorization: Basic Base64Encoder(APIkeys.clientid:APIkeys.clientsecret)

listoffield = []
#with open("FieldTitles.txt", "r") as sf:
#  for i in sf:
#    listoffield.append(i)






users = 'UsersToBeNotified.csv'
fieldinstructions = 'FieldInstructions.txt'
officeinstructions = 'OfficeInstructions.txt'
  


def getToken(url):
    headers = {
        'Accept': 'application/json'
    }
    response = requests.request("POST", url=url, headers=headers, auth=authdata)
    cookies = response.cookies
    cookiestr = ""
    for i in cookies:
        cookiestr += i.name + i.value +";"
    return cookiestr, response.json()['access_token']



def warning_title(days,contact,expiration):
  warning = json.dumps({
    "rich_text": [
    {
      "start_position": 1,
      "end_position": 2,
      "format_type": "Paragraph",
      "format_attr": "h1"
    }
  ],
    "message": emoji.emojize(':warning:') + "Your network password expires on " + expiration + emoji.emojize(':warning:') + "\n" + emoji.emojize(':warning:') + "( Less than " + days.split('\n')[0] + " days!!) Please follow the instructions below: "+ emoji.emojize(':warning:'),   
    "to_contact": contact
  })
  return warning
def instructions(contact,instructionsf):
  line_list = []
  with open(instructionsf, 'r', encoding="UTF-8") as file:
    for i in file:
      line_list.append(i)
  fistring = ' '.join(line_list)

  if instructionsf == fieldinstructions:
    instruction = json.dumps({
      "rich_text": [
      {
        "start_position": 1,
        "end_position": 2,
        "format_type": "Paragraph",
        "format_attr": "h1"
      }
      ],  
      "message": "\U0001F4F1" + fistring + "\U0001F4F1",   
      "to_contact": contact
    })
    return instruction
  if instructionsf == officeinstructions:
    instruction = json.dumps({
      "rich_text": [
      {
        "start_position": 1,
        "end_position": 2,
        "format_type": "Paragraph",
        "format_attr": "h1"
      }
      ],  
      "message": "\U0001F5A5" + fistring + "\U0001F5A5",   
      "to_contact": contact
    })
    return instruction


  

def runme():
    users_list = []
    with open("UsersToBeNotified.csv", 'r', encoding='UTF-16 LE') as usersf: 
      users_l = usersf.readlines()
      #print(users_l)
      for i in range(len(users_l)-1):
        user = users_l[i+1]
        print(user)
        user = user.split(',')
        days = user[2] # less than days
        expire = user[1] #expire date
        user = user[0] #email
        warning = warning_title(days,user,expire)
        instruction= instructions(user,fieldinstructions)
        steps = instructions(user,officeinstructions)

        session = requests.session()
        responsew = session.request("POST", base_api_endpoint + ithelpdesk_smsg_ep, headers=headersPauth, data=warning)
        print(responsew.text)
        if '{"id":"' not in responsew:
          with open("BotErrors.log", "a") as sf:
            sf.write(user + ",Encoundered and error Sending the Warning")
        #responseo = session.request("POST", base_api_endpoint + ithelpdesk_smsg_ep, headers=headersPauth, data=instructions(email,officeinstructions))
        #print(responseo.text)
        responsef = session.request("POST", base_api_endpoint + ithelpdesk_smsg_ep, headers=headersPauth, data=instruction) #send field instructions to user
        print(responsef.text)
        if '{"id":"' not in responsef:
          with open("BotErrors.log", "a") as sf:
            sf.write(user + ",Encoundered and error Sending the Field Instructions\n")
        

        #get errors and send them to a file
        

        

cookieandtoken = getToken(base_api_endpoint + auth_ep) #get token and cookies

headersPauth = { # Headers after token has been recived
  'Authorization': 'Bearer' + cookieandtoken[1],
  'Content-Type': 'application/json',
  'Cookie': cookieandtoken[0]
}




#warning = warning_title("14",email)
#steps = instructions(email,officeinstructions)
runme()







#response = requests.request("POST", base_api_endpoint + ithelpdesk_smsg_ep, headers=headersPauth, data=steps)





#print(response.text)




