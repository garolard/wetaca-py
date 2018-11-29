# -*- coding: utf-8 -*-

import re
import urllib3
import csv
import logging

from bs4 import BeautifulSoup

# Desactivo esos avisos molestos de que no es una peticion segura, YA SE QUE NO ES SEGURA!!
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

log = logging.getLogger(__name__)

userAgent = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'}
http = urllib3.PoolManager(headers=userAgent)


def captureCourseLinksInSoup(soup):
    links = []
    allLinks = [tag['href']
                for tag in soup.find_all(class_=re.compile('lc_google_click'))]
    # Eliminado duplicados. Podria usar un set pero me joderia el orden
    # de la lista
    for l in allLinks:
        if l not in links:
            links.append(l)
    return links


def parseCourse(courseLink):
    webContent = http.request('GET', courseLink).data.decode('UTF-8', 'ignore')
    soup = BeautifulSoup(webContent, 'html.parser')

    courseLabels = [tag.get_text() for tag in soup.find_all(
        'span', attrs={'class': 'LC_name'})]
    courseValues = [tag.get_text() for tag in soup.find_all(
        'span', attrs={'class': 'LC_data'})]

    course = list(zip(courseLabels, courseValues))

    course.insert(0, ('Plato', soup.title.string.split('-')[0].strip()))
    return course


if __name__ == '__main__':
    wetacaMenuContent = http.request(
        'GET', 'https://wetaca.com/27-nuestros-platos').data.decode('UTF-8', 'ignore')
    soup = BeautifulSoup(wetacaMenuContent, 'html.parser')

    courseLinks = captureCourseLinksInSoup(soup)

    # seguro que puede simplificarse para que no quede tan
    # chapuza pero usando list comprehension el http peta
    courses = []
    for link in courseLinks:
        courses.append(parseCourse(link))

    with open('wetaca-weekly.csv', 'w', encoding='utf8') as temp:
        referenceCourse = dict(courses[0])

        # Si los de wetaca son retrasados y no ponen la info del primer plato
        # intento coger los del segundo
        if len(referenceCourse.keys()) == 1:
            fieldnames = dict(courses[1]).keys()
        else:
            fieldnames = referenceCourse.keys()

        writer = csv.DictWriter(temp, fieldnames=fieldnames)
        writer.writeheader()

        # Si los de wetaca son retrasados y no ponen la info de algun
        # plato pues no lo escribo y ya esta, si no tiene info no puede estar bueno
        for c in courses:
            d = dict(c)
            try:
                writer.writerow(d)
            except ValueError as err:
                log.error('Error encontrado con el plato ' + d['Plato'] + '\n' + str(err))
