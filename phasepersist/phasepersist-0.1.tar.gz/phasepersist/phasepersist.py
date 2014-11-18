# -*- coding: utf-8 -*-
import pickle

def save(data, filename='mypersist.pkl', prefix = 'en'):
	filename = prefix + filename
	output = open(filename, 'wb')
	pickle.dump(data, output)
	output.close()

def load(filename='mypersist.pkl', prefix = 'en'):
	filename = prefix + filename
	pkl_file = open(filename, 'rb')
	data = pickle.load(pkl_file)
	return data
