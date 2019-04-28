# TODO: timout
import urllib.request
import sys
import collections
from bs4 import BeautifulSoup
import csv

# arguments
beginArg = sys.argv[1]
endArg = sys.argv[2]

# base url
mainUrl = "https://registration.boun.edu.tr/scripts/sch.asp?donem="
hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}

# department and corresponding abbreviation list
depAndAbbr = [('MANAGEMENT', 'AD'), ('ASIAN STUDIES', 'ASIA'), ('ASIAN STUDIES WITH THESIS', 'ASIA'),
              ('ATATURK INSTITUTE FOR MODERN TURKISH HISTORY', 'ATA'), ('AUTOMOTIVE ENGINEERING', 'AUTO'),
              ('MOLECULAR BIOLOGY & GENETICS', 'BIO'), ('BUSINESS INFORMATION SYSTEMS', 'BIS'),
              ('BIOMEDICAL ENGINEERING', 'BM'), ('CRITICAL AND CULTURAL STUDIES', 'CCS'), ('CIVIL ENGINEERING', 'CE'),
              ('CONSTRUCTION ENGINEERING AND MANAGEMENT', 'CEM'),
              ('COMPUTER EDUCATION & EDUCATIONAL TECHNOLOGY', 'CET'), ('EDUCATIONAL TECHNOLOGY', 'CET'),
              ('CHEMICAL ENGINEERING', 'CHE'), ('CHEMISTRY', 'CHEM'), ('COMPUTER ENGINEERING', 'CMPE'),
              ('COGNITIVE SCIENCE', 'COGS'), ('COMPUTATIONAL SCIENCE & ENGINEERING', 'CSE'),
              ('ECONOMICS', 'EC'), ('EDUCATIONAL SCIENCES', 'ED'), ('ELECTRICAL & ELECTRONICS ENGINEERING', 'EE'),
              ('ECONOMICS AND FINANCE', 'EF'), ('ENVIRONMENTAL SCIENCES', 'ENV'), ('ENVIRONMENTAL TECHNOLOGY', 'ENVT'),
              ('EARTHQUAKE ENGINEERING', 'EQE'), ('ENGINEERING AND TECHNOLOGY MANAGEMENT', 'ETM'),
              ('FINANCIAL ENGINEERING', 'FE'),
              ('FOREIGN LANGUAGE EDUCATION', 'FLED'), ('GEODESY', 'GED'), ('GEOPHYSICS', 'GPH'),
              ('GUIDANCE & PSYCHOLOGICAL COUNSELING', 'GUID'), ('HISTORY', 'HIST'),
              ('HUMANITIES COURSES COORDINATOR', 'HUM'),
              ('INDUSTRIAL ENGINEERING', 'IE'), ('INTERNATIONAL COMPETITION AND TRADE', 'INCT'),
              ('CONFERENCE INTERPRETING', 'INT'),
              ('INTERNATIONAL TRADE', 'INTT'), ('INTERNATIONAL TRADE MANAGEMENT', 'INTT'),
              ('LINGUISTICS', 'LING'), ('WESTERN LANGUAGES & LITERATURES', 'LL'), ('LEARNING SCIENCES', 'LS'),
              ('MATHEMATICS', 'MATH'), ('MECHANICAL ENGINEERING', 'ME'), ('MECHATRONICS ENGINEERING', 'MECA'),
              ('INTERNATIONAL RELATIONS:TURKEY,EUROPE AND THE MIDDLE EAST', 'MIR'),
              ('INTERNATIONAL RELATIONS:TURKEY,EUROPE AND THE MIDDLE EAST WITH THESIS', 'MIR'),
              ('MANAGEMENT INFORMATION SYSTEMS', 'MIS'), ('FINE ARTS', 'PA'), ('PHYSICAL EDUCATION', 'PE'),
              ('PHILOSOPHY', 'PHIL'), ('PHYSICS', 'PHYS'), ('POLITICAL SCIENCE&INTERNATIONAL RELATIONS', 'POLS'),
              ('PRIMARY EDUCATION', 'PRED'), ('PSYCHOLOGY', 'PSY'),
              ('SECONDARY SCHOOL SCIENCE AND MATHEMATICS EDUCATION', 'SCED'),
              ('SYSTEMS & CONTROL ENGINEERING', 'SCO'), ('SOCIOLOGY', 'SOC'), ('SOCIAL POLICY WITH THESIS', 'SPL'),
              ('SOFTWARE ENGINEERING', 'SWE'),
              ('SOFTWARE ENGINEERING WITH THESIS', 'SWE'), ('TURKISH COURSES COORDINATOR', 'TK'),
              ('TURKISH LANGUAGE & LITERATURE', 'TKL'), ('TRANSLATION AND INTERPRETING STUDIES', 'TR'),
              ('TOURISM ADMINISTRATION', 'TRM'),
              ('SUSTAINABLE TOURISM MANAGEMENT', 'TRM'), ('TRANSLATION', 'WTR'), ('EXECUTIVE MBA', 'XMBA'),
              ('SCHOOL OF FOREIGN LANGUAGES', 'YADYOK'), ('MATHEMATICS AND SCIENCE EDUCATION', 'SCED')]


