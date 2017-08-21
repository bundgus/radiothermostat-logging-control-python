import radiotherm
import time
import datetime
from datetime import timezone

########################################
# 1st floor
IP1 = '192.168.0.111'
# 2ND floor
IP2 = '192.168.0.112'

max_samples_under_target = 8
seconds_in_period = 300  # 5 minutes (600 seconds)
#########################################

def get_target_temp(tstat):
    now = datetime.datetime.now()
    #print('getting target temp ', tstatnum, now)
    #print(now.isoweekday())
    #print(now.hour)
    return 75

periods_under_target_1 = 0
periods_under_target_2 = 0

print('starting auto set temp')
print('max undertemp time (mins): ', (max_samples_under_target+1)*seconds_in_period/60)
while True:
    try:
        tstat1 = radiotherm.get_thermostat(host_address=IP1)
        tstat2 = radiotherm.get_thermostat(host_address=IP2)

        while True:
            now = datetime.datetime.now(timezone.utc)

            target_temp_1 = get_target_temp(tstat1)
            if tstat1.tmode['human'] == 'Cool' and tstat1.t_cool['raw'] < target_temp_1:
                print(now, 'hvac 1 set to less than 75 for ' + str(periods_under_target_1 * seconds_in_period / 60)
                      + ' minutes')
                if periods_under_target_1 > max_samples_under_target:
                    print(now, 'setting hvac 1 to target temp ' + str(target_temp_1))
                    tstat1.t_cool = target_temp_1
                    periods_under_target_1 = 0
                else:
                    periods_under_target_1 += 1
            else:
                pass
                # print(now, 'ac 1 not set under 75')

            target_temp_2 = get_target_temp(2)
            if tstat2.tmode['human'] == 'Cool' and tstat2.t_cool['raw'] < target_temp_2:
                print(now, 'hvac 2 set to less than 75 for ' + str(periods_under_target_2 * seconds_in_period / 60)
                      + ' minutes')
                if periods_under_target_2 > max_samples_under_target:
                    print(now, 'setting hvac 2 to target temp ' + str(target_temp_2))
                    tstat2.t_cool = target_temp_2
                    periods_under_target_2 = 0
                else:
                    periods_under_target_2 += 1
            else:
                pass
                # print(now, 'ac 2 not set under 75')

            time.sleep(seconds_in_period)
    except Exception as e:
        print('exception occurred', e)
        time.sleep(300)  # Delay for 5 minutes (300 seconds)