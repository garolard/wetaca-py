class ResReader():
    __content = None

    def get_resources(self):
        if not self.__content:
            with open('res.txt', 'r', encoding='utf8') as f:
                self.__content = f.read()

        return self.__content
