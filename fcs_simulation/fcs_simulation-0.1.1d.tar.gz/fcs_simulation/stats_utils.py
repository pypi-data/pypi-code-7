import numpy as np

def PDF_to_events(PDF_time_series, times, totalEvents=None, eventDensity=None):
    if totalEvents==None:
        totalEvents = int((times[-1]-times[0])*eventDensity)
    print totalEvents
    if type(PDF_time_series)==list:
        PDF_time_series = np.array(PDF_time_series)
    if type(times)==list:
        times = np.array(times)

    CDF_time_series = np.zeros(PDF_time_series.shape)
    delta_t_ = lambda i: times[i]-times[i-1]
    for i in range(1, len(PDF_time_series)):
        CDF_time_series[i] = delta_t_(i)*( PDF_time_series[i]+PDF_time_series[i-1] ) + CDF_time_series[i-1]
#    return CDF_time_series
    # events in CDF space
    events = np.sort(np.random.rand(totalEvents)*CDF_time_series[-1])
    progression = 0 # will iterate through events mapping back to time space
    for i in range(1, len(PDF_time_series)):
        while progression < totalEvents and events[progression] < CDF_time_series[i]:
#            import pdb; pdb.set_trace()
            events[progression] = (events[progression]-CDF_time_series[i-1])*delta_t_(i)/(CDF_time_series[i]-CDF_time_series[i-1]) + times[i-1]
            progression = progression + 1
    return events
