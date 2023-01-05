import urllib.request
from datetime import datetime, timedelta
import into_unixtime as unix

#--------------------------
# UTC -> KST(한국시간) 변경
#--------------------------
def convert_kst(utc_string):
	# datetime 값으로 변환
	dt_tm_utc = datetime.strptime(utc_string,'%Y.%m.%d.%H:%M:%S')
	
	# +9 시간
	tm_kst = dt_tm_utc + timedelta(hours=9)
	
	# 일자 + 시간 문자열로 변환
	str_datetime = tm_kst.strftime('%Y.%m.%d.%H:%M:%S')
	
	return str_datetime

def get_server_time():
    month = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', \
    'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
    url = 'https://api.coinone.co.kr/public/v2/currencies/'
    date = urllib.request.urlopen(url).headers['Date'][5:-4]
    d, m, y, hour, min, sec = date[:2], month[date[3:6]], date[7:11], date[12:14], date[15:17], date[18:]

    formular = y + '.' + m + '.' + d + '.' + hour + ':' + min + ':' + sec
    return formular




