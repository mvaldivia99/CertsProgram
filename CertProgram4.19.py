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


#----------------------START CERTIFICATE PROGRAM--------------------------------------

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
            
#-------------------Start Certificates Checks------------------------

#returns a bool
def didComplete(requiredCourses, studentClasses):
    didComplete = False
    matchedCourses = 0
    
    for studentCourse in studentClasses:
        for reqCourse in requiredCourses:

            if reqCourse == studentCourse:
                matchedCourses += 1


    if matchedCourses == len(requiredCourses):
        didComplete = True

    return didComplete

#returns list of strings; COMPLETE
def gen_Completed(studentClasses): #see if general classes have been completed; NOT A CERTIFICATE
    
    #check all the classes needed
    #General Classes completion:
             # BUS 120 or PSYCH& 100 or SOC& 101 (needs one of these)
             # CMST 1001 or CMST& 220 (needs one of these)
             # ENGL& 109 or ENGL& 101 (needs one of these)
             # FAD 150 
             # MATH& 141 */

    #create flags for classes that can be substituted
    socScience = 0
    communications = 0
    engl = 0
    fad = 0
    mathCourse = 0
    totalClasses = 5
    coursesTaken = []

    for course in studentClasses:
        if ((course == "BUS 120" or course == "PSYC& 100" or course == "SOC& 101") and socScience == 0):
            coursesTaken.append(course)
            socScience += 1
        if ((course == "CMST 100" or course == "CMST& 220") and communications == 0):
            coursesTaken.append(course)
            communications += 1
        if ((course == "ENGL& 109" or course == "ENGL& 101") and engl == 0):
            coursesTaken.append(course)
            engl += 1
        if course == "FAD 150" and fad == 0:
            coursesTaken.append(course)
            fad += 1
        if course == "MATH& 141" and mathCourse ==0:
            coursesTaken.append(course)
            mathCourse += 1

    if len(coursesTaken) != totalClasses:
        coursesTaken[:] = []
        
    return coursesTaken
    
#returns list of strings              
def cisco_CertAccmp(studentClasses): #Cisco Certificate of Accomplishment
    #cisco certification requires completion of CS 156 - 159
    requiredCourses = ["CS 156", "CS 157", "CS 158", "CS 159"]

    if not didComplete(requiredCourses, studentClasses):
        #clears the list
        requiredCourses[:] = []
    
    return requiredCourses


#returns list of strings
def cisco_CertAchv(studentClasses): #Cisco Certificate of Achievement
    requiredCourses = ["CS 101", "CS 105", "CS 105"]
    
    if len(gen_Completed(studentClasses)) > 0: #check general classes completion
        if didComplete(requiredCourses, studentClasses):
            requiredCourses.extend(gen_Completed(studentClasses))
        else:
            requiredCourses[:] = []
    else:
        requiredCourses[:] = []

    return requiredCourses

#returns list of strings
def compSupportSpecCertAccmp(studentClasses): #Computer Support Spec Cert Accomplishment

    requiredCourses = ["CS 104", "CS 105", "CS 110", "CS 205", "CS 207"]
    if not didComplete(requiredCourses, studentClasses):
        requiredCourses[:] = []
        
    return requiredCourses

#return list of strings
def netSupportSpecCert(studentClasses): #Network Support Spec Cert Accomplishment

    requiredCourses = ["CS 104", "CS 105", "CS 110", "CS 156", "CS 157", "CS 205", "CS 206"]
    if not didComplete(requiredCourses, studentClasses):
        requiredCourses[:] = []

    return requiredCourses

