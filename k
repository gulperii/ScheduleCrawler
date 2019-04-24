import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from email.mime.text import MIMEText

import requests
import xlsxwriter
from bs4 import BeautifulSoup


pageUrl = "https://boxofficeturkiye.com/vizyon/"
mainPage = requests.get(pageUrl, headers={'User-agent': 'Mozilla/5.0'})
mainPageContent = BeautifulSoup(mainPage.content, "html.parser")
links = []

fileName = "film" + datetime.today().strftime("%Y-%m") + ".xlsx"
workbook = xlsxwriter.Workbook(fileName)
worksheet = workbook.add_worksheet()
rowTitle = 0
colTitle = 0
bold = workbook.add_format({'bold': True})

titles = ['Film Adı', 'Vizyon Tarihi', 'TR Dağıtım', 'Şirket', 'Film Türü', 'Konusu', 'Ülke', 'Yönetmen', 'Oyuncular']

for title in titles:
    worksheet.write(rowTitle, colTitle, title, bold)
    colTitle += 1

for item in mainPageContent.findAll('a', {'class': 'film'}):
    link = pageUrl[:-8] + item['href']
    name = item['title']
    pair = (name, link)
    links.append(pair)

rowFilm = 1
for pair in links:
    colFilm = 0
    (name, link) = pair
    page = requests.get(link, headers={'User-agent': 'Mozilla/5.0'})
    pageContent = BeautifulSoup(page.content, "html.parser")

    try:
        items = pageContent.findAll('td', {'class': 'movie-summary-value'})
    except IndexError:
        items = "null"
    try:
        releaseDate = items[0].get_text().replace("\n", " ")
    except IndexError:
        releaseDate = "null"
    try:
        trCompany = items[1].get_text()
    except IndexError:
        trCompany = "null"
    try:
        company = items[2].get_text()
    except IndexError:
        company = "null"
    try:
        genre = items[3].get_text().replace(" ", "").replace('\r\n', " ")
    except IndexError:
        genre = "null"
    try:
        topic = \
        pageContent.findAll('span', {'class': 'spot'}, limit=1)[0].get_text().replace("\n", " ").split("Devamı")[
            0]
    except IndexError:
        topic = 'null'

    country = pageContent.find('img', {'class': 'cercevesiyah'}, width=25).get('title')

    cast = pageContent.find('div', {'id': 'movieCast'}).get_text().split("\n")

    modifiedCast = list(filter(lambda x: x != "" and x != "'", cast))

    directors = []
    actors = []

    actorIndex = 0

    try:
        directorIndex = modifiedCast.index('Yönetmen')
    except ValueError:
        directorIndex = -1
    try:
        actorIndex = modifiedCast.index('Oyuncular')
    except ValueError:
        actorIndex = -1
    try:
        screenwriterIndex = modifiedCast.index('Senaryo')
    except ValueError:
        screenwriterIndex = -1

    if (directorIndex != -1):
        if (actorIndex != -1):
            directors = modifiedCast[directorIndex + 1:actorIndex]
            if (screenwriterIndex != -1):
                actors = modifiedCast[actorIndex + 1:screenwriterIndex]
            else:
                actors = modifiedCast[actorIndex + 1:]
        elif (screenwriterIndex != -1):
            directors = modifiedCast[directorIndex + 1:screenwriterIndex]
        else:
            directors = modifiedCast[directorIndex + 1:]

    allnfo = [name, releaseDate, trCompany, company, genre, topic, country, str(directors)[1:-1], str(actors)[1:-1]]

    for info in allnfo:
        worksheet.write(rowFilm, colFilm, info)
        colFilm += 1
    rowFilm += 1

workbook.close()

username = 'hobot@yga.org.tr'
password = '%663KienOVTQ6S$'
send_from = 'hobot@yga.org.tr'
send_to = 'hobot@yga.org.tr'
msg = MIMEMultipart()
msg['From'] = send_from
msg['To'] = send_to
msg['Date'] = formatdate(localtime=True)
msg['Subject'] = "Excel attachment"
msg.attach(MIMEText("Ayın vizyon filmleri"))
part = MIMEBase('application', "octet-stream")
part.set_payload(open(fileName, "rb").read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="' + fileName + '"')
msg.attach(part)
smtp = smtplib.SMTP('smtp.office365.com', 587)
smtp.ehlo()
smtp.starttls()
smtp.login(username, password)
smtp.sendmail(send_from, send_to, msg.as_string())
smtp.quit()

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)