class Reverse:
    name = "reverse"

    def transform(self, text):
        return text[::-1]


plugin = Reverse()
