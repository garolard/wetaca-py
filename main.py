# -*- coding: utf-8 -*-

import sys
import os
from shutil import copyfile
import re
import csv
import logging
import datetime

import aiohttp
import asyncio

from bs4 import BeautifulSoup
from tqdm import tqdm

log = logging.getLogger(__name__)

loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)

baseFolder = os.path.dirname(__name__)
outputFolderPath = 'out'
#gdriveFolderPath = 'D:\Gabriel\Wetacas'
fileName = 'wetaca-weekly-' + datetime.date.today().strftime('%d%m%Y') + '.csv'

def ensure_output_folder_exists():
    if not os.path.exists(os.path.join(baseFolder, outputFolderPath)):
        os.makedirs(os.path.join(baseFolder, outputFolderPath))

def capture_course_links(soup):
    allLinks = [tag['href']
                for tag in soup.find_all(class_=re.compile('lc_google_click'))]
    return set(allLinks)


async def parse_course_info(client, courseLink):
    webContent = await get_url(client, courseLink)
    soup = BeautifulSoup(webContent, 'html.parser')

    courseLabels = [tag.get_text() for tag in soup.find_all(
        'span', attrs={'class': 'LC_name'})]
    courseValues = [tag.get_text() for tag in soup.find_all(
        'span', attrs={'class': 'LC_data'})]

    # Ahora mismo no caigo para que esto no sea tan cutre
    courseLabels.insert(0, 'Plato')
    courseValues.insert(0, soup.title.string.split('-')[0].strip())

    return zip(courseLabels, courseValues)

async def get_url(client, url):
    async with client.get(url) as resp:
        assert resp.status == 200
        return await resp.text()

async def main(client, loop):
    wetacaMenuContent = await get_url(client, 'https://wetaca.com/27-nuestros-platos')
    soup = BeautifulSoup(wetacaMenuContent, 'html.parser')

    courseLinks = capture_course_links(soup)

    # seguro que puede simplificarse para que no quede tan
    # chapuza pero usando list comprehension el http peta
    coursesTasks = []

    log.info('Parseando enlaces')
    print('Parseando enlaces')

    for link in courseLinks:
        coursesTasks.append(parse_course_info(client, link))

    courses = await asyncio.gather(*coursesTasks)

    ensure_output_folder_exists()

    referenceCourse = dict(courses[0])

    # Si los de wetaca son retrasados y no ponen la info del primer plato
    # intento coger los del segundo
    if len(referenceCourse.keys()) == 1:
        fieldnames = dict(courses[1]).keys()
    else:
        fieldnames = referenceCourse.keys()

    fileFullPath = os.path.join(baseFolder, outputFolderPath, fileName)

    with open(fileFullPath, 'w', encoding='utf8') as temp:
        writer = csv.DictWriter(temp, fieldnames=fieldnames)
        writer.writeheader()

        log.info('Escribiendo platos')
        print('Escribiendo platos')
        for c in tqdm(courses):
            d = dict(c)
            writer.writerow(d)

    #copyfile(fileFullPath, os.path.join(gdriveFolderPath, fileName))
    await client.close()

    print('Terminado')

loop.run_until_complete(main(client, loop))
loop.close()
sys.exit(0)
