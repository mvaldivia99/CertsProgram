from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, NoSuchWindowException, UnexpectedAlertPresentException
from tkinter import Tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import time
   
SSIDnum = 0
PINnum = 0
path_to_chromedriver = " "

#get the adp credenials
with open('adp_credentials.txt') as input_file:
    for i, line in enumerate(input_file):
        if i == 0:
            SSIDnum = line
        if i == 1:
            PINnum = line

#get the path to chromedriver
with open('chromedriver_path.txt') as input_file:
    for i, line in enumerate(input_file):
        if i == 0:
            path_to_chromedriver = line.strip()

root = Tk()
root.withdraw()
studentIDList = []

#opens file path prompt for files needed
print("Choose a path to student ID text file")
path_to_studentIDFile = askopenfilename(filetypes=[('Text Files','*.txt')], title='Select Student ID text file')

print("Choose a path to certificate requirements text file")
path_to_CertTxtFile = askopenfilename(filetypes=[('Text Files','*.txt')],title='Select Certificate Requirements text file')

with open(path_to_studentIDFile) as input_file:
    for line in input_file:
        studentIDList.append(line)

def errorParsing(errorStr):
    messagebox.showinfo("Error", errorStr)
    browser.quit()

print("\n\tStudent ID's have been read from file\n")

#create a new file that will contain all student Info
auditFileName = "StudentAudit.txt"
newAudit = open(auditFileName, "w+")

#intialize driver
browser = webdriver.Chrome(executable_path=path_to_chromedriver)

#get the URL
url = r'https://adp.bigbend.edu/adp/Login.aspx'
browser.get(url)

while True:
    try:
        #get the SSID input box and input SSID
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_TextBox_Sid"]""").send_keys(SSIDnum)

        #get the PIN input box and input PIN
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_TextBox_Pin"]""").send_keys(PINnum)
        
        #get the login button and click
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Button_Login"]""").click()

        time.sleep(1)
        
        #if len(browser.find_elements_by_xpath("""//*//*[@id="ctl00_ContentPlaceHolder_Main_Label_Error"]""")) > 0:
         #   errorParsing("Invalid credentials; check credentials document")
          #  break   
        time.sleep(2)
        
        break
    except (StaleElementReferenceException, NoSuchElementException) as e:
        time.sleep(3)
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_TextBox_Sid"]""").clear()
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_TextBox_Pin"]""").clear()
        time.sleep(1)
        continue

while True:
    try:
        #click ACCEPT on FERPA
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Button_Accept"]""").click()
        break
    except(StaleElementReferenceException, NoSuchElementException) as e:
        time.sleep(1)
        continue

#get the first student ID on the list
studentID = studentIDList[0]

time.sleep(3)

#When StaleElementException is raised the program keeps trying until it can find the element
while True:
    try:
        #locate studentID field and input studentID
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_TextBox_Sid"]""").send_keys(studentID)
        time.sleep(1)
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Button_SidSearch"]""").click() #search button click
        time.sleep(2)
        
        if browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Label_SearchMessage"]""").text == "No Student Found":
            errorParsing("No Student found; check Student ID document input")
            break
        else:        
            browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_GridView_Students_ctl02_Button_SelectStudent"]""").click() #select student
            time.sleep(2)

        time.sleep(1)
        break
    except (StaleElementReferenceException, NoSuchElementException) as e:
        browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_TextBox_Sid"]""").clear()
        time.sleep(2)
        continue

time.sleep(1)

