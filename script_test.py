#스크립트 테스트
import CoinoneAPI_config
import into_unixtime as unix
import server_time as stime
from CoinoneAPI_GET import GET
from CoinoneAPI_POST import POST
import time

get = GET()
post = POST()

def ust():
    return unix.into_unixtime(stime.convert_kst(stime.get_server_time()))

print(unix.into_datetime(1672823460000))
print(unix.into_datetime(1672823490000))

while True:
    if ust()%60000 == 0:
        print("지금 서버시간은!!", ust())
        print(get.get_chart(target_currency='XRP'))







