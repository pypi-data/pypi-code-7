import os
import sys
import traceback
from bosrv.connect import connect
from bosrv.ttypes import *
from exc.ttypes import *
import boshExcel
import boshC3


def shell(host, port, token, shell_name, command, timeout):
	import time
	now = time.time()
	addr_info = (
		str(host),
		int(port)
		)
	result_str = ""

        temp_command_str=command.split('>>')
        output_command=str()

        if len(temp_command_str)>=2:
              command=temp_command_str[0]
              output_command=temp_command_str[1]         
              if len(output_command)==0:
                   return "*** FILENAME required after \">>\""           

	result_table = []

	try:
		with connect(addr_info, int(timeout)) as cli:
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
				

				#now = time.time()

				while not result_table or result_table[-1] != -1:
					try:
						temp = cli.cursor_fetch(
							token,
							exec_ret,
							RangeSpec(page=limit)
					   		)
						row = json.loads(temp)
					    	result_table.extend(row)
					
					except:
						print "except : " + str(sys.exc_info()[0])
						traceback.print_exc() 
						break
					

				else:
				    cli.cursor_close(token,exec_ret)
				    result_table.pop()
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
                                     if ".html" in outfile:                                          
                                            outfile=boshC3.Default_output(result_table,outfile)
                                            if outfile == "BADINPUT" :
                                                 return "*** Cancel output"
                                     elif ".xlsx" in outfile:
		                            template=outfile if os.path.exists(outfile) else None
		                            boshExcel.Default_output(result_table,template=template,output=outfile)
                                     elif ".csv" in outfile:
                                            import csv
                                            with open(outfile,"w") as csvfile:
                                                 writer=csv.writer(csvfile)
                                                 for row in result_table:
                                                        writer.writerow(row)    
	
                                     else:
                                            fd=open(outfile,"w")
                                            jsonstr=json.dumps(result_table)
                                            fd.write(jsonstr)
                                            fd.close()
                                     print "Write into file: "+os.path.abspath(outfile)
                                     
                                     if doInvoke:
                                            from subprocess import Popen
                                            import platform
                                            try:
                                                 saverr=os.dup(2)
                                                 os.close(2)
                                                 if "Darwin" in platform.system():
                                                       Popen(["open",outfile])
                                                 elif os.name=="posix":
                                                       Popen(["xdg-open",outfile])
                                                 elif os.name=="nt":
                                                       Popen(["open",outfile])
                                                 else:
                                                       print "Invoke function is not supported under your os environment." 
                                            finally:
                                                 os.dup2(saverr,2)
	
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
