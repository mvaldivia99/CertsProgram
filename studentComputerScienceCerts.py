studentList = {} #contains list of student info
name = ""

def addClass(docLine): #adds a class to a student's information
    docLine = docLine[4:36] #remove everything except the department, #, and class name
    studentList[name].append(docLine) #add the class to the student's information
    
with open('StudentAuditSample.txt') as input_file:
    for line in input_file:
        if line.find("Student Name:") != -1:#find when the student name begins
            line = line[59:] #remove everything from the line but the last and first name
            name = line.split() #split the name into two parts and remove \n
            name = name[1] + " " + name[0]
            studentList[name] = [] #add student name as key in dictionary, make a new list for each student
            
        if line.find("Student ID:") != -1: #find student ID
            line = line[59:] #remove everything from line but ID
            studentID = line.split() #remove any blank spaces or \n at line ends
            studentList[name].append(studentID[0]) #add student ID to student's info

        #find when class was taken; indicates that the class had been taken
        if line.find("Fal 2") != -1 or line.find("Spr 2") != -1 or line.find("Win 2") != -1 or line.find("Sum 2") != -1: 
            if line.find("*") == -1 and line.find("0.0") == -1 and (line.find("[") == -1):
                #find CS Classes
                if line.find("CS 1") != -1 or line.find("CS 2") != -1: #if the class is a CS class
                    #* - class is in progress; 0.0 - insufficient grade; [3]- insufficient grade(see audit report)
                    if line.find("*") == -1 and line.find("0.0") == -1 and (line.find("[") == -1): #if CS class was successfully completed
                        addClass(line) #add class to student list

                #find psych/soc/bus classes
                if line.find("BUS 120") != -1 or line.find("PSYC& 100") or line.find("SOC& 101") != -1:
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
            print(info) #print classes and certificate"""
