# -*- coding: utf-8 -*-

import re
import urllib3
import csv

from bs4 import BeautifulSoup


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
    soup = BeautifulSoup(webContent)

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

    sortedCourses = sorted(courses, key=lambda tup: tup[0])

    with open('wetaca-weekly.csv', 'w', encoding='utf8') as temp:
        fieldnames = dict(courses[0]).keys()
        writer = csv.DictWriter(temp, fieldnames=fieldnames)
        writer.writeheader()

        for c in courses:
            d = dict(c)
            writer.writerow(d)
