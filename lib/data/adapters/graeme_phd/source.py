from sqlalchemy import Column, Integer, Sequence, ForeignKey, String, Float, CHAR, DateTime, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Channel(Base):
    __tablename__ = 'tbl_channels'
    id = Column(Integer, Sequence('channel_seq'), primary_key=True)
    name = Column(String(30), nullable=False)
    site_id = Column(Integer, ForeignKey('tbl_sites.id'), nullable=False)
    channel_unit_id = Column(Integer, ForeignKey('tbl_channel_units.id'), nullable=False)
    unit_id = Column(Integer, ForeignKey('tbl_units.id'), nullable=False)
    channel_type_id = Column(Integer, ForeignKey('tbl_channel_types.id'), nullable=True)
    KEYNAME = Column(String(12), nullable=False)
    AREA = Column(String(27), nullable=False)
    SITE = Column(String(27), nullable=False)
    ENTYPE = Column(CHAR(2), nullable=False)
    UNITS = Column(String(7), nullable=False)
    VIRTUAL = Column(CHAR(1), nullable=False)
    SERV_DESC = Column(String(20), nullable=False)
    MANMETER = Column(String(12), nullable=False)

    site = relationship("Site")
    channel_unit = relationship("ChannelUnit")
    type = relationship("ChannelUnit")
    data = relationship("MeterData", order_by="MeterData.date_sql")

"""
  KEY `site_id` (`site_id`)
"""

class ChannelType(Base):
    __tablename__ = 'tbl_channel_types'
    id = Column(Integer, Sequence('channel_type_seq'), primary_key=True)
    channel_type = Column(String(25), nullable=False)
    unit_id = Column(Integer, ForeignKey('tbl_units.id'), nullable=False)
"""
  KEY `unit_id` (`unit_id`)
"""


"""
CREATE TABLE IF NOT EXISTS `tbl_channel_type_to_serv_desc_map` (
  `SERV_DESC` varchar(20) default NULL,
  `channel_type_id` int(11) unsigned NOT NULL default '0'
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
"""

class ChannelUnit(Base):
    __tablename__ = 'tbl_channel_units'
    id = Column(Integer, Sequence('channel_units_seq'), primary_key=True)
    UNITS = Column(String(7), nullable=False)
    unit_id = Column(Integer, ForeignKey('tbl_units.id'), nullable=True)
    multiplier = Column(Float, nullable=False)
    unit = relationship("Unit")
"""
  KEY `unit_id` (`unit_id`)
"""

class MeterData(Base):
    __tablename__ = 'tbl_meter_data'
    channel_id = Column(Integer, ForeignKey('tbl_channels.id'), nullable=False, primary_key=True)
#    keyname = Column(String(18), nullable=False)
    date_sql = Column(DateTime, nullable=False, primary_key=True)
    integ = Column(String(30), nullable=False)
    movement = Column(String(20), nullable=False)
"""
  KEY `channel_id_date_sql` (`channel_id`,`date_sql`)
"""

class Site(Base):
    __tablename__ = 'tbl_sites'
    id = Column(Integer, Sequence('site_seq'), primary_key=True)
    Site = Column(String(255), nullable=False)
"""
  `Dynamat SITE` varchar(27) NOT NULL default '',
"""

"""
CREATE TABLE IF NOT EXISTS `tbl_site_groups` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

CREATE TABLE IF NOT EXISTS `tbl_site_group_membership` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `site_group_id` int(10) unsigned NOT NULL default '0',
  `site_id` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `unique_membership` (`site_group_id`,`site_id`),
  KEY `site_group_index` (`site_group_id`),
  KEY `member_index` (`site_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=322 ;

CREATE TABLE IF NOT EXISTS `tbl_site_types` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=7 ;
"""


class Unit(Base):
    __tablename__ = 'tbl_units'
    id = Column(Integer, Sequence('unit_seq'), primary_key=True)
    name = Column(String(30), nullable=False)
    suffix = Column(String(10), nullable=False)
    channel_type_id = Column(Integer, ForeignKey('tbl_channel_types.id'), nullable=False)


class UnitConversion(Base):
    __tablename__ = 'tbl_unit_conversions'
    id = Column(Integer, Sequence('unit_conversion_seq'), primary_key=True)
    from_unit_id = Column(Integer, ForeignKey('tbl_units.id'), nullable=False)
    to_unit_id = Column(Integer, ForeignKey('tbl_units.id'), nullable=False)
    coefficient = Column(Float, nullable=False)
"""
  KEY `from_unit_id` (`from_unit_id`,`to_unit_id`)
"""


class Source(object):
    def __init__(self, config, echo=False, sscursor=True):
        connection_string = "mysql://%s:%s@%s/%s" % (config.user, config.password, config.host, config.db)
        if sscursor:
            from MySQLdb.cursors import SSCursor
            engine = create_engine(connection_string, connect_args={'cursorclass': SSCursor}, echo=echo)
        else:
            engine = create_engine(connection_string, echo=echo)
        Session = sessionmaker(bind=engine)
        self.session = Session()

#        meta = MetaData(engine, reflect=True)
#        conn = engine.connect()
#        rs = s.execution_options(stream_results=True).execute()
#        result = connection.execution_options(stream_results=True).execute(stmt)

    def channels(self):
        return self.session.query(Channel).all()

    def channel(self, meter_id):
        return self.session.query(Channel).get(meter_id)

    def siteSearch(self, term):
        return self.session.query(Site).filter(Site.Site.contains(unicode(term))).all()

    def channelSearch(self, term):
        return self.session.query(Channel).filter(Channel.name.contains(unicode(term))).all()

    def unit(self, unit_id):
        return self.session.query(Unit).get(unit_id)

    def data(self, channel_id, yield_per=2000):
        return self.session.query(MeterData).filter(MeterData.channel_id == channel_id).order_by(MeterData.date_sql).yield_per(yield_per)
