import os
import sys
import traceback
from bosrv.request import connect
from bosrv.ttypes import *
from exc.ttypes import *
import tools


def shell(host, port, token_str, shell_name, command, timeout):
	import time
	now = time.time()
	result_str = ""
	addr_info= "bo://:" + token_str + "@" + host + ":" + str(port)
	
        temp_command_str=command.split('>>')
        output_command=str()

        if len(temp_command_str)>=2:
              command=temp_command_str[0]
              output_command=temp_command_str[1]         
              if len(output_command)==0:
                   return "*** FILENAME required after \">>\""           

	result_table = []

	try:
		with connect(addr_info, False, int(timeout)) as conn:
    			token, cli = conn
		#with connect(addr_info, int(timeout)) as cli:
			try:
				if shell_name == "sql":
					exec_ret = cli.sql_execute(token, command, True)
				elif shell_name == "la":
					exec_ret = cli.aux_execute(token, command, True)
				elif shell_name == "assoc":
					exec_ret = cli.assoc_execute(token, command, True)
			except:
				traceback.print_exc()
				exec_ret = ""
	   			result_str = "Unexpected error:" + str(sys.exc_info()[0])
			end = time.time()
			#table_str = ""

		
			if (exec_ret != ""):
				import json
				limit = 100 # decide the limit of records returned per fetch
				
				eol = None
				while eol != -1:
					try:
						temp = json.loads(cli.cursor_fetch(
							token,
							exec_ret,
							RangeSpec(page=100)
							))
						eol, rows = temp # if eol == -1, then no more data to read
						result_table.extend(rows)
					except:
						print "except : " + str(sys.exc_info()[0])
						traceback.print_exc() 
						break
				else:
				    cli.cursor_close(token,exec_ret)

				key_index = 0

				result_str = "result:\n"
				#result_str += "size:" + str(len(result_table)) + "\n"
			
				for record in result_table:
				    #print str(record).decode('unicode-escape')
				    result_str += str(record).decode('unicode-escape')
				    result_str += "\n"
				    #table_str += str(record) + ","
				result_str += "size:" + str(len(result_table)) + "\n"
                                
 
		                if output_command :
                                     doInvoke=False
                                     outfile=str()
                                     if "@" in output_command:
                                            outfile=output_command[output_command.find("@")+1:].strip()
                                            if len(outfile)==0:
                                                   return "*** FILENAME required after \">>@\""
                                            doInvoke=True
                                     else:
                                            outfile=output_command.strip()
                                     outfile=tools.redirectFiles(result_table,outfile) 
                                     if outfile=="BADINPUT":
                                            return "*** cancel outputting the file"
                                     if doInvoke:
                                            tools.invokeFiles(outfile)	

			#print "send: \"" + command + "\" to " + host + ":" + str(port) + "\n" + result_str + '\ntime: %ss' %  str(round((end - now),2)) + "\n" 	
			print "send: \"" + command + "\" to " + host + ":" + str(port) + "\n"
			print result_str 
			print 'time: %ss' %  str(round((end - now),2)) + "\n"	
			print "======================"
			if len(result_table) > 0:
				return result_table
			else:
				return ""

	except:
		traceback.print_exc()
		print "======================"
		return ""
