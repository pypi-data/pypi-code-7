__author__ = 'yarnaid'

import json
import logging
import os
import numpy as np
import pyfftw
import copy
import mlpy.wavelet as wave
from smooth import smooth
import random

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)


def load_config():
    with open(os.path.join(current_dir, 'config.json')) as f:
        conf = json.load(f)
    return conf


def get_X_q(time_row):
    X_q = -np.log(1 - np.power((1 - conf['q']) ** 2, time_row.size - 2))
    X_q = -np.log(conf['q'])
    return X_q


def get_trend(data, power=0):
    '''
    get trend of given power of data
    '''
    polyfit = np.polyfit(data.time_var, data.values, power)
    fit = np.polyval(polyfit, data.time_var)
    return fit


def center_row(time_row):
    new_row = copy.deepcopy(time_row)
    trend = get_trend(time_row)
    new_row.values = time_row.values - trend
    return new_row


def get_ft_final(data_row):
    '''
    get FFT of centered data
    '''
    fft_res = pyfftw.n_byte_align_empty(data_row.values.size, conf['fftw_n'], conf['fftw_dtype'])
    fft_res[:] = data_row.values
    fft_res = pyfftw.interfaces.numpy_fft.fft(fft_res)
    res = copy.deepcopy(data_row)
    res.values = fft_res
    return res


def get_fft_freqs(data_row):
    res = np.fft.fftfreq(data_row.time_var.size, data_row.time_var[1] - data_row.time_var[0])
    return res


def get_fft_level(data_row, X_q=None):
    if X_q is None:
        X_q = get_X_q(data_row.time_var)
    res = data_row.values.var() * X_q / data_row.time_var.size
    return res


def get_acf(data_row):
    n = len(data_row.values)
    variance = data_row.values.var()
    x = data_row.values - data_row.values.mean()
    r = np.correlate(x, x, mode='full')[-n:]
    assert np.allclose(
        r, np.array([(x[:n - k] * x[-(n - k):]).sum() for k in range(n)]))
    res_acf = r / (variance * (np.arange(n, 0, -1)))
    res = copy.deepcopy(data_row)
    res.values = res_acf
    return res


def get_acf_level(data_row):
    n = len(data_row.values)
    std = data_row.values.std()
    mean = data_row.values.mean()
    sample_number = conf['acf_sample_number']
    samples_acf = []
    sample = copy.deepcopy(data_row)
    for i in xrange(sample_number):
        sample.values = np.random.normal(mean, std, n)
        sample_acf = get_acf(sample)
        samples_acf.append(sample_acf.values)
    samples_acf = np.asarray(samples_acf)
    mean_level = samples_acf.mean(axis=0)
    std_level = samples_acf.std(axis=0)
    return {'mean': mean_level, 'std': std_level}


def get_scalogram_scales(data_row):
    dt = data_row.time_var[1] - data_row.time_var[0]
    scales = wave.autoscales(N=data_row.values.size, dt=dt, dj=conf['wavelet_step'], wf=conf['wavelet'], p=conf['morlet_param'])
    return scales


def get_scalogram(data_row):
    dt = data_row.time_var[1] - data_row.time_var[0]
    # Compute scales as fractional power of two
    scales = wave.autoscales(N=data_row.values.size, dt=dt, dj=conf['wavelet_step'], wf=conf['wavelet'], p=conf['morlet_param'])
    cwt = wave.cwt(data_row.values, dt, scales, conf['wavelet'], conf['morlet_param'])
    scalogr = np.abs(cwt)
    # scalogr = scalogr ** 2
    return scalogr


def get_scalogram_final(data_row):
    scalogr = get_scalogram(data_row)
    mean, std = get_scalogram_level(data_row).values()
    scalogr = scalogr / mean
    logging.warning('Generating gaussian errors for normal scalogram')
    errors = np.abs(np.random.normal(scalogr.mean(), scalogr.std(), scalogr.shape)) * conf['scalogram_noise_level']  # emulate errors
    errors[errors < 1] = 1
    scalogr = scalogr / errors
    return scalogr, errors.mean()



def get_sf(data_row):
    res = copy.deepcopy(data_row)
    n = len(data_row.values)
    sf = np.zeros(n)
    for tau in xrange(n):
        rolled_data = data_row.values[tau::]
        sf_value = ((data_row.values[:n - tau:] - rolled_data) ** 2).mean()
        sf[tau] = (sf_value)
    res.values = sf
    return res


def get_scalogram_level(data_row):
    samples_number = conf['scalogram_samples_number']
    mean = data_row.values.mean()
    std = data_row.values.std()
    n = len(data_row.values)
    samples = []
    data_sample = copy.deepcopy(data_row)
    for i in xrange(samples_number):
        norm_sample = np.random.normal(mean, std, n)
        data_sample.values = norm_sample
        sample_scalo = get_scalogram(data_sample)
        samples.append(sample_scalo)
    samples = np.asarray(samples)
    mean_levels = samples.mean(axis=0)
    std_levels = samples.std(axis=0)
    return {
        'mean': mean_levels,
        'std':std_levels
    }


def get_sf_level(data_row):
    residuals = make_residual_bank(data_row)

    model_curves = []
    for i in xrange(conf['sf_random_models']):
        model_curve = get_model_curve(data_row)
        for j in xrange(len(model_curve)):
            model_curve[j] += random.choice(residuals)
        model_curves.append(model_curve)

    samples_sf = []
    sample_sf = copy.deepcopy(data_row)
    for curve in model_curves:
        sample_sf.values = curve
        samples_sf.append(get_sf(sample_sf).values)

    samples_sf = np.asarray(samples_sf)
    mean_level = samples_sf.mean(axis=0)
    std_level = samples_sf.std(axis=0)
    return {
        'mean': mean_level,
        'std':std_level
    }


def make_residual_bank(data_row, window_len=None):
    data_storage = get_bank_seq(db_path=data_row)
    residuals = []
    
    if window_len is None:
        window_len = min(conf['sf_models_smooth_window'], len(data_storage[0]) / 2.)
    
    for i in xrange(len(data_storage)):
        smoothed = smooth(data_storage[i], window_len=window_len)
        residuals.extend(data_storage[i] - smoothed[:data_storage[i].shape[0]])
    return np.asarray(residuals)


def get_model_curve(data):
    logging.warning('[WARNING!!!]: RANDOM CURVE MODEL USING')
    res = np.random.random_sample(len(data.values))
    return res * data.values.max()


def get_bank_seq(db_path):
    logging.warning('[WARNING!!!]: ' + str(conf['sf_bank_samples']) + ' RANDOM BANK USING')
    res = [get_model_curve(db_path) for i in xrange(conf['sf_bank_samples'])]
    return res


conf = load_config()
logging.basicConfig(level=logging.DEBUG, format=conf['LOG_FORMAT'])