#return list of strings
def sysAdminCertAchv(studentClasses): #SysAdmin Cert Achievement
    requiredCourses = ["CS 104", "CS 105", "CS 106", "CS 110", "CS 156", "CS 157", "CS 205"]
    
    if len(gen_Completed(studentClasses)) > 0: #check general classes completion       
        if didComplete(requiredCourses, studentClasses):
            #remove courses found in studentClasses
            for reqCourse in requiredCourses:
                for studentCourse in studentClasses:
                    if reqCourse == studentCourse:
                        studentClasses.remove(reqCourse)
                        break

            #flag for additional class; needs 1 more
            additionalClass = 0
            
            #find additional CS classes that were not filtered out (electives)
            for studentCourse in studentClasses:
                if ("CS 1" in studentCourse) or ("CS 2" in studentCourse):
                    requiredCourses.append(studentCourse)
                    additionalClass += 1
                    break

            if additionalClass != 1:
                requiredCourses[:] = []
            else:
                requiredCourses.extend(gen_Completed(studentClasses))
                
        else:
            requiredCourses[:] = [] 
    else:
        requiredCourses[:] = []

    return requiredCourses

#returns a list of strings
def webDesignCertAchv(studentClasses): #Web Design Cert Achievment
    requiredCourses = ["CS 104", "CS 105", "CS 111", "CS 115", "CS 161", "CS 265", "CS 271"]
    
    if len(gen_Completed(studentClasses)) > 0: #check general classes completion        
        if didComplete(requiredCourses, studentClasses):
                #remove courses found in studentClasses
                for reqCourse in requiredCourses:
                    for studentCourse in studentClasses:
                        if reqCourse == studentCourse:
                            studentClasses.remove(reqCourse)
                            break

                #flag for additional class; needs 2 more
                additionalClass = 0
                
                #find additional CS classes that were not filtered out (electives)
                for studentCourse in studentClasses:
                    if (("CS 1" in studentCourse) or ("CS 2" in studentCourse)) and additionalClass != 2:
                        requiredCourses.append(studentCourse)
                        additionalClass += 1

                if additionalClass != 2:
                    requiredCourses[:] = []
                else:
                    requiredCourses.extend(gen_Completed(studentClasses))
                
        else:
           requiredCourses[:] = [] 
    else:
        requiredCourses[:] = []

    return requiredCourses
         
        
#-------------------------End of Certificate checks--------------------- 

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
        classesCompleted = studentClassList(studentInfo) #call the studentClassList function to filter classes only

        
        ciscoAccmpCourses = cisco_CertAccmp(classesCompleted)
        ciscoAchvCourses = cisco_CertAchv(classesCompleted)
        specCertCourses = compSupportSpecCertAccmp(classesCompleted)
        netSupportCourses = netSupportSpecCert(classesCompleted)
        webDesignCourses = webDesignCertAchv(classesCompleted)
        sysAdminCourses = sysAdminCertAchv(classesCompleted)

        if len(ciscoAccmpCourses) > 0:#check for cisco accomplishment
            print("Cisco Certificate of Accomplishment")

            for course in ciscoAccmpCourses:
                print("\t" + course)            
            if len(ciscoAchvCourses) > 0: #check for cisco achievement
                print("Cisco Certificate of Achievement")

                for course in ciscoAchvCourses:
                    print("\t" + course)  
        if len(specCertCourses) > 0:
            print("Computer Support Specialist Certificate of Accomplishment")

            for course in specCertCourses:
               print("\t" + course)    
        if len(netSupportCourses) > 0:
            print("Network Support Specialist Certificate of Accomplishment")

            for course in netSupportCourses:
                print("\t" + course) 
                
        if len(sysAdminCourses) > 0:
            print("System Administration Certificate of Achievement")

            for course in sysAdminCourses:
                print("\t" + course) 

        if len(webDesignCourses) > 0:
            print("Web Design Certificate of Achievement")

            for course in webDesignCourses:
                print("\t" + course) 

        
checkCerts() #check each student to see if they have achieved a certificate

"""for studentName in studentList:
    studentInfo = studentList[studentName] #take individual student info  
    print("Student Name:", studentName)
    for i, info in enumerate(studentInfo): #print information of student
        if i == 0:
            print("\tStudent ID: ", info) #first index will always be student ID
        else:
            print(info) #print classes and certificate
"""