# To transform the argument dates (eg: 2018-Fall) to Url-form (2018/2019-1)
def constructDates(arg):
    if (arg.split('-')[1] == 'Fall'):
        term = 1
        year = int(arg.split('-')[0])
        year2 = year + 1
    elif (arg.split('-')[1] == 'Summer'):
        term = 3
        year = int(arg.split('-')[0]) - 1
        year2 = year + 1
    else:
        term = 2
        year = int(arg.split('-')[0]) - 1
        year2 = year + 1

    return str(year) + "/" + str(year2) + "-" + str(term)


def deconstructDates(date):
    if (date.split("-")[1] == 1):
        return str(date.split("/")[0]) + "-" + "Fall"
    else:
        if (date.split("-")[1] == 2):
            return str(date.split("/")[1].split("-")[0]) + "-" + "Spring"
        else:
            return str(date.split("/")[1].split("-")[0]) + "-" + "Summer"


endDate = constructDates(endArg)
beginDate = constructDates(beginArg)

# List to store the terms to crawl(in URL-friendly form)
dates = []


# Given an end and a begin term, produces the terms in between in url-form
def constructDateInterval(beginDate, endDate):
    dates.append(beginDate)
    beginTerm = int(beginDate.split('-')[1])
    beginYear = int(beginDate.split('/')[0])
    date = beginDate
    while (date != endDate):
        if (beginTerm != 3):
            date = str(beginYear) + "/" + str(beginYear + 1) + "-" + str(beginTerm + 1)
            dates.append(date)
            beginTerm += 1

        else:
            beginTerm = 1
            beginYear = beginYear + 1
            date = str(beginYear) + "/" + str(beginYear + 1) + "-" + str(beginTerm)
            dates.append(date)


constructDateInterval(beginDate, endDate)

# Column Names
columns = ['Dept./Prog.(name)', 'Course Code', 'Course Name']
for date in dates:
    columns.append(deconstructDates(date))

columns.append('Total Offerings')


# Given a date and a department, constructs the url for accessing the schedule
# Blank space is replaced by + and & is replaced by %26
def constructUrls(date, deptAbbr):
    deptName, abbr = deptAbbr
    deptName = deptName.replace(" ", "+").replace("&", "%26")
    return mainUrl + date + "&kisaadi=" + abbr + "&bolum=" + deptName


