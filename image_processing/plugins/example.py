from plugin import Plugin


class Example(Plugin):

    def __init__(self):
        super().__init__()

    def vegetation_from_file(self, src):
        return 0.5 