def writeStudentAudit():
    #prevent StaleElementException
    studentName = ""
    studentID = ""
    while True:
        try:
            #get student name and studentID
            studentName = browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Panel_BSI_Hider"]/div/div/table/tbody/tr[1]/td[2]/strong""").text
            studentID = browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Panel_BSI_Hider"]/div/div/table/tbody/tr[2]/td[2]""").text
            time.sleep(1) 
            break
        except (StaleElementReferenceException, NoSuchElementException, UnexpectedAlertPresentException) as e: #EDIT 4/3/2018: ADDED UNEXPECTREDALERTPRESENTEXCEPTION
            if type(e) == UnexpectedAlertPresentException:
                alert = browser.switch_to.alert
                alert.dismiss()

            studentName = ""
            time.sleep(1)
            continue

    time.sleep(1)
    while True:
        try:
            browser.find_element_by_xpath("""//*[@id="ctl00_ContentPlaceHolder_Main_Image_UnofficialTranscript"]""").click()
            time.sleep(1)
            break
        except NoSuchElementException as e:
            time.sleep(1)
            continue
        
    print("Appending audit for student ", studentName, studentID)
    time.sleep(1)

    #create a list for table rows tag
    tableRows = []

    #find all elements with tag name table row [tr] and add to list
    tableRows = browser.find_elements_by_tag_name("tr")
    courseFlagStart = 0 #indicates when the courses begin in table rows
    courses = []
    #find courses in table rows list
    for row in tableRows:
        if row.text.find("Course") != -1:
            courseFlagStart = 1
            
        if courseFlagStart == 1:                
            #create a line that states when the transfer courses begin
            if row.text.find("YRQ") != -1 and row.text.find("Eval") != -1:
                courses.append("---- TRANSFER-IN COURSES BEGIN HERE ----")
            #row must contain a period to indicate a valid GPA and not dashes or asterisks
            if row.text.find(".") != -1 and row.text.find("-") == -1 and row.text.find("*") == -1 and row.text.find("0.0") == -1:
                courses.append(row.text)
        else:
            continue

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
        except (StaleElementReferenceException, NoSuchElementException) as e:
            browser.find_element_by_xpath("""//*[@id="ctl00_TextBox_LoadedStudentSid"]""").clear()
            time.sleep(1)
            continue

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
            continue
        
        if line.find("Student ID:") != -1: #find student ID
            line = line[12:] #remove everything from line but ID
            studentID = line.split() #remove any blank spaces or \n at line ends
            studentList[name].append(studentID[0]) #add student ID to student's info
            continue

        #audit contains a line that marks where courses begin
        #any line after that will be added differently
        if line.find("TRANSFER-IN COURSES BEGIN HERE") != -1:
            TRCrsFlag = 1
            pass
        if TRCrsFlag == 1 and line.find("TRANSFER-IN COURSES BEGIN HERE") == -1 and not line.isspace(): #line is under transfer courses line and not whitespace
            addTRClass(line)
        else:
            if not line.isspace(): #checks if the line is whitespace
                addClass(line)
#------------------------------COMPARE COURSES AGAINST CERTIFICATES------------------------------------------
certList = {} 
certName = ""

with open(path_to_CertTxtFile) as input_file:
    for line in input_file:
        if line.find(":") != -1: #top line will have a : symbol
            certName = line.strip()
            certList[certName] = []
        elif line.find("1") != -1 or line.find("2") != -1 or line.find("*") and not line.isspace(): #find a course
            cert_str = line.strip()
            certList[certName].append(cert_str)
        
#returns a list of courses that student has completed on course
def certCompare(requiredCourses, studentCourses):
    completedCourses = [] 
    electivesList = [] 

    for reqCourse in requiredCourses:
        if reqCourse.find("*") != -1:
            electivesList.append(reqCourse)
            continue
        for studCourse in studentCourses:
            if reqCourse.find(studCourse) != -1: #if the student has the required course
                completedCourses.append(studCourse)
                break

    #1/14/2018 Edit: If all the completed courses meet the required courses
    # Skip looking for the electives        
    if len(completedCourses) == len(requiredCourses):
        return completedCourses

    if len(electivesList) > 0: #if there are elements in the electives list
        for reqCourse in electivesList:
            strList_reqCourse = reqCourse.split() #split string into a list
            astIndex = strList_reqCourse.index("*")  #find index of asterisk
            deptCode = strList_reqCourse[astIndex - 1] #get the dept code that will be index before asterisk

            for studCourse in studentCourses:
                if studCourse in completedCourses: #if the student course has already been counted
                    continue #keep going
                else:
                    str_studCourse = studCourse.split()
                    str_studCourseDept = str_studCourse[0] #first element will be student course dept code

                    if reqCourse.find(studCourse) != -1:
                        completedCourses.append(studCourse)
                        break
                    elif str_studCourseDept == deptCode:
                        completedCourses.append(studCourse)
                        break
              
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

                

studentCertFile = open("StudentCerts.txt", "w+")

def checkCerts():
    certCount = 0
    for studentName in studentList: #take individual student
        studentInfo = studentList[studentName] #make a list of the classes student has taken
        studentCourses = studentClassList(studentInfo) #call the studentClassList function to filter classes only
        didPrintName = 0
        for cert in certList:
            #get a list of student courses that have been completed
            completedCourses = certCompare(certList[cert], studentCourses)
            
            
            if len(completedCourses) == len(certList[cert]): #if a certificate is found
                if didPrintName == 0:
                    studentCertFile.write("\nStudent Name:" + studentName)
                    studentCertFile.write("\nStudent ID: " + studentInfo[0])
                    didPrintName = 1
                                    
                studentCertFile.write("\n" + cert) #add to student cert text file
                    
                certCount += 1
                for course in completedCourses:
                    studentCertFile.write("\n\t" + course) #write the courses

                print("\n\n")
                    
    print("Number of certificates found: ", certCount)
    
checkCerts()
print("Program complete")