# Every department is represented by a Department object.
class Department:

    def __init__(self, deptPairAbbr, dates):
        # Name and abbreviation of the department
        name, abbr = deptPairAbbr
        # Total number of undergrad. courses in the given interval (Total Offering)
        self.totOffU = 0
        # Total number of grad. courses in the given interval (Total Offering)
        self.totOffG = 0
        # First Row is a list that keeps the statistics.
        self.firstRow = [0] * len(columns)
        # allCourseSet stores name and abbreviation of every course that is offered in the given interval.
        # set is used to avoid duplicates
        self.allCourseSet = set()
        # allInstructorSet stores name of every instructor for all courses
        self.allInstructorSet = set()
        # This array stores the number of undergrad (0th index) and number of grad (1th index) courses that has been offered in the given interval.(2nd column)
        # Used to avoid iterating allCoursesSet
        self.totalCourseDiv = [0, 0]
        self.departmentName = name
        self.departmentAbbr = abbr
        # This is a dictionary such that keys are terms and values are orderdered dictionaries of course codes (as keys) and course instructors (as values).
        # Ordered dictionary is used to keep the order of the course codes, which are already sorted int the webpage, so that sorting them again is not necessary
        self.classesByTerm = {term: collections.OrderedDict() for term in dates}

    #
    # To construct the statistics for the department
    def firstRowInfo(self):
        self.firstRow[0] = self.departmentAbbr + " (" + self.departmentName + ")"
        self.firstRow[1] = "U" + str(self.totalCourseDiv[0]) + " G" + str(self.totalCourseDiv[1])
        self.firstRow[2] = " "
        a = 3
        # Statistics for each term
        for date in dates:
            # totOfU is the sum of undergrad courses offered in all terms.  So we add the number of yndergard courses of each term together
            self.totOffU += self.classesByTerm[date]["courseDiv"][0]
            # totOfG is the sum of grad courses offered in all terms.  So we add the number of gard courses of each term together
            self.totOffG += self.classesByTerm[date]["courseDiv"][1]
            # Term-specific statistics
            self.firstRow[a] = "U" + str(self.classesByTerm[date]["courseDiv"][0]) + " G" + str(
                self.classesByTerm[date]["courseDiv"][1]) + " I" + str(self.classesByTerm[date]["uniqueIns"])
            a += 1
        # Totatl offerings statistics.
        self.firstRow[-1] = "U" + str(self.totOffU) + " G" + str(self.totOffG) + " I" + str(len(self.allInstructorSet))
        return self.firstRow


# List that stores all departmant objects.
deptObjList = []

# Loop that creates Department objects for each department in the initial list.
for pair in depAndAbbr:
    deptObjList.append(Department(pair, dates))

