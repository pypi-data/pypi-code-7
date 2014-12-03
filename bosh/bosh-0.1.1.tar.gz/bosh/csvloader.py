'''
Created on Sep 9, 2014

@author: eugene
'''
import sys
from bosrv.request import connect
from exc.ttypes import *
import traceback
import sys

def dequote(s):
    if (s[0] == s[-1]) and s[0] == '\"':
	s = replaceSingleQuote(s)
        return "\'" + s[1:-1].replace("\",\"" , "\',\'") + "\'"
    return s

def addSingleQuote(s):
	s = replaceSingleQuote(s)
	return "\'" + s.replace("," , "\',\'") + "\'"

def replaceSingleQuote(s):
	return s.replace("'","%27")

def csvload(host, port,token_str, csv_file, bt_name ,insert_line=30000 ):
	errorfile = open('errorinsert.txt', 'w')

	addr_info= "bo://:" + token_str + "@" + host + ":" + str(port)
	import time
	now = time.time()
	with connect(addr_info, False, None) as conn:
    		token, cli = conn
   
		try:		
			f = open(csv_file)
		except IOError:
        		print 'cannot open file'
			return
		except:
			return

		print ('open ' + csv_file + ' insert to ' + bt_name)
		insert_prefix = 'INSERT INTO ' + bt_name + " VALUES "
		line_count = 0
	    
		first_line = f.readline()
		check_double_qoute = first_line.count('\"') 
		check_comma = first_line.count(',')
	   
		remove_double_quote = False
		if(check_double_qoute >= 2*check_comma):
			remove_double_quote = True
			print ("Double quoted csv file")

		f.seek(0)
		
		data_str = ""
		for line in f:
			line_count += 1
		
			if (remove_double_quote == False):
				data_str += "(" + addSingleQuote(line.rstrip()) + ")"
			else:
				data_str += "(" + dequote(line.rstrip()) + ")"
		
			if (line_count % insert_line) == 0 and line_count != 1:
				try:
					cli.sql_execute(token,insert_prefix + data_str , True)
				except:
					traceback.print_exc()
		   			print "Unexpected error:" + str(sys.exc_info()[0])
					print line_count	
					errorfile.write(data_str)
					errorfile.write('\n=========================================\n')
				data_str = ""
			else:
				data_str += ","
			

		if (line_count % insert_line) != 0:
			try:
				cli.sql_execute(token,insert_prefix + data_str[:len(data_str)-1] , True)
			except:
				traceback.print_exc()
	   			print "Unexpected error:" + str(sys.exc_info()[0])

		f.close()
		end = time.time()

		return 'insertion done. total %i rows , time: %ss' %  (line_count, round((end - now),2))
	return

if __name__ == '__main__':

	if(len(sys.argv) < 6):
		print ("csvloader.py <host> <port> <token> <csv filename> <bigtable name>")
		exit()

	csvload(sys.argv[1], sys.argv[2] , sys.argv[3], sys.argv[4], sys.argv[5])
	print ("test done.")
