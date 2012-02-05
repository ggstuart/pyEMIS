import logging
from MySQLdb import connect, cursors, Error
from .. import config

class Classic(object):
    # doctest: +ELLIPSIS
    """
    The classic database uses a config object so it needs a config file.
    >>> import os.path, pyEMIS.DataAccess as DA
    >>> config_path = os.path.expanduser('~/.EMIS/config.cfg')
    >>> src = DA.sources.Classic(config_path, "Classic")
    >>> src #doctest: +ELLIPSIS
    <pyEMIS.DataAccess.sources.classic.Classic object at ...>
    >>>
    """
    def __init__(self, config_file, database='Classic'):
        self._logger = logging.getLogger('DataSource:Classic')
        conf = config(config_file, database)
        try:
            self.conn = connect(host=conf.host(), user=conf.user(), passwd=conf.password(), db=conf.db())
            self.cursor = self.conn.cursor(cursors.DictCursor)
        except Error, e:
            if e.args[0] == 1045:
                self._logger.error('Invalid configuration for [%s] at %s' % (database, config_path))
                sys.exit(1)
            else:
                raise

    def _query(self, sql):
        self._logger.debug(sql)
        try:
            self.cursor.execute (sql)
            return self.cursor.fetchall ()
        except Error, e:
            if e.args[0] == 1054:
                self._logger.error("invalid sql")
                self._logger.error(e.args[1])
                self._logger.error(sql)
                sys.exit(1)
            else:
                raise

    def movement(self, meter_id):
        sql = "SELECT DISTINCT date_sql as date, movement FROM tbl_meter_data WHERE channel_id = %s AND date_sql > 0 ORDER BY date_sql" % str(meter_id)
        return self._query(sql)

    def integ(self, meter_id):
        sql = "SELECT DISTINCT date_sql as date, integ FROM tbl_meter_data WHERE channel_id = %s AND date_sql > 0 ORDER BY date_sql" % str(meter_id)
        return self._query(sql)

    def meters(self):
        sql = """
        SELECT ch.id, ch.name, t.channel_type as type
        FROM tbl_channels AS ch
        LEFT JOIN tbl_channel_types as t ON ch.channel_type_id = t.id
        """
        return self._query(sql)


    def __del__(self):
        self.conn.close


if __name__ == "__main__":
    import doctest
    doctest.testmod()
