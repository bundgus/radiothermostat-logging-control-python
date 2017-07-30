import radiotherm
import datetime
import time
import datetime
from datetime import timezone

# 1st floor
IP1 = '192.168.0.111'
# 2ND floor
IP2 = '192.168.0.112'

target_temp_1 = 75
target_temp_2 = 75
periods_under_target_1 = 0
periods_under_target_2 = 0

while True:
    try:
        tstat1 = radiotherm.get_thermostat(host_address=IP1)
        tstat2 = radiotherm.get_thermostat(host_address=IP2)

        while True:
            now = datetime.datetime.now(timezone.utc)

            if tstat1.tmode['human'] == 'Cool' and tstat1.t_cool['raw'] < 75:
                # print(now, 'hvac 1 set to less than 75 for ' + str(periods_under_target_1) + ' periods')
                if periods_under_target_1 > 1:
                    print(now, 'setting hvac 1 to target temp ' + str(target_temp_1))
                    tstat1.t_cool = target_temp_1
                    periods_under_target_1 = 0
                else:
                    periods_under_target_1 += 1
            else:
                pass
                # print(now, 'ac 1 not set under 75')

            if tstat2.tmode['human'] == 'Cool' and tstat2.t_cool['raw'] < 75:
                # print(now, 'hvac 2 set to less than 75 for ' + str(periods_under_target_2) + ' periods')
                if periods_under_target_2 > 1:
                    print(now, 'setting hvac 2 to target temp ' + str(target_temp_2))
                    tstat2.t_cool = target_temp_2
                    periods_under_target_2 = 0
                else:
                    periods_under_target_2 += 1
            else:
                pass
                # print(now, 'ac 2 not set under 75')

            time.sleep(1200)  # Delay for 20 minutes (1200 seconds)
    except Exception as e:
        print('exception occurred', e)
        time.sleep(300)  # Delay for 5 minutes (300 seconds)