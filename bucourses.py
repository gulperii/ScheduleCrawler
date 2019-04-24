# TODO: nbsp ne????? yok et ?????


import urllib.request
import sys
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

beginArg = sys.argv[1]
endArg = sys.argv[2]
mainUrl = "https://registration.boun.edu.tr/scripts/sch.asp?donem="
hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
depAndAbbr = [('ASIAN STUDIES', 'ASIA'), ('ASIAN STUDIES WITH THESIS', 'ASIA'),
              ('ATATURK INSTITUTE FOR MODERN TURKISH HISTORY', 'ATA'), ('AUTOMOTIVE ENGINEERING', 'AUTO'),
              ('BIOMEDICAL ENGINEERING', 'BM'), ('BUSINESS INFORMATION SYSTEMS', 'BIS'),
              ('CHEMICAL ENGINEERING', 'CHE'), ('CHEMISTRY', 'CHEM'), ('CIVIL ENGINEERING', 'CE'),
              ('COGNITIVE SCIENCE', 'COGS'), ('COMPUTATIONAL SCIENCE & ENGINEERING', 'CSE'),
              ('COMPUTER EDUCATION & EDUCATIONAL TECHNOLOGY', 'CET'), ('COMPUTER ENGINEERING', 'CMPE'),
              ('CONFERENCE INTERPRETING', 'INT'),
              ('CONSTRUCTION ENGINEERING AND MANAGEMENT', 'CEM'), ('CRITICAL AND CULTURAL STUDIES', 'CCS'),
              ('EARTHQUAKE ENGINEERING', 'EQE'), ('ECONOMICS', 'EC'), ('ECONOMICS AND FINANCE', 'EF'),
              ('EDUCATIONAL SCIENCES', 'ED'), ('EDUCATIONAL TECHNOLOGY', 'CET'),
              ('ELECTRICAL & ELECTRONICS ENGINEERING', 'EE'), ('ENGINEERING AND TECHNOLOGY MANAGEMENT', 'ETM'),
              ('ENVIRONMENTAL SCIENCES', 'ENV'), ('ENVIRONMENTAL TECHNOLOGY', 'ENVT'), ('EXECUTIVE MBA', 'XMBA'),
              ('FINANCIAL ENGINEERING', 'FE'), ('FINE ARTS', 'PA'), ('FOREIGN LANGUAGE EDUCATION', 'FLED'),
              ('GEODESY', 'GED'), ('GEOPHYSICS', 'GPH'), ('GUIDANCE & PSYCHOLOGICAL COUNSELING', 'GUID'),
              ('HISTORY', 'HIST'), ('HUMANITIES COURSES COORDINATOR', 'HUM'), ('INDUSTRIAL ENGINEERING', 'IE'),
              ('INTERNATIONAL COMPETITION AND TRADE', 'INCT'),
              ('INTERNATIONAL RELATIONS:TURKEY,EUROPE AND THE MIDDLE EAST', 'MIR'),
              ('INTERNATIONAL RELATIONS:TURKEY,EUROPE AND THE MIDDLE EAST WITH THESIS', 'MIR'),
              ('INTERNATIONAL TRADE', 'INTT'), ('INTERNATIONAL TRADE MANAGEMENT', 'INTT'), ('LEARNING SCIENCES', 'LS'),
              ('LINGUISTICS', 'LING'),
              ('MANAGEMENT', 'AD'), ('MANAGEMENT INFORMATION SYSTEMS', 'MIS'), ('MATHEMATICS', 'MATH'),
              ('MATHEMATICS AND SCIENCE EDUCATION', 'SCED'), ('MECHANICAL ENGINEERING', 'ME'),
              ('MECHATRONICS ENGINEERING', 'MECA'), ('MOLECULAR BIOLOGY & GENETICS', 'BIO'), ('PHILOSOPHY', 'PHIL'),
              ('PHYSICAL EDUCATION', 'PE'), ('PHYSICS', 'PHYS'), ('POLITICAL SCIENCE&INTERNATIONAL RELATIONS', 'POLS'),
              ('PRIMARY EDUCATION', 'PRED'), ('PSYCHOLOGY', 'PSY'), ('SCHOOL OF FOREIGN LANGUAGES', 'YADYOK'),
              ('SECONDARY SCHOOL SCIENCE AND MATHEMATICS EDUCATION', 'SCED'),
              ('SOCIAL POLICY WITH THESIS', 'SPL'), ('SOCIOLOGY', 'SOC'), ('SOFTWARE ENGINEERING', 'SWE'),
              ('SOFTWARE ENGINEERING WITH THESIS', 'SWE'), ('SUSTAINABLE TOURISM MANAGEMENT', 'TRM'),
              ('SYSTEMS & CONTROL ENGINEERING', 'SCO'), ('TOURISM ADMINISTRATION', 'TRM'), ('TRANSLATION', 'WTR'),
              ('TRANSLATION AND INTERPRETING STUDIES', 'TR'), ('TURKISH COURSES COORDINATOR', 'TK'),
              ('TURKISH LANGUAGE & LITERATURE', 'TKL'), ('WESTERN LANGUAGES & LITERATURES', 'LL')]


def constructDates(arg):
    if (arg.split('-')[1] == 'Fall'):
        term = 1
        year = int(arg.split('-')[0])
        year2 = year + 1
    elif (arg.split('-')[1] == 'Summer'):
        term = 3
        year = int(arg.split('-')[0]) -1
        year2 = year + 1
    else:
        term = 2
        year = int(arg.split('-')[0]) - 1
        year2 = year + 1

    return str(year) + "/" + str(year2) + "-" + str(term)


endDate = constructDates(endArg)
beginDate = constructDates(beginArg)
dates=[]

def constructDateInterval(beginDate, endDate):
    dates.append(beginDate)
    beginTerm = int(beginDate.split('-')[1])
    beginYear = int(beginDate.split('/')[0])
    date = beginDate
    while(date != endDate):
        if(beginTerm !=3):
             date = str(beginYear) + "/" + str(beginYear + 1) + "-" + str(beginTerm+1)
             dates.append(date)
             beginTerm+=1

        else:
            beginTerm =1
            beginYear = beginYear+1
            date = str(beginYear) + "/" + str(beginYear+1) + "-" + str(beginTerm)
            dates.append(date)


constructDateInterval(beginDate,endDate)

columns = ['Dept./Prog.(name)','Course Code','Course Name']
for date in dates:
    columns.append(date)

columns.append('Total Offerings')

df = pd.DataFrame(columns=columns)
print(len(depAndAbbr))

def constructUrls(date, deptAbbr):
    deptName, abbr = deptAbbr
    deptName = deptName.replace(" ", "+").replace("&", "%26")
    return mainUrl + date + "&kisaadi=" + abbr + "&bolum=" + deptName


for date in dates:
    for deptAbbrPair in depAndAbbr:
        request = urllib.request.Request(constructUrls(date, deptAbbrPair), headers=hdr)
        response = urllib.request.urlopen(request)
        soupObj = BeautifulSoup(response.read(), features="html.parser")

        for item in soupObj.findAll('tr', {'class': ['schtd','schtd2']}):
            courseCode = item.findAll('td')[0].text
            courseName = item.findAll('td')[2].text
            courseInstructor = item.findAll('td')[5].text
            print(courseCode, courseName, courseInstructor)


