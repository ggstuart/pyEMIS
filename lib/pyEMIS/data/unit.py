from . import DataError

class Unit(object):
    """coefficient represents the number to multiply by to get the base unit"""
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
            raise DataError("Units derived from %s and %s are incompatible." % (self.base_unit, unit.base_unit))
        return unit.from_base(self.to_base(value))

    def __repr__(self):
        return "%s (%s)" % (self.name, self.suffix)

    def __eq__(self, other):
        return self.base_unit == other.base_unit and self.coefficient == other.coefficient

    def __ne__(self, other):
        return not self.__eq__(other)


class BaseUnit(Unit):
    def __init__(self, name, suffix):
        super(BaseUnit, self).__init__(self, 1.0, name, suffix)

    def __eq__(self, other):
        return self.name == other.name and self.suffix == other.suffix

    def __ne__(self, other):
        return not self.__eq__(other)

M3 = BaseUnit('Cubic Metres', 'm3')
GJ = BaseUnit('GigaJoules', 'GJ')
kWh = Unit(GJ, 0.0036, 'kiloWatt hours', 'kWh')
C = BaseUnit('Celcius', 'C')
