class Shout:
    name = "shout"

    def transform(self, text):
        return text.upper() + "!"


plugin = Shout()