index = 0
# Main loop to crawl data. We gather info about a department for every term in the range.
for deptAbbrPair in depAndAbbr:
    for date in dates:
        # Make a web request with the url we have constructed tailored to the department and the term
        #Used headers to prevent website from blocking us
        request = urllib.request.Request(constructUrls(date, deptAbbrPair), headers=hdr)
        response = urllib.request.urlopen(request)
        rawHtml = response.read()
        soupObj = BeautifulSoup(rawHtml, features="html.parser")
        # An OrderedDict to keep course codes and the instructors of that course for a specific term.
        # Instructors are stored in a set to avoid duplicates caused by different section of that class
        classesDict = collections.OrderedDict()
        # Keeps track of number of grad / unndergrad courses for a specific term
        underGrad = [0, 0]
        # All instructors for that term and that department, regardless of the course they have given.
        # Set is used to prevent duplicates caused by instructors that gave more than one course
        uniqueIns = set()
        # All classes offered in that department in that term.
        # Set is used to avoid duplicates caused by different sections of that class
        uniqueClasses = set()
        # Fo loop to iterate all courses
        for item in soupObj.findAll('tr', {'class': ['schtd', 'schtd2']}):
            # Name and code of the course,
            courseCode = item.findAll('td')[0].text.split('.')[0].replace(u'\xa0', u'')
            courseName = item.findAll('td')[2].text.replace(u'\xa0', u'')
            # Courses with labs and PSs have extra lines that dont have coursename but instead &nbsp in HTML code.
            # I couldnt properly replace &nbsp character. Instead, I checked if [-3] character exists or not.
            try:
                courseCode[-3]
            except:
                continue

            courseInstructor = item.findAll('td')[5].text.replace(u'\xa0', u'')

            # STAFF is not a distinct instructor, this "if" ensures that.
            if 'STAFF' not in courseInstructor:
                # Add to the set independent of dept and term
                deptObjList[index].allInstructorSet.add(courseInstructor)
                # Add to term and dept specific set
                uniqueIns.add(courseInstructor)
            # Term and date specific set
            uniqueClasses.add(courseCode)

            # This try-except blocks prevents crashing whem encountered with course codes that has letters instead of numbers.
            # Those codes are counted as undergrad courses
            try:
                # If the [-3]th char of the course code is bigger than 4, it is a grad course
                if int(courseCode[-3]) >= 5:
                    # If we have processed another section of that course before, we dont update our statistics.
                    if (courseCode, courseName) not in deptObjList[index].allCourseSet:
                        # Department-specific, term and course independent
                        deptObjList[index].totalCourseDiv[1] += 1
                    if courseCode not in classesDict:
                        # department and term specific, course independent
                        underGrad[1] += 1
                # If it is not a grad course, then it is an undergrad course.
                else:
                    # If we have processed another section of that course before, we dont update our statistics.
                    if courseCode not in classesDict:
                        underGrad[0] += 1
                    if (courseCode, courseName) not in deptObjList[index].allCourseSet:
                        deptObjList[index].totalCourseDiv[0] += 1
            # If it contains letters instead of number in the course code, then it is an undergrad course
            except:
                if courseCode not in classesDict:
                    underGrad[0] += 1
                if (courseCode, courseName) not in deptObjList[index].allCourseSet:
                    deptObjList[index].totalCourseDiv[0] += 1

            # Add the course to all course set(department specific, term independent)
            deptObjList[index].allCourseSet.add((courseCode, courseName))
            if courseCode in classesDict:
                classesDict[courseCode].append(courseInstructor)
            else:
                classesDict[courseCode] = [courseInstructor]
        # Term specific stats of distribution of undergrad vs grad courses
        classesDict["courseDiv"] = underGrad
        # How many distinct instructors are there in that semester for that department
        classesDict["uniqueIns"] = len(uniqueIns)
        # How many distinct courses are there in that department for that semester
        classesDict["uniqueClasses"] = uniqueClasses
        # As we are done with that term, we can insert our ordered dictionary of courses-instructors to our dictionary of terms-course info.
        deptObjList[index].classesByTerm[date] = classesDict
    # to iterate thorough the department list.
    index += 1

# Writes to stdout in csv format, seperator character is semicolon
theWriter = csv.writer(sys.stdout, delimiter=";")
# First write the header
theWriter.writerow(columns)

for i in range(len(deptObjList)):
    # For every department we first write the statistics.
    theWriter.writerow(deptObjList[i].firstRowInfo())
    # We sort our course list and write course-specific stats row by row.
    uniqueCourseList = list(deptObjList[i].allCourseSet)
    uniqueCourseList.sort()
    for course in uniqueCourseList:
        code, name = course
        row = [" ", code, name]
        howManyTerms = 0
        howManyInst = set()
        for date in dates:
            # As allCourseSet has all courses for all terms, we should check whether the course was offered in this term.
            # If it is, we put a "x" and also add the instructors of the course for that term to the more general set- which contains all instructors
            # that has given that course.
            if code in deptObjList[i].classesByTerm[date]["uniqueClasses"]:
                howManyInst = howManyInst.union(set(deptObjList[i].classesByTerm[date][code]))
                row.append("x")
                howManyTerms += 1
            else:
                row.append(" ")

        row.append(str(howManyTerms) + "/" + str(len(howManyInst)))
        theWriter.writerow(row)
