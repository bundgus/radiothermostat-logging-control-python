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


def tstat_read(tstat):
    reading = {'temp': {tstat.temp['raw']},
               't_heat': tstat.t_heat['raw'],
               't_cool': tstat.t_cool['raw'],
               'tmode': tstat.tmode['human'],
               'tstate': tstat.tstate['human'],
               }
    return reading


def get_target_temp_cooling(tstat_reading, story=None):
    if tstat_reading or story:
        pass
    # for now always default to 75
    return 75.0


def get_target_temp_heating(tstat_reading, story=None):
    target_now = datetime.datetime.now().time()
    four_thirty_am = datetime.time(hour=4, minute=30)
    seven_am = datetime.time(hour=7)
    ten_pm = datetime.time(hour=22)

    if story is 1:
        # between 5 am and 7 am turn up the heat to 72 downstairs
        if four_thirty_am <= target_now < seven_am:
            return 72.0
        # between 7 am and 10 pm moderate the heat to 70 downstairs
        elif seven_am <= target_now < ten_pm:
            return 70.0
        # other times adjust the heat to 68 to avoid overheating upstairs
        else:
            return 68.0
    # upstairs always has the heat turned down
    else:
        return 62.0


periods_under_target_1 = 0
periods_under_target_2 = 0
periods_over_target_1 = 0
periods_over_target_2 = 0

print('starting auto set temp')
print('max manual override time (mins): ', (max_samples_over_under_target + 1) * minutes_in_period)
while True:
    try:
        tstat1 = radiotherm.get_thermostat(host_address=IP1)
        tstat2 = radiotherm.get_thermostat(host_address=IP2)

        while True:
            tstat1_reading = tstat_read(tstat1)
            tstat2_reading = tstat_read(tstat2)

            now = datetime.datetime.now(timezone.utc)

            target_cool_temp_1 = get_target_temp_cooling(tstat1_reading, story=1)
            target_cool_temp_2 = get_target_temp_cooling(tstat2_reading, story=2)
            target_heat_temp_1 = get_target_temp_heating(tstat1_reading, story=1)
            target_heat_temp_2 = get_target_temp_heating(tstat2_reading, story=2)

            if tstat1_reading['tmode'] == 'Cool' and tstat1_reading['t_cool'] < target_cool_temp_1:
                if tstat1_reading['t_cool'] < (target_cool_temp_1 - 1):
                    tstat1.t_cool = target_cool_temp_1 - 1
                print(now, 'ac 1 cooling set to less than ' + str(target_cool_temp_1) + ' for '
                      + str(periods_under_target_1 * minutes_in_period) + ' minutes')
                if periods_under_target_1 > max_samples_over_under_target:
                    print(now, 'setting ac 1 cooling to target temp ' + str(target_cool_temp_1))
                    tstat1.t_cool = target_cool_temp_1
                    periods_under_target_1 = 0
                else:
                    periods_under_target_1 += 1
            elif tstat1_reading['tmode'] == 'Heat' and tstat1_reading['t_heat'] != target_heat_temp_1:
                print(now, 'heat 1 set to ' + str(tstat1_reading['t_heat']) + ' instead of ' + str(target_heat_temp_1)
                      + ' for ' + str(periods_over_target_1 * minutes_in_period) + ' minutes')
                if periods_over_target_1 > max_samples_over_under_target:
                    print(now, 'setting heat 1 heating to target temp ' + str(target_heat_temp_1))
                    tstat1.t_heat = target_heat_temp_1
                    periods_over_target_1 = 0
                else:
                    periods_over_target_1 += 1
            else:
                pass
                # print(now, 'ac 1 not set under 75')

            if tstat2_reading['tmode'] == 'Cool' and tstat2_reading['t_cool'] < target_cool_temp_2:
                if tstat2_reading['t_cool'] < (target_cool_temp_2 - 1):
                    tstat2.t_cool = target_cool_temp_2 - 1
                print(now, 'ac 2 cooling set to less than 75 for ' + str(periods_under_target_2 * minutes_in_period)
                      + ' minutes')
                if periods_under_target_2 > max_samples_over_under_target:
                    print(now, 'setting ac 2 cooling to target temp ' + str(target_cool_temp_2))
                    tstat2.t_cool = target_cool_temp_2
                    periods_under_target_2 = 0
                else:
                    periods_under_target_2 += 1
            elif tstat2_reading['tmode'] == 'Heat' and tstat2_reading['t_heat'] != target_heat_temp_2:
                print(now, 'heat 2 set to ' + str(tstat2_reading['t_heat']) + ' instead of ' + str(target_heat_temp_2)
                      + ' for ' + str(periods_over_target_2 * minutes_in_period) + ' minutes')
                if periods_over_target_2 > max_samples_over_under_target:
                    print(now, 'setting heat 2 heating to target temp ' + str(target_heat_temp_2))
                    tstat2.t_heat = target_heat_temp_2
                    periods_over_target_2 = 0
                else:
                    periods_over_target_2 += 1
            else:
                pass
                # print(now, 'ac 2 not set under 75')

            time.sleep(minutes_in_period * 60)
    except Exception as e:
        print('exception occurred', e)
        time.sleep(300)  # Delay for 5 minutes (300 seconds)
