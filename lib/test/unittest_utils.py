import unittest
from pyEMIS.data import utils
from datetime import datetime, timedelta

class testTimeCalcs(unittest.TestCase):
    """A test class for the data utils module"""

    def setUp(self):
        self.test_data = [
            (datetime(1970,1,1,0,0,0,0,utils.tz), 0),
            (datetime(2012,7,5,16,53,50,0,utils.tz), 1341507230),
            (datetime(2004,9,16,23,59,58,0,utils.tz), 1095379198),
            (datetime(2004,9,16,23,59,59,0,utils.tz), 1095379199)
        ]


#2004-09-16T23:59:59.25	1095379199.25
#2004-09-16T23:59:59.50	1095379199.50
#2004-09-16T23:59:59.75	1095379199.75
#2004-09-17T00:00:00.00	1095379200.00
#2004-09-17T00:00:00.25	1095379200.25
#2004-09-17T00:00:00.50	1095379200.50
#2004-09-17T00:00:00.75	1095379200.75
#2004-09-17T00:00:01.00	1095379201.00
#2004-09-17T00:00:01.25	1095379201.25


    def test_ts_to_dt(self):
        for dt, ts in self.test_data:
            self.assertEqual(utils.timestamp_from_datetime(dt), ts)

    def test_dt_to_ts(self):
        for dt, ts in self.test_data:
            self.assertEqual(utils.datetime_from_timestamp(ts), dt)

    def testOneWay(self):
        for ts in xrange(0, 10000000, 60*60*24):
            dt = utils.datetime_from_timestamp(ts)
            ts2 = utils.timestamp_from_datetime(dt)
            if ts != ts2:
                print " -> ".join([str(ts), str(dt), str(ts2)])
            self.assertEqual(ts, ts2)

    def testTheOtherWay(self):
        td = timedelta(seconds=1)
        for dt in [datetime(1970,1,1,0,0,0,0,utils.tz) + td * i for i in xrange(0, 10000000, 60*60*24)]:
            ts = utils.timestamp_from_datetime(dt)
            dt2 = utils.datetime_from_timestamp(ts)
            
            if dt != dt2:
                print " -> ".join([str(dt), str(ts), str(dt2)])
            self.assertEqual(dt, dt2)

#        for dt, ts in self.test_data:
#            ts_from_dt = utils.timestamp_from_datetime(dt)
#            dt_from_ts = utils.datetime_from_timestamp(ts)
#            dt2 = utils.datetime_from_timestamp(ts_from_dt)
#            ts2 = utils.timestamp_from_datetime(dt_from_ts)
#            self.assertEqual(dt, dt2)
#            self.assertEqual(ts, ts2)
#            self.assertEqual(ts, ts_from_dt)
#            self.assertEqual(dt, dt_from_ts)

if __name__ == "__main__":
    unittest.main()
