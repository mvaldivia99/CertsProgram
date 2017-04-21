certList = {} 
certName = ""

#VVVtestVVV
studentCourses = ["CS 101","CS 104","CS 105","CS 156","CS 157","CS 158","CS 159","SOC& 101","CMST& 220","ENGL& 101","FAD 150","MATH& 141"]

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

for cert in certList:
    completedCourses = certCompare(certList[cert], studentCourses)
    
    if len(completedCourses) >= len(certList[cert]):
        print(completedCourses)
        print(cert)

        
        
