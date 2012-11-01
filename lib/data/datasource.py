#Commodity should be mapped to a master list somewhere?

COMMODITIES = [
    'electricity',
    'electricity (reactive)',
    'gas',
    'temperature',
    'unknown',
    'water',
]

class DataSourceError(Exception): pass

class Node(object):
    def __init__(self, label, parent=None, type_='Node'):
        if parent:
            self.parent = parent
            self.parent.children.append(self)
        self.label = label
        self.type_ = type_
        self.children = []

    def __str__(self):
        return "%s (%s)" % (self.label, self.type_)

class Organisation(Node):
    def __init__(self, label):
        super(Organisation, self).__init__(label, type_='Oganisation')

class Building(Node):
    def __init__(self, label, organisation):
        super(Building, self).__init__(label, parent=organisation, type_='Building')
        self.organisation = self.parent
        self.datasources = []
        self.meters = self.datasources

class DataSource(object):
    """Stores meta-data about the sensor, meter or simulation that generated a dataset"""
    def __init__(self, label, commodity, node=None):
        """
        Label should be a string that describes the data source
        """
        if commodity.lower() not in COMMODITIES:
            raise DataSourceError("Unknown commodity: %s (must be one of %s)" % (commodity.lower(), COMMODITIES))
        if node:
            self.node = node
            node.datasources.append(self)
        self.commodity = commodity.title()
        self.label = label

class Meter(DataSource):
    def __init__(self, label, commodity, building): 
        super(Meter, self).__init__(label, commodity, node=building)
        self.building = self.node
        
if __name__ == "__main__":

#    home = Node('Home')

    DMU = Organisation('DMU')#, parent=home)
    LCC = Organisation('LCC')#, parent=home)

    CC = Building('Campus Centre', DMU)
    KMB = Building('Kimberlin Library', DMU)
    NW = Building('New Walk', LCC)
    JMCC = Building('Judgemeadow Community College', LCC)

    shop = Node('Shop', parent=CC)
    pub = Node('Pub', parent=CC)
    office = Node('Office', parent=CC)

    NWA = Node('A block', parent=NW)
    NWB = Node('B block', parent=NW)
    
    JMElec = DataSource('JMCC electricity', 'energY', node=JMCC)
    JMGas = DataSource('JMCC gas', 'eNergY', node=JMCC)
    NWAGas = DataSource('NWA Gas', 'enerGY', node=NWA)
    PubElec = DataSource('Pub electricity', 'enerGY', node=pub)


    def print_node(node, tabs=1):
        print "|%s%s" % (" -" * tabs, node)
        new_tabs = tabs + 1
        for datasource in node.datasources:
            print "|%s%s" % (" ~" * new_tabs, datasource.label)
        for child in node.children:
            print_node(child, tabs=new_tabs)


    print "|"
    print_node(LCC)
    print_node(DMU)
    print "|"
