import requests
import argparse
import xml.etree.ElementTree as ET 


banner=r'''
__________.__        ___.                 
\______   \  |   ____\_ |__   ___________ 
 |    |  _/  |  /  _ \| __ \_/ __ \_  __ \
 |    |   \  |_(  <_> ) \_\ \  ___/|  | \/
 |______  /____/\____/|___  /\___  >__|   
        \/                \/     \/       
By: LOCO
'''

baseurl = '.blob.core.windows.net'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

storage_accounts=[]



def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def prBlue(skk): print("\033[36m {}\033[00m" .format(skk))
def prRed(skk): print("\033[31m {}\033[00m" .format(skk))

def cmdline_args():
    
    prBlue(banner)
        
    p = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    
    p.add_argument("-T","--Target",
                   help="Name of the Target you are testing")
    
    p.add_argument("-W","--Wordlist",
                   help="Wordlist used to guess storage account name (default is lists/wordlist.txt)", default="lists/wordlist.txt")

    
    
    arg_input=p.parse_args()

    global wordlist_file

    wordlist_file=arg_input.Wordlist

   

    Company=arg_input.Target



    if str(Company) =='None':
        control()


    
    return(p.parse_args())

def account_wordlist(file_name):
    
    words=open(file_name, 'r').read().splitlines()
    return words


def containers_requests(storge_accounts, num_of_account):

    container_files=open("lists/containers.txt", 'r').read().splitlines()

    containers=[]

    if num_of_account != '*':
         
         for words in container_files:
            url=f"https://{storage_accounts[int(num_of_account)]}/{words}?restype=container&comp=list"

            list_req= requests.get(url, headers=headers)

            if "not authorized" in list_req.text or "The specified resource does not exist" in list_req.text or "OutOfRangeInput" in list_req.text:
                continue
                
            else:
                containers.append(url)
                prGreen(f"\t[+] Found public container: \"{words}\" in {url}" )
                
                file=open('req.xml', 'w').write(list_req.text)
                blob_parse(url)

         if len(containers)==0:
            prRed("[-] No containers found")
            return #until i make the main list a function that we can return to

         return

    for i in range(len(storage_accounts)):


        for words in container_files:
            
            url=f"https://{storage_accounts[i]}/{words}?restype=container&comp=list"
            
            list_req= requests.get(url, headers=headers)

            if "not authorized" in list_req.text or "The specified resource does not exist" in list_req.text or "OutOfRangeInput" in list_req.text:
                continue
                
            else:
                containers.append(url)
                prGreen(f"\t[+] Found public container: \"{words}\" in {url}" )
                
                file=open('req.xml', 'w').write(list_req.text)
                blob_parse(url)

        if len(containers)==0:
            prRed("[-] No containers found")
            continue

                
           
            
def blob_parse(url):

    root = ET.parse("req.xml")
    for child in root.iter():
        if 'https://' in str(child.text):
            prGreen(f"\t\t[+] Readable files within the container: {child.text}")
           
    
def accounts_requests(wordlist_values):
    temp_storage=[]
    temp_name=''
    counter=0
    
    for names in wordlist_values:
        url="https://"+names+baseurl
        try:
            req=requests.get(url,headers=headers, timeout=None)    
               
        except Exception as e:
            if "Failed to resolve" in str(e) or "Name or service not known" in str(e):
                continue

        temp_name=str(url).replace("https://", "")
        temp_storage.append(temp_name)
        prGreen(f"\t[{counter}] Found Storage account: {temp_name}")
        counter=counter + 1
    if len(temp_storage) == 0 :
        prRed("[-] No Storage accounts found")
        exit() 
    
    return temp_storage

def permutation(Company, file_name): 
    
    
    words=open("lists/Permutations.txt", "r").read().splitlines()

    file=open(file_name, 'w') # first time we need to overwrite
    file.write(str(Company)+'\n')

    for w  in words:    # first write $Company$word
        file.write(str(Company)+w+'\n')
    
    file.close()
    file=open(file_name, 'a')

    for w in words:     #$word$company
        file.write(w+str(Company)+'\n')
    
    for w in words:     #$word$company$word
        file.write(w+str(Company)+w+'\n')

    for w in words:     #$word$word$company
        file.write(w+w+str(Company)+'\n')
    
    for w in words:     #$Company$word$word
        file.write(str(Company)+w+w + '\n')

    file.close()


def show_storage_accounts(accounts):
    

    for i in range(len(accounts)):

        prGreen(f"\t[{i}] {storage_accounts[i]}")
        
def check_fqdn(company):

    if '.' in company:
        company=str(company).split('.')
        return company[0]
    
    return company



def control():

    global storage_accounts

    while 1:

        print("0) Scan a new target")
        print("1) Scan the containers available for a specific Storage Account")
        print("2) Scan all storage accounts")
        print("3) Show Storage Accounts")
        print("4) Add a new storage account to the list")
        print("5) exit")

        option=input(">")


        if option == "0":

            Company_name = input("Enter the target name: ")

            check_fqdn(Company_name)

            storage_accounts=make_scan(Company_name)

        elif option =="1":
            if len(storage_accounts)==0:
                prRed("[!] There's no storage accounts!\n")
                continue
            
            num = input("[!] Enter the number of the storage account you want to list the containers for: ")

            containers_requests(storage_accounts,num)

        elif option == "2":
            if len(storage_accounts)==0:
                prRed("[!] There's no storage accounts!\n")
                continue
        
            containers_requests(storage_accounts, '*')


        elif option == "3":
            
            if len(storage_accounts)==0:
                prRed("[!] There's no storage accounts!\n")
                continue

            show_storage_accounts(storage_accounts)

        

        elif option == "4":

            account=input("Enter the Storage Account you want to add: ")

            if ".blob.core.windows.net" not in account:
                print(f"do you mean {account}.blob.core.windows.net? (y or n) ")

                decide=input(">")

                if decide.lower() == "n" or decide.lower() == "no":
                    prRed("Please enter a valid storage account\n")
                    continue

                else:
                    account=account+".blob.core.windows.net"
            
            storage_accounts.append(account)
            prGreen("Successfully added!\n")
        

        elif option == "5":
            exit()
        
        else:
            prRed("BRUH!! You didn't enter a vild option!")

    
def make_scan(Company_name):

    permutation(Company_name, wordlist_file)

    wordlist_values=account_wordlist(wordlist_file)

    print(f"[!] Storage Accounts for {Company_name}")

    storage_accounts=accounts_requests(wordlist_values)

    return storage_accounts



if __name__ == '__main__':
    

    try:
        
        args = cmdline_args()
        
        Company_name=args.Target
        
        Company_name=check_fqdn(Company_name)
        storage_accounts=make_scan(Company_name)
        
        control()


    except Exception as e:
        print('usage: python3 blober.py -T Target')
        print(e)




        

