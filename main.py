# -*- coding: utf-8 -*-

import io
import re
import urllib3

from res_reader import ResReader


http = urllib3.PoolManager()
findValidRegex = 're:\s{1}([^\s].*)'
findNameRegex = 'np:\s{1}([^\s].*)'
findLinkRegex = 'a data-item.*?href=\"(.*?)\"'
reader = ResReader()


def getUrlContent(url):
    return http.request('GET', url).data.decode('UTF-8')


def parseRegexFromFile():
    r = re.compile(findValidRegex, re.IGNORECASE)
    return r.search(reader.get_resources()).group(1)


def applyRegex(regex, content):
    cr = re.compile(regex, re.IGNORECASE)
    founded = cr.findall(content)
    values = {}
    for t in founded:
        values.update({t[1]: t[5]})
    return values


def captureCourseName(urlContent):
    courseNameRegexMatch = re.compile(findNameRegex, re.IGNORECASE).search(reader.get_resources())
    if courseNameRegexMatch:
        courseNameRegex = courseNameRegexMatch.group(1)
    r = re.compile(courseNameRegex, re.IGNORECASE)
    match = r.search(urlContent)
    if match:
        return match.group(1)
    return '{{Nombre desconocido}}'


def captureCourseLinks(content):
    r = re.compile(findLinkRegex, re.IGNORECASE)
    return r.findall(content)


def captureCourseInfo(courseUrl):
    validRegex = parseRegexFromFile()
    content = getUrlContent(courseUrl)
    courseName = captureCourseName(content)
    results = applyRegex(validRegex, content)

    results.update({'name': courseName})

    return results


if __name__ == '__main__':
    wetacaMenuContent = getUrlContent('https://wetaca.com/27-nuestros-platos')
    courseLinks = captureCourseLinks(wetacaMenuContent)

    courses = []
    for link in courseLinks:
        courses.append(captureCourseInfo(link))

    for c in courses:
        for k, v in c.items():
            print(k + ": " + v)
