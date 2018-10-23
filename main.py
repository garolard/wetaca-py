import re


def compileRegex(pattern):
    return re.compile(pattern, re.IGNORECASE)


def testSomeRegex(regex, text):
    cre = compileRegex(regex)
    match = cre.findall(text)
    for m in match:
        print(m)


if __name__ == '__main__':
    text = 'Habia una vez un cabron que vendia un huevo a 432,50 € el kilo'
    testSomeRegex(r'\d+,?\d+?\s?€', text)
