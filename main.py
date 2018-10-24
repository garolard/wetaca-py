import io
import re
import urllib3


http = urllib3.PoolManager()


def getUrlContent(url):
    return http.request('GET', url).data.decode('UTF-8')


# La regex de este metodo pilla todas las lineas del estilo 're: este texto'
def parseRegexFromFile(path):
    with io.open(path, 'r', encoding='utf8') as f:
        content = f.read()
        r = re.compile(r're:\s{1}([^\s].*)', re.IGNORECASE)
        return r.findall(content)


def applyRegex(regex, content):
    cr = re.compile(regex, re.IGNORECASE)
    founded = cr.findall(content)
    return [t[2] for t in founded]


if __name__ == '__main__':
    validRegex = parseRegexFromFile('res.txt')
    content = getUrlContent('https://wetaca.com/175-crema-de-setas.html')
    results = [applyRegex(r, content) for r in validRegex]

    print(results)
