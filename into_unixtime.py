import datetime
import time
from time import localtime

def into_unixtime(giventime):  #ex)2021.04.08.21:31:48
    y,m,d,t=giventime.split('.')
    h,min,sec=t.split(':')
    date_time = datetime.datetime(int(y),int(m),int(d),int(h),int(min),int(sec))
    return int(time.mktime(date_time.timetuple()))*1000

def into_datetime(unix):
    unix = int(unix)/1000
    unix_timestamp = int(unix)
    tm=localtime(unix_timestamp)
    return ''.join(str(tm.tm_year)+"."+str(tm.tm_mon)+"."+str(tm.tm_mday)+"."+str(tm.tm_hour)+":"+str(tm.tm_min)+":"+str(tm.tm_sec))

if __name__ == '__main__':
    unix=into_unixtime('2021.04.08.21:31:48')  #ex)2021.04.08.21:31:48
    print(unix)
    datetime=into_datetime('1617885108')
    print(datetime)