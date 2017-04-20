from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException
import time

studentIDList = []

with open('studentIDs.txt') as input_file:
    for line in input_file:
        studentIDList.append(line)

print("\n\tStudent ID's have been read from file\n")

#create a new file that will contain all student Info
auditFileName = "StudentAudit.txt"
newAudit = open(auditFileName, "w+")

path_to_chromedriver = r"C:\Users\Michell\seleniumWork\chromedriver_win32\chromedriver.exe"
#"credentials_enabled_service", False
#"profile.password_manager_enabled", False

#intialize driver
browser = webdriver.Chrome(executable_path=path_to_chromedriver)

#https://adp.bigbend.edu/adp/Login.aspx
#get the URL
url = r'https://adp.bigbend.edu/adp/Login.aspx'
browser.get(url)

while True:
    try:
        SSIDnum = input("Enter SSID: ")
        PINnum = input("Enter PIN: ")

        #get the SSID input box and input SSID
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_TextBox_Sid"]""").send_keys(SSIDnum)

        #get the PIN input box and input PIN
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_TextBox_Pin"]""").send_keys(PINnum)

        #get the login button and click
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Button_Login"]""").click()

        time.sleep(4)

        #click ACCEPT on FERPA
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Button_Accept"]""").click()
        break
    except (StaleElementReferenceException, NoSuchElementException) as e:
        pass

#get the first student ID on the list
studentID = studentIDList[0]

time.sleep(3)

#When StaleElementException is raised the program keeps trying until it can find the element
while True:
    try:
        #locate studentID field and input studentID
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_TextBox_Sid"]""").send_keys(studentID)
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Button_SidSearch"]""").click() #search button click
        time.sleep(1)
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_GridView_Students_ctl02_Button_SelectStudent"]""").click() #select student
        break
    except (StaleElementReferenceException, NoSuchElementException) as e:
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_TextBox_Sid"]""").clear()
        time.sleep(2)
        pass

time.sleep(1)

def writeStudentAudit():
    #prevent StaleElementException'
    studentName = ""
    studentID = ""
    while True:
        try:
            #get student name and studentID
            studentName = browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Panel_BSI_Hider"]/div/div/table/tbody/tr[1]/td[2]/strong""").text
            studentID = browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Panel_BSI_Hider"]/div/div/table/tbody/tr[2]/td[2]""").text
            break
        except (StaleElementReferenceException, NoSuchElementException) as e:
            studentName = ""
            time.sleep(1)
            pass

    time.sleep(1)
    while True:
        try:
            browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Image_UnofficialTranscript"]""").click()
            break
        except NoSuchElementException as e:
            time.sleep(1)
            pass
        
    print("Appending audit for student ", studentName, studentID)
    time.sleep(1)

    #create a list for table rows tag
    tableRows = []

    #find all elements with tag name table row [tr] and add to list
    tableRows = browser.find_elements_by_tag_name("tr")

    courses = []
    #find courses in table rows list
    for row in tableRows:
        #create a line that states when the transfer courses begin
        if row.text.find("YRQ") != -1 and row.text.find("Eval") != -1:
            courses.append("---- TRANSFER-IN COURSES BEGIN HERE ----")
        #row must contain a period to indicate a valid GPA and not dashes or asterisks
        if row.text.find(".") != -1 and row.text.find("-") == -1 and row.text.find("*") == -1 and row.text.find("0.0") == -1:
            courses.append(row.text)

    #write student name and ID
    newAudit.write("Student Name: "+ studentName + "\n")
    newAudit.write("Student ID: " + studentID + "\n")

    #write courses
    for course in courses:
        newAudit.write(course + "\n")

    #include a space between students
    newAudit.write("\n")

#search a new student (every student after the first)
def searchNewStudent(studentID):
    #prevent StaleElementException
    while True:
        try:
            #clear search, enter new id and click enter
            browser.find_element_by_xpath("""//*[@id="ctl00_TextBox_LoadedStudentSid"]""").clear()
            browser.find_element_by_xpath("""//*[@id="ctl00_TextBox_LoadedStudentSid"]""").send_keys(studentID)
            browser.find_element_by_xpath("""//*[@id="ctl00_Button_ChangeLoadedStudent"]""").click()
            time.sleep(3)
            break
        except (StaleElementReferenceException,NoSuchElementException) as e:
            browser.find_element_by_xpath("""//*[@id="ctl00_TextBox_LoadedStudentSid"]""").clear()
            time.sleep(1)
            pass

    time.sleep(2)
    
    writeStudentAudit()

#search over list of students and write their schedule in a file
count = 0
while count < len(studentIDList):
    if count == 0: #first student would have already been found
        writeStudentAudit()
        count += 1
    else:
        searchNewStudent(studentIDList[count])
        count += 1


#close audit file and browser
newAudit.close()
browser.quit()
print("Audit complete")


