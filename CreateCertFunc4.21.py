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

        

        
        
