# TODO: nbsp ne????? yok et ?????
# TODO: deal with staff
import urllib.request
import sys
import collections
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import csv

beginArg = sys.argv[1]
endArg = sys.argv[2]
mainUrl = "https://registration.boun.edu.tr/scripts/sch.asp?donem="
hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
depAndAbbr = [('WESTERN LANGUAGES & LITERATURES', 'LL')]


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


endDate = constructDates(endArg)
beginDate = constructDates(beginArg)
dates = []


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

columns = ['Dept./Prog.(name)', 'Course Code', 'Course Name']
for date in dates:
    columns.append(date)

columns.append('Total Offerings')


def constructUrls(date, deptAbbr):
    deptName, abbr = deptAbbr
    deptName = deptName.replace(" ", "+").replace("&", "%26")
    return mainUrl + date + "&kisaadi=" + abbr + "&bolum=" + deptName


class Department:
    allCourseSet = set()
    allInstructorSet = set()
    departmentName = ""
    departmentAbbr = ""
    totalCourseDiv = [0, 0]
    firstRow = [0] * len(columns)
    totOffU = 0
    totOffG = 0

    def __init__(self, deptPairAbbr, dates):
        name, abbr = deptPairAbbr
        self.departmentName = name
        self.departmentAbbr = abbr
        self.classesByTerm = {term: collections.OrderedDict() for term in dates}

    def firstRowInfo(self):
        self.firstRow[0] = self.departmentAbbr + " (" + self.departmentName + ")"
        self.firstRow[1] = "U" + str(self.totalCourseDiv[0]) + " G" + str(self.totalCourseDiv[1])
        a = 3
        for date in dates:

            self.totOffU += self.classesByTerm[date]["courseDiv"][0]
            self.totOffG += self.classesByTerm[date]["courseDiv"][1]
            self.firstRow[a] = "U" + str(self.classesByTerm[date]["courseDiv"][0]) + " G" + str(
                self.classesByTerm[date]["courseDiv"][1]) + " I" + str(self.classesByTerm[date]["uniqueIns"])
            a += 1
        self.firstRow[-1] = "U" + str(self.totOffU) + " G" + str(self.totOffG) + " I" + str(len(self.allInstructorSet))
        return self.firstRow


deptObjList = []

for pair in depAndAbbr:
    deptObjList.append(Department(pair, dates))

for deptAbbrPair in depAndAbbr:
    index = 0
    for date in dates:
        # for specifc date
        request = urllib.request.Request(constructUrls(date, deptAbbrPair), headers=hdr)
        response = urllib.request.urlopen(request)
        soupObj = BeautifulSoup(response.read(), features="html.parser")
        classesDict = collections.OrderedDict()
        underGrad = [0, 0]
        uniqueIns = set()
        for item in soupObj.findAll('tr', {'class': ['schtd', 'schtd2']}):
            # for course
            courseCode = item.findAll('td')[0].text.split('.')[0].replace(u'\xa0', u'')
            courseName = item.findAll('td')[2].text.replace(u'\xa0', u'')
            try:
                courseCode[-3]
            except:
                continue

            courseInstructor = item.findAll('td')[5].text.replace(u'\xa0', u'')
            deptObjList[index].allCourseSet.add((courseCode, courseName))
            deptObjList[index].allInstructorSet.add(courseInstructor)
            uniqueIns.add(courseInstructor)
            try:
                if int(courseCode[-3]) >= 5:
                    deptObjList[index].totalCourseDiv[1] += 1
                    underGrad[1] += 1
                else:
                    deptObjList[index].totalCourseDiv[0] += 1
                    underGrad[0] += 1
            except:
                deptObjList[index].totalCourseDiv[0] += 1
                underGrad[0] += 1

            if courseName in classesDict:
                classesDict[courseName].append(courseInstructor)
            else:
                classesDict[courseName] = [courseInstructor]
        classesDict["courseDiv"] = underGrad
        classesDict["uniqueIns"] = len(uniqueIns)
        deptObjList[index].classesByTerm[date] = classesDict

    index += 1

with open('mycsv.csv', 'w') as f:
    theWriter = csv.writer(f)
    theWriter.writerow(columns)
    for dept in deptObjList:
        theWriter.writerow(dept.firstRowInfo())
