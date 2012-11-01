from sqlalchemy import Table, Column, create_engine, MetaData, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base, mapper

#from https://bitbucket.org/sqlalchemy/sqlalchemy/src/408388e5faf4/examples/declarative_reflection/declarative_reflection.py
from sqlalchemy.orm.util import _is_mapped_class
class DeclarativeReflectedBase(object):
    _mapper_args = []

    @classmethod
    def __mapper_cls__(cls, *args, **kw):
        """Declarative will use this function in lieu of 
        calling mapper() directly.
        
        Collect each series of arguments and invoke
        them when prepare() is called.
        """

        cls._mapper_args.append((args, kw))

    @classmethod
    def prepare(cls, engine):
        """Reflect all the tables and map !"""
        while cls._mapper_args:
            args, kw  = cls._mapper_args.pop()
            klass = args[0]
            # autoload Table, which is already
            # present in the metadata.  This
            # will fill in db-loaded columns
            # into the existing Table object.
            if args[1] is not None:
                table = args[1]
                Table(table.name, 
                    cls.metadata, 
                    extend_existing=True,
                    autoload_replace=False,
                    autoload=True, 
                    autoload_with=engine,
                    schema=table.schema)

            # see if we need 'inherits' in the
            # mapper args.  Declarative will have 
            # skipped this since mappings weren't
            # available yet.
            for c in klass.__bases__:
                if _is_mapped_class(c):
                    kw['inherits'] = c
                    break

            klass.__mapper__ = mapper(*args, **kw)

Base = declarative_base(cls=DeclarativeReflectedBase)


class Meter(Base):
    __tablename__ = 'Meter'
    Readings = relationship("Meter_Reading")
    Measured_Unit_ID = Column(Integer, ForeignKey('Units.Unit_ID'))


class Meter_Reading(Base):
    __tablename__ = 'Meter_Reading'


class Site(Base):
    __tablename__ = 'Site'
    Site_ID = Column(Integer, primary_key=True)


class Tree(Base):
    __tablename__ = 'Tree'
    Parent_Node_ID = Column(Integer, ForeignKey('Tree.Node_ID'))
    Node_ID = Column(Integer, primary_key=True)
    children = relationship("Tree", backref=backref('parent', remote_side=[Node_ID]))


class Units(Base):
    __tablename__ = u'Units'
    Unit_ID = Column(Integer, primary_key=True)

class Source(object):
    def __init__(self, config, echo=False):
        connection_string = "mssql+pyodbc://%s:%s@%s/%s" % (config.user, config.password, config.host, config.db)
        engine = create_engine(connection_string, echo=echo)
        Base.prepare(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        meta = MetaData()

    def meters(self):
        return self.session.query(Meter).all()

    def meter(self, Meter_ID):
        return self.session.query(Meter).get(Meter_ID)

    def root(self):
        return self.session.query(Tree).filter(Tree.Parent_Node_ID==0).one()

    def siteSearch(self, term):
        return self.session.query(Site).filter(Site.Name.contains(unicode(term))).all()

    def meterSearch(self, term):
        return self.session.query(Meter).filter(Meter.Description.contains(unicode(term))).all()

    def unit(self, Unit_ID):
        return self.session.query(Units).get(Unit_ID)

