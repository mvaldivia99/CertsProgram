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


#---------------------------CREATE A LIST OF STUDENTS AND COURSES--------------------------------------
studentList = {} #contains list of student info
name = ""

def addClass(docLine): #adds a class to a student's information
    courseLine = docLine.split()
    
    #removes the last two elements of the line, which are the GPA and the credits earned
    courseLine.pop(-1)
    courseLine.pop(-1)
    #put line back together
    course = ""
    for indivWord in courseLine:
        course += indivWord + " "
        
    studentList[name].append(course) #add the class to the student's information

#transfer course has differnt format than the rest of the courses
#these courses will only show the department and number
def addTRClass(docLine):
    courseLine = docLine.split()

    #remove the last three columns of the line
    courseLine.pop(-1)
    courseLine.pop(-1)
    courseLine.pop(-1)

    lineSize = len(courseLine)
    
    course = courseLine[lineSize - 2] + " " + courseLine[lineSize - 1]
    
    studentList[name].append(course)

#flag will indicate when to start working with transfer courses    
TRCrsFlag = 0

with open('StudentAudit.txt') as input_file:
    for line in input_file:
        if line.find("Student Name:") != -1:#find when the student name begins
            TRCrsFlag = 0 #reassign flag to 0
            line = line[14:] #remove everything from the line but the last and first name
            name = line.split() #split the name into two parts and remove \n
            name = name[1] + " " + name[0]
            studentList[name] = [] #add student name as key in dictionary, make a new list for each student
                
        if line.find("Student ID:") != -1: #find student ID
            line = line[12:] #remove everything from line but ID
            studentID = line.split() #remove any blank spaces or \n at line ends
            studentList[name].append(studentID[0]) #add student ID to student's info

        #audit contains a line that marks where courses begin
        #any line after that will be added differently
        if line.find("TRANSFER-IN COURSES BEGIN HERE") != -1:
            TRCrsFlag = 1
            pass
        if TRCrsFlag == 1 and line.find("TRANSFER-IN COURSES BEGIN HERE") == -1 and not line.isspace(): #line is under transfer courses line and not whitespace
            addTRClass(line)
        else:            
            #find CS Classes
            if line.find("CS 1") != -1 or line.find("CS 2") != -1: #if the class is a CS class
                addClass(line) #add class to student list

            #find psych/soc/bus classes
            if line.find("BUS 120") != -1 or line.find("PSYC& 100") != -1 or line.find("SOC& 101") != -1:
                addClass(line) #add class to student list

            #find communications classes
            if line.find("CMST 100") != -1 or line.find("CMST& 220") != -1:
                addClass(line) 

            #find english classes
            if line.find("ENGL& 109") != -1 or line.find("ENGL& 101") != -1:
                addClass(line) 

            #find first aid
            if line.find("FAD 150") != -1:
                addClass(line)

            #find Math 141
            if line.find("MATH& 141") != -1:
                addClass(line)
#------------------------------COMPARE COURSES AGAINST CERTIFICATES------------------------------------------
certList = {} 
certName = ""

with open('CompSciCertificatesText.txt') as input_file:
    for line in input_file:
        lineList = line.split(",")
        certName = lineList[0] #first element will be the certificate name
        certList[certName] = [] #certName as key, new list for each course
        
        for index, course in enumerate(lineList):
            if index > 0:
                certList[certName].append(course)#add courses to certList

        

def certCompare(requiredCourses, studentCourses):
    completedCourses = []
    
    for studCourse in studentCourses:
        for reqCourse in requiredCourses:
            if reqCourse.find(studCourse) != -1:
                completedCourses.append(studCourse)
                
    return completedCourses


#returns a list
def studentClassList(studentInfo): #take a student and split the class line to only get the department and class number
    studentClasses = [] #classes taken will be added to studentClasses list
    for i, info in enumerate(studentInfo):
        if i > 0: #Indices past 0 contains class info
            classCompleted = info.split()
            classCompleted = classCompleted[0] + " " + classCompleted[1] #get the department and number
            studentClasses.append(classCompleted)

    #removes duplicates in the list
    studentClasses = set(studentClasses)
    return studentClasses

def checkCerts():
    for studentName in studentList: #take individual student
        studentInfo = studentList[studentName] #make a list of the classes student has taken
        print("Student Name:", studentName)
        print("Student ID: ", studentInfo[0])
        studentCourses = studentClassList(studentInfo) #call the studentClassList function to filter classes only

        for cert in certList:
            completedCourses = certCompare(certList[cert], studentCourses)
        
            if len(completedCourses) >= len(certList[cert]):
                print(cert)
                for course in completedCourses:
                    print("\t", course)
                

checkCerts()  