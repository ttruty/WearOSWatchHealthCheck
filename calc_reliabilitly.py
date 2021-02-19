"""
Function:
calc_reliability(timeArr, unit, plot=0)
: Calculate the reliability of time series data from sensor.
Requirement:
package: python(either python2.x or python 3.x), pandas, numpy, matplotlib
The time must be unixtimestamp in milliseconds.
Development log:
1. function and script name the same - done
2. options for second, minute, hour - done
3. modification: more comments - done
4. (add y label in figure. - no figure saving) plot or not, to add one param y - done
5. non-idle -> hasData - done
6. add plot switch: reliability_calc(timeArr, unit, plot=0) - done
7. another script named 'save_reliability.py' - done
8. fixed calc_reliability() plot function x label display bug (done)- may31 2020 shibo
"""

from __future__ import division
import os
import sys
import numpy as np
import pandas as pd
import plotly

pd.options.plotting.backend = "plotly"


def calc_reliability(timeArr, unit='second', outfolder='', plot=0):
    """
    Calculate the reliability of time series sensor data in each 'unit' from the start of the 'timeArr' to the end.
    Plot is optional.
    Note that the returned dataframe time column is unixtime in second unit (10 digits).

    Requirement: timeArr must be unixtimestamp in milliseconds.

    :param timeArr: time array of unixtimestamp in milliseconds, size N*1
    :param unit: str, options: "second", "minute", "hour"
    :param plot: 0 or 1
    :return countDf: reliability result dataframe with columns 'Time' and 'SampleCounts'.

    """

    # ==================================================================================
    # generate the reliability dataframe
    # ==================================================================================
    msecCnts = {
        "second": 1000,
        "minute": 60000,
        "hour": 3600000,
    }

    timeNoDuplicateArr = np.unique(timeArr)
    timeNoDuplicateArr = np.floor_divide(timeNoDuplicateArr, msecCnts[unit]).astype(int)
    timeNoDuplicateArr = np.sort(timeNoDuplicateArr)

    reliabilityTimeList = []
    reliabilitySampleCountsList = []
    interpolated = []
    count = 0

    # loop through the timeNoDuplicateArr
    for i in range(len(timeNoDuplicateArr) - 1):
        # if next timestamp is the same as current one
        if timeNoDuplicateArr[i + 1] == timeNoDuplicateArr[i]:
            count += 1
        else:
            temp_time_list = int(timeNoDuplicateArr[i])
            reliabilityTimeList.append(int(timeNoDuplicateArr[i]))
            # count+1 instead of count because it's looking at the next second
            reliabilitySampleCountsList.append(count + 1)
            interpolated.append(0)

            count = 0
            # if the data have a gap, which means unit(s) with no data exist(s)
            for time in range(timeNoDuplicateArr[i] + 1, timeNoDuplicateArr[i + 1]):
                reliabilityTimeList.append(int(time))
                # append 0 to noData seconds
                reliabilitySampleCountsList.append(0)
                interpolated.append(1)

    # With try-except, no need to check the input and the empty countDf will be returned.
    # Advantage: In batch processing, when empty data files with only header exist,
    #  the reliability files will follow the same pattern.
    try:
        reliabilityTimeList.append(int(timeNoDuplicateArr[-1]))
        reliabilitySampleCountsList.append(count + 1)
        interpolated.append(0)
    except:
        print('Warning: timeArr is empty!')

    countDf = pd.DataFrame({'Time': reliabilityTimeList, 'SampleCounts': reliabilitySampleCountsList, 'Interpolated': interpolated}, \
                           columns=['Time', 'SampleCounts', 'Interpolated'])

    # ==================================================================================
    # plot figure
    # ==================================================================================
    if plot:
        countDf['Time'] = pd.to_datetime(countDf['Time'], unit=unit[0], utc=True)  # unit is 's'/'m'/'h'
        countDf = countDf.set_index(['Time'])
        # countDf.index = countDf.index.tz_convert('US/Central')

        #f = plt.figure(figsize=(12, 5))
        fig = countDf.plot(title="Reliability scores")
        #plt.title('Reliability Test')
        #plt.ylabel('Count Per Unit')
        fig.show()
        # plt.savefig(os.path.join(outfolder, 'reliability(frequency).png')) # FYI, save fig function

    return countDf