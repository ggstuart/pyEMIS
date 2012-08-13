class Unit(object):
    def __init__(self, base_unit, coefficient, name, suffix):
        self.name = name
        self.suffix = suffix
        self.base_unit = base_unit
        self.coefficient = float(coefficient)

    def to_base(self, value):   
        return value * self.coefficient

    def from_base(self, value):
        return value / self.coefficient

    def to_unit(self, value, unit):
        if unit.base_unit != self.base_unit:
            raise TypeError, "Units derived from %s and %s are incompatible." % (self.base_unit, unit.base_unit)
        return unit.from_base(self.to_base(value))

    def __repr__(self):
        return "%s (%s)" % (self.name, self.suffix)
        
        
class BaseUnit(Unit):
    def __init__(self, name, suffix):
        super(BaseUnit, self).__init__(self, 1.0, name, suffix)
