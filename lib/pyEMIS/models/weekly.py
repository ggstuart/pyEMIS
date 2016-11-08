from .date_format import Factory as DFFactory

class Factory(DFFactory):
    def __init__(self, factory):
        super(Factory, self).__init__(factory, "%a %H:%M")
