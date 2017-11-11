import radiotherm
import time
import datetime
from datetime import timezone

########################################
# 1st floor
IP1 = '192.168.0.111'
# 2ND floor
IP2 = '192.168.0.112'

max_samples_over_under_target = 8
minutes_in_period = 5
#########################################


def get_target_temp_cooling(tstat):
    now = datetime.datetime.now()
    #print('getting target temp ', tstatnum, now)
    #print(now.isoweekday())
    #print(now.hour)
    return 75


def get_target_temp_heating(tstat):
    now = datetime.datetime.now()
    #print('getting target temp ', tstatnum, now)
    #print(now.isoweekday())
    #print(now.hour)
    return 70


periods_under_target_1 = 0
periods_under_target_2 = 0
periods_over_target_1 = 0
periods_over_target_2 = 0

print('starting auto set temp')
print('max undertemp time (mins): ', (max_samples_over_under_target + 1) * minutes_in_period)
while True:
    try:
        tstat1 = radiotherm.get_thermostat(host_address=IP1)
        tstat2 = radiotherm.get_thermostat(host_address=IP2)

        while True:
            now = datetime.datetime.now(timezone.utc)

            target_cool_temp_1 = get_target_temp_cooling(tstat1)
            target_cool_temp_2 = get_target_temp_cooling(tstat2)
            target_heat_temp_1 = get_target_temp_heating(tstat1)
            target_heat_temp_2 = get_target_temp_heating(tstat2)

            if tstat1.tmode['human'] == 'Cool' and tstat1.t_cool['raw'] < target_cool_temp_1:
                if tstat1.t_cool['raw'] < (target_cool_temp_1 - 1):
                    tstat1.t_cool = target_cool_temp_1 - 1
                print(now, 'hvac 1 cooling set to less than ' + str(target_cool_temp_1) + 'for '
                      + str(periods_under_target_1 * minutes_in_period) + ' minutes')
                if periods_under_target_1 > max_samples_over_under_target:
                    print(now, 'setting hvac 1 cooling to target temp ' + str(target_cool_temp_1))
                    tstat1.t_cool = target_cool_temp_1
                    periods_under_target_1 = 0
                else:
                    periods_under_target_1 += 1
            elif tstat1.tmode['human'] == 'Heat' and tstat1.t_heat['raw'] > target_heat_temp_1:
                print(now, 'hvac 1 set to more than' + target_heat_temp_1 + 'for '
                      + str(periods_over_target_1 * minutes_in_period) + ' minutes')
                if periods_over_target_1 > max_samples_over_under_target:
                    print(now, 'setting hvac 1 heating to target temp ' + str(target_heat_temp_1))
                    tstat1.t_heat = target_heat_temp_1
                    periods_over_target_1 = 0
                else:
                    periods_over_target_1 += 1
            else:
                pass
                # print(now, 'ac 1 not set under 75')

            if tstat2.tmode['human'] == 'Cool' and tstat2.t_cool['raw'] < target_cool_temp_2:
                if tstat2.t_cool['raw'] < (target_cool_temp_2 - 1):
                    tstat2.t_cool = target_cool_temp_2 - 1
                print(now, 'hvac 2 cooling set to less than 75 for ' + str(periods_under_target_2 * minutes_in_period)
                      + ' minutes')
                if periods_under_target_2 > max_samples_over_under_target:
                    print(now, 'setting hvac 2 cooling to target temp ' + str(target_cool_temp_2))
                    tstat2.t_cool = target_cool_temp_2
                    periods_under_target_2 = 0
                else:
                    periods_under_target_2 += 1
            else:
                pass
                # print(now, 'ac 2 not set under 75')

            time.sleep(minutes_in_period * 60)
    except Exception as e:
        print('exception occurred', e)
        time.sleep(300)  # Delay for 5 minutes (300 seconds)