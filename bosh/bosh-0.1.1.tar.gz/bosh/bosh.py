import sys
import cmd
import os

import rpcshell

import re
import boshCmd
import csvloader
from urlparse import urlparse
import texttable
import tools
import getpass
import traceback
import readline



d_type = "postgresql"
d_host = ""
d_port = ""
d_user = ""
d_pass = ""
d_db = ""
db_access_str = ""


def load_database_url(db_url):
	if db_url != "" and db_url != None:
		global d_type, d_host, d_port, d_user, d_pass, d_db, db_access_str
		url_object = urlparse(db_url)
		d_type = url_object.scheme
		if d_type == "postgres":
			d_type = "postgresql"
		d_host = url_object.hostname
		d_port = url_object.port
		d_user = url_object.username
		d_pass = url_object.password
		d_db = url_object.path[1:]

		db_access_str = '"' + "type=" + str(d_type) + " host=" + str(d_host) + " port=" + str(d_port) + " user=" + str(d_user) + " password=" + str(d_pass) + " db=" + str(d_db) + '"' 
		#print "DATABASE_URL :" + db_access_str
	else:
		print "DATABASE_URL is empty"
		db_access_str = ""
	return db_access_str

def dbinput():
	global d_type, d_host, d_port, d_user, d_pass, d_db, db_access_str
	dbtype = raw_input(">>> database type [" + d_type + "] : " )
	if dbtype != "":
		d_type = dbtype
	host = raw_input(">>> host [" + d_host + "] : " )
	if host != "":
		d_host = host
	port = raw_input(">>> port [" + d_port + "] : " )
	if port != "":
		d_port = port
	username = raw_input(">>> username [" + d_user + "] : " )
	if username != "":
		d_user = username
	password = getpass.getpass(">>> Password (hidden) : ")
	if password != "":
		d_pass = password
	dbname = raw_input(">>> database name [" + d_db + "] : " )
	if dbname != "":
		d_db = dbname
	
	db_access_str = '"' + "type=" + str(d_type) + " host=" + str(d_host) + " port=" + str(d_port) + " user=" + str(d_user) + " password=" + str(d_pass) + " db=" + str(d_db) + '"'
	return db_access_str

class baseCmd(cmd.Cmd):
	#def __init__(self):
	#	cmd.Cmd.__init__(self)
	def emptyline(self):
    		pass
	def do_exit(self, line):
	        return True
	def do_quit(self, line):
		return True

	def setremote(self, host, port, token, prompt, timeout=30):
		self.host = host
		self.port = port
		self.token = token
		self.timeout = timeout
		self.prompt = prompt
		self.intro = "Welcome to the BigObject shell\n\nenter 'help' for listing commands\nenter 'quit'/'exit' to exit bosh"

	def do_sethost(self, line):
		if line != "":
			self.host = line
	def do_setport(self, line):
		if line != "":
			self.port = line
	def do_settimeout(self, line):
		if line != "":
			self.timeout = line
	#def do_la(self, line):
	#	newcmd = laCmd()
	#	newcmd.host = self.host
	#	newcmd.port = self.port
	#	newcmd.token = self.token
	#	newcmd.timeout = 600
	#	newcmd.prompt = self.prompt[:len(self.prompt)-1] + ":la>"
	#	newcmd.cmdloop()

	#def do_assoc(self, line):
	#	newcmd = associateCmd()
	#	newcmd.host = self.host
	#	newcmd.port = self.port
	#	newcmd.token = self.token
	#	newcmd.timeout = 9999
	#	newcmd.algorithm = 'cos_sim'
	#	newcmd.prompt = self.prompt[:len(self.prompt)-1] + ":assoc>"
	#	newcmd.cmdloop()
		
	#def do_sql(self, line):
	#	if line != "":
	#		print "perform sql command : " + line
	#		#print sqlshell.shell(self.host, self.port ,self.token, line, self.timeout)
	#		print rpcshell.shell(self.host, self.port ,self.token, "sql" , line, self.timeout)
	#	else:
	#		newcmd = sqlCmd()
	#		newcmd.host = self.host
	#		newcmd.port = self.port
	#		newcmd.token = self.token
	#		newcmd.timeout = 9999
	#		newcmd.prompt = self.prompt[:len(self.prompt)-1] + ":*sql>"
	#		newcmd.draw_texttable()
	#		newcmd.cmdloop()

	def do_csvloader(self, line):
		if line != "":
			input_line = line.split();
			if len(input_line) >= 2:
				print csvloader.csvload(self.host, self.port ,self.token, input_line[0] , input_line[1])
			else:
				print "csvloader <csv_file> <bt_name>"
	def do_psql(self, line):
		db_url = os.environ.get('DATABASE_URL')
		load_database_url(db_url)
		print 
		tools.psql_run(d_host, d_port, d_user, d_pass, d_db)
		
	def do_info(self, line):
		print "host : " + self.host	
		print "port : " + str(self.port)
		print "timeout : " + str(self.timeout)

	def help_psql(self):
		print "\trun postgresql client. psql required"
	def help_csvloader(self):
		print "\tload a local CSV file into a server-side BigObject table\n\tex. csvloader <csv_file> <bt_name>"
	def help_sethost(self):
		print "\tset host name"
	def help_setport(self):
		print "\tset port"
	def help_settimeout(self):
		print "\tset timeout value"

class associateCmd(cmd.Cmd):
	#assocword = [ 'associate', 'association', 'with', 'from' , 'by' , 'where' , 'query' , 'tables' , 'associates', 'from', 'by', 'group by' , 'where' , 'tree' , 'table' , 'fact' , 'dim']
	assocword = [ 'association', 'with', 'from' , 'by' , 'where' , 'query' , 'tables' , 'from', 'by', 'group by' , 'where' , 'tree' , 'table' , 'fact' , 'dim']
	#algorithm_set = ['cos_sim', 'aggr']
	def __init__(self):
		cmd.Cmd.__init__(self)
		#self.var_list = set()
		import readline
		readline.set_history_length(80)
		try:
                    readline.read_history_file()
                except IOError:
                    readline.write_history_file()
	def completedefault(self, text, line, begidx, endidx):
		if not text:
			completions = self.assocword[:]
		else:
			completions = [ f
			for f in self.assocword
			if f.startswith(text)
			]
		return completions	
	def default(self, line):
		split_command = line.split('=')
		#if len(split_command) == 2:
		#	var_name=split_command[0]
		#	cmd_line=split_command[1]
		if len(split_command) >= 2 and len(split_command[0].split()) == 1:
			var_name=split_command[0]
			cmd_line=line[line.find('=') + 1:]
		else:
			cmd_line = line

		if line.strip().replace(" ","").find("=find") != -1: 
                        if "where " in line:
       	                     where_str_origin=cmd_line[cmd_line.find("where")+5:]
                             tmp_split=where_str_origin.split("=")
                             prefixStr=str()
                             varStr=str()
                             if len(tmp_split)>=2:
                                  prefixStr=tmp_split[0]+"="
                                  varStr=tmp_split[1]
                                  where_str=self.replace_var(varStr,prefix=prefixStr,joinstr="or")
                                  cmd_line=cmd_line.replace(where_str_origin,where_str)               
             
                        
			return_data = rpcshell.shell(self.host, self.port ,self.token, "assoc" , cmd_line, self.timeout)
			globals()[var_name] = return_data
		
		elif line.strip().replace(" ","").find("=query") != -1: 
			#if cmd_line.find('$') != -1:
			#	var_va = cmd_line[cmd_line.find('$') + 1:cmd_line.find(' ',cmd_line.find('$'))]
			#	cmd_line = cmd_line.replace("$"+var_va , str(globals()[var_va])[1:-1])
			#	#print line
	                strEnd=len(cmd_line) if cmd_line.find(" from")==-1 else cmd_line.find(" from")
		        query_str_origin=cmd_line[cmd_line.find("query ") + 5 : strEnd]
                        query_str=self.replace_var(query_str_origin)
                        cmd_line= "query "+query_str+cmd_line[strEnd:]
		          
			return_data = rpcshell.shell(self.host, self.port ,self.token, "assoc" , cmd_line, self.timeout)
			globals()[var_name] = return_data
			#self.var_list.add(var_name)

		elif line.strip().replace(" ","").find("=row") != -1: 
			temp_str=line[line.find("=row") + 4:]
			split_temp = temp_str.split()
			exec_str = var_name + "="
			repeated_str = "[" + split_temp[0] + "]"
			exec_str += "map(a.__getitem__," + repeated_str + ")"
			#print exec_str
			exec(exec_str) in globals()
			# a=[['a','b'],['c','d'],['e','f']]
			# b=row 1,2 in a

		elif line.strip().replace(" ","").find("=column") != -1: 
			temp_str=line[line.find("=column") + 8:]
			split_temp = re.split(r'[, ]', temp_str)
			#print split_temp
			#print split_temp[:-2]
			exec_str = var_name + "="
			repeated_str = ""
			for sp in split_temp[:-2]:
				repeated_str += "[__row["+ sp + "]"
				repeated_str += " for __row in "
				repeated_str += split_temp[-1] + "],"
			if len(split_temp[:-2]) > 1:
				exec_str += "[list(__merge_i) for __merge_i in zip("
				exec_str += repeated_str[:-1] + ")]"
			else:
				exec_str += repeated_str[:-1]
			exec(exec_str) in globals()
			#check_unicode_string = "if isinstance(" + var_name + "[0], unicode)==True:" + var_name + "=" + var_name +".encode('ascii','replace')"
			check_unicode_string = "if isinstance(" + var_name + "[0], basestring)==True:" + var_name + "=[row.encode('ascii','replace') for row in " + var_name + "]"
			try:
				exec(check_unicode_string) in globals()
			except:
				traceback.print_exc()

			#print exec_str	
			# a=[['a','b',1],['d','e',2]]
			# b=column 1,2 in a
			# [list(wa) for wa in zip([row[1] for row in a],[row[0] for row in a])]
		else:
			try:
				exec(line) in globals()
			except:
				traceback.print_exc()

		#elif line.find("=query") != -1: 
		#	return_data = rpcshell.shell(self.host, self.port ,self.token, "assoc" , cmd_line, self.timeout)
		#	globals()[var_name] = return_data
		#	self.var_list.add(var_name)

		#if line.find("=create") != -1: 
		#if line.find("=query") != -1: 
		#if line.find("associate") != -1:
		#	tools.parse_associate_string_for_display(line)			
		#	print rpcshell.shell(self.host, self.port ,self.token, "assoc" , line, self.timeout)
		#else:
		#	print "*** Unknown syntax: " + line

	#def do_testv(self, line):
	#	for var_temp in self.get_bosh_global_var_with_filter():
	#		if var_temp in line:
	#			print "found"

	
	def do_listvar(self, line):
		#print "all variables: " + str(list(self.var_list))
		print "all variables: "		
		print self.get_bosh_global_var_with_filter()
	def do_find(self, line):
                if "where " in line:
	              where_str_origin=line[line.find("where")+5:]
                      tmp_split=where_str_origin.split("=")
                      prefixStr=str()
                      varStr=str()
                      if len(tmp_split)>=2:
                           prefixStr=tmp_split[0]+"="
                           varStr=tmp_split[1]
                           where_str=self.replace_var(varStr,prefix=prefixStr,joinstr="or")
                           line=line.replace(where_str_origin,where_str)               
                
         	rpcshell.shell(self.host, self.port ,self.token, "assoc" , "find " + line, self.timeout)


	def do_create(self, line):
		#print rpcshell.shell(self.host, self.port ,self.token, "assoc" , "build " + line, self.timeout)
		print rpcshell.shell(self.host, self.port ,self.token, "assoc" , "create " + line, self.timeout)

	def do_build(self, line):
		#print rpcshell.shell(self.host, self.port ,self.token, "assoc" , "build " + line, self.timeout)
		print rpcshell.shell(self.host, self.port ,self.token, "assoc" , "create " + line, self.timeout)
        
        def do_ask(self, line):
                if "about" in line:
                      stoplist=["where","for","top","bottom"]
                      stopPoslist=[ len(line) if line.find(stopstr)==-1 else line.find(stopstr) for stopstr in stoplist ]
                      about_str_origin=line[line.find("about")+5:min(stopPoslist)]
                      about_str_origin=about_str_origin.strip(" ()")
                      about_str=self.replace_var(about_str_origin)
                      line=line.replace(about_str_origin, about_str)
 
                rpcshell.shell(self.host, self.port, self.token, "assoc","ask "+line,self.timeout)

	def do_query(self, line):
                strEnd=len(line) if line.find(" from")==-1 else line.find(" from")
		query_str_origin=line[line.find("query ") + 1 : strEnd]
                query_str=self.replace_var(query_str_origin)
                line= query_str+line[strEnd:]
		#print globals()
		#if line.find('$') != -1:
		#	var_va = line[line.find('$') + 1:line.find(' ',line.find('$'))]
		#	line = line.replace("$"+var_va , str(globals()[var_va])[1:-1])
		#	#print line
		rpcshell.shell(self.host, self.port ,self.token, "assoc" , "query " + line, self.timeout)
	#def do_set(self, line):
	#	if line[:9] == "algorithm":
	#		if line[10:] in associateCmd.algorithm_set:
	#			self.algorithm = line[10:]
	#			print "algorithm : " + self.algorithm

	def do_setprompt(self, line):
		self.prompt = line
	def do_info(self, line):
		print "host : " + self.host	
		print "port : " + str(self.port)
		print "timeout : " + str(self.timeout)
		#print "algorithm : " + self.algorithm
	def do_show(self, line):
		if line == "tables":
			print boshCmd.getinfo(self.host, self.port ,self.token, "get_table_list" , "" , self.timeout)
		#elif line == "matrices":
		#	print boshCmd.getinfo(self.host, self.port ,self.token, "get_mbt_list" , "" , self.timeout)
		#elif line == "algorithms":
		#	print self.algorithm_set
		elif line == "association":
			print boshCmd.getinfo(self.host, self.port ,self.token, "get_qbo_list" , "" , self.timeout)
		else:
			print "show [tables | association ]"
	def do_desc(self, line):
		if line[:12] == "association ":
			print boshCmd.getinfo(self.host, self.port ,self.token, "get_qbo_info" , line[12:], self.timeout)
		#elif line[:7] == "matrix ":
		#	print boshCmd.getinfo(self.host, self.port ,self.token, "get_mbt_info" , line[7:], self.timeout)
		elif line != "":
			print boshCmd.getinfo(self.host, self.port ,self.token, "get_table_schema" , line, self.timeout)
		else:
			print "desc [association] <name>"
	
	#def do_list(self, line):
	#	name = line.split()
	#	#print name[0] + "   " + name[1]
	#	rpcshell.shell(self.host, self.port ,self.token, "la" , "create tree listattribute from " + name[0] + " group by " + name[1], self.timeout)
	#	rpcshell.shell(self.host, self.port ,self.token, "la" , "select distinct # from listattribute", self.timeout)

	#def do_analyze(self, line):
	#	if line != "":
	#		if line.startswith('distinct'):
	#			print rpcshell.shell(self.host, self.port ,self.token, "la" , "select " + line, self.timeout)
	#		else:
	#			print rpcshell.shell(self.host, self.port ,self.token, "sql" , "select " + line, self.timeout)
	#def do_get(self, line):
	#	if line != "":
	#		if line.startswith('distinct'):
	#			print rpcshell.shell(self.host, self.port ,self.token, "la" , "select " + line, self.timeout)
	#		else:
	#			print rpcshell.shell(self.host, self.port ,self.token, "sql" , "select " + line, self.timeout)
	def do_exit(self, line):
	        return True
	def do_quit(self, line):
		return True	
	def emptyline(self):
    		pass
	def do_sql(self, line):
		if line != "":
			print "perform sql command : " + line
			print rpcshell.shell(self.host, self.port ,self.token, "sql" , line, self.timeout)
		else:
			newcmd = sqlCmd()
			newcmd.host = self.host
			newcmd.port = self.port
			newcmd.token = self.token
			newcmd.timeout = 9999
			newcmd.prompt = self.prompt[:len(self.prompt)-1] + ":*sql>"
			newcmd.draw_texttable()
			newcmd.cmdloop()
	def do_admin(self, line):
		newcmd = baseCmd()
		newcmd.host = self.host
		newcmd.port = self.port
		newcmd.token = self.token
		newcmd.timeout = 600
		newcmd.prompt = self.prompt[:len(self.prompt)-1] + ":admin>"
		newcmd.cmdloop()

        def do_print(self,line):
               command=line.split(">>")
               if len(command)==2:
                      doInvoke=False
                      outfile=str()
                      if "@" in command[1]:
                            outfile=command[1][command[1].find("@")+1:].strip()
                            if len(outfile)==0:
                                   return "*** FILENAME required after \">>@\""
                            doInvoke=True
                      else:  
                            outfile=command[1].strip()
                      outfile=tools.redirectFiles(globals()[command[0].strip()],outfile)
                      if outfile=="BADINPUT":
                            return "*** cancel outputting the file"
                      if doInvoke:
                            tools.invokeFiles(outfile)

               else:
	             try:
		           exec("print "+line) in globals()
		     except:
		           traceback.print_exc()

                       
	def writehist(self):
		import readline
		readline.set_history_length(80)
		readline.write_history_file()
		
	def get_bosh_global_var_with_filter(self):
		f = ['re', 'readline', 'd_pass', 'cmd', 'getpass', 'rpcshell', 'd_port', 'tools', 'dbinput', 'd_host', 'csvloader', 'load_database_url', 'main', 'sys', 'd_db', 'sqlCmd', 'texttable', 'baseCmd', 'associateCmd', 'traceback', 'urlparse', 'd_user', 'os', 'd_type', 'db_access_str', 'boshCmd']
		return [v for v in globals().keys() if not v.startswith('_') and not v in f]

        def replace_var(self,ori_str,prefix="",joinstr=","):
                #print "input str: ", ori_str
                #print "prefix: ", prefix
                
         	split_temp = re.split(r'[,]', ori_str)
                result_list=list()
                replace_list=list()
		for split_value in split_temp:
                        #print split_value
                        split_value=split_value.strip()
                        if split_value=="":continue
			if split_value in self.get_bosh_global_var_with_filter():
                                if isinstance(globals()[split_value],basestring):
                                     replace_list.append(globals()[split_value])
                                else:       
                                     replace_list.extend(globals()[split_value])
                        else:
                                result_list.append(split_value)
                #print "result var list:",result_list 
                new_str=joinstr.join(prefix+str(element) for element in result_list)
                new_str+=joinstr.join(prefix+"'"+str(element)+"'" for element in replace_list)
                
                #print "final str:" ,new_str
                return new_str
              

 
	def help_column(self):
		print "\tex. b=column 1 in a \n\tb=column 2,4 in a"
	def help_row(self):
		print "\tex. b=row 1 in a \n\tb=row 2,4 in a"
	def help_sql(self):
		print "\trun star-sql shell"
	def help_admin(self):
		print "\trun admin shell"
	#def help_get(self):
	#	print "\t An alias of analyze"

	def help_find(self):
		tools.print_help_string('assoc_find')
	#def help_analyze(self):
	#	tools.print_help_string('assoc_analyze')
	def help_create(self):
		tools.print_help_string('assoc_associate')
	def help_query(self):
		tools.print_help_string('assoc_query')
	def help_show(self):
		print "\tlist resource in the shell\n\tex. show [tables | association ]"
	def help_desc(self):
		print "\tshow meta-information of a resource\n\tex. desc [association] <name>"

class sqlCmd(cmd.Cmd):
	SELECTword = [ 'from', 'by', 'group by' , 'where' , 'sum' , 'count' , 'distinct' ]
	def complete_select(self, text, line, begidx, endidx):
		if not text:
			completions = self.SELECTword[:]
		else:
			completions = [ f
			for f in self.SELECTword
			if f.startswith(text)
			]
		return completions	
	CREATEword = [ 'from', 'by', 'group by' , 'where' , 'tree' , 'table' , 'fact' , 'dim']
	def complete_create(self, text, line, begidx, endidx):
		if not text:
			completions = self.CREATEword[:]
		else:
			completions = [ f
			for f in self.CREATEword
			if f.startswith(text)
			]
		return completions

	def draw_texttable(self):
		table = texttable.Texttable()
		table.set_cols_align(["l"])
		table.set_cols_valign(["b"])
		table.add_rows([ ["Welcome to Star-SQL"], 
			["Star-SQL is a small subset of SQL for datasets in star schema or snowflake schema.\nIt is aimed to address analytic problems rather than transactional problems.\nType \"help\" for more information."],
                        ["Type \"enableColor\" if your terminal support ANSI escape code."],
                        ["Draw charts in Excel or HTML files! Type \"help syntaxout\" for examples."]
                 ])
		print table.draw() + "\n"

	def emptyline(self):
    		pass

	def setremote(self, host, port, token, timeout=30):
		self.host = host
		self.port = port
		self.token = token
		self.timeout = timeout
		self.prompt = "bosh>"
		print "server : " + self.host + ":" + str(self.port)
		print "enter quit/exit to exit bosh"

	def do_show(self, line):
		if line == "tables":
			print boshCmd.getinfo(self.host, self.port ,self.token, "get_table_list" , "" , self.timeout)
		else:
			print "list tables: 'show tables'"
		
	def do_starschema(self, line):
		if line != "":
			print boshCmd.getinfo(self.host, self.port ,self.token, "get_table_relation" , line , self.timeout)
	def do_desc(self, line):
		if line != "":
			print boshCmd.getinfo(self.host, self.port ,self.token, "get_table_schema" , line, self.timeout)

	def do_settimeout(self, line):
		if line != "":
			self.timeout = line
	def do_info(self, line):
		print "host : " + self.host	
		print "port : " + str(self.port)
		print "timeout : " + str(self.timeout)
	def do_select(self, line):
		if line != "":
			if line.startswith('distinct'):
				print rpcshell.shell(self.host, self.port ,self.token, "la" , "select " + line, self.timeout)
			else:
				print rpcshell.shell(self.host, self.port ,self.token, "sql" , "select " + line, self.timeout)
	def do_create(self, line):
		if line != "":
			if line.startswith('tree') or line.startswith('fulltree'):
				print rpcshell.shell(self.host, self.port ,self.token, "la" , "create " + line, self.timeout)
			else:
				print rpcshell.shell(self.host, self.port ,self.token, "sql" , "create " + line, self.timeout)	
	def do_insert(self, line):
		if line != "":
			print rpcshell.shell(self.host, self.port ,self.token, "sql" , "insert " + line, self.timeout)	
	def do_update(self, line):
		if line != "":		
			print rpcshell.shell(self.host, self.port ,self.token, "sql" , "update " + line, self.timeout)	
	def do_drop(self, line):
		if line != "":
			print rpcshell.shell(self.host, self.port ,self.token, "sql" , "drop " + line, self.timeout)	

	def do_copy(self, line):
		db_url = os.environ.get('DATABASE_URL')
		db_access_str = load_database_url(db_url)

		if line != "":
			if line.find("DATABASE") != -1 and db_access_str != "":
				line = line.replace("DATABASE" , db_access_str)
				#print "line: " + line
			elif line.find("DATABASE") != -1 and db_access_str == "":
				print "input your database information"
				db_access_str = dbinput()
				line = line.replace("DATABASE" , db_access_str)
			print rpcshell.shell(self.host, self.port ,self.token, "sql" ,"copy " + line , self.timeout) 	
	def do_load(self, line):
		db_url = os.environ.get('DATABASE_URL')
		db_access_str = load_database_url(db_url)

		if line != "":
			if line.find("DATABASE") != -1 and db_access_str != "":
				line = line.replace("DATABASE" , db_access_str)
				#print "line: " + line
			elif line.find("DATABASE") != -1 and db_access_str == "":
				print "input your database information"
				db_access_str = dbinput()
				line = line.replace("DATABASE" , db_access_str)
			print rpcshell.shell(self.host, self.port ,self.token, "sql" ,"load " + line , self.timeout) 	
	
	def do_exit(self, line):
	        return True
	def do_quit(self, line):
		return True
        
        def do_disableColor(self, line):
                tools.docSql.disableColor()
 
        def do_enableColor(self, line):
                tools.docSql.enableColor()
	def help_select(self):
		tools.print_help_string('sql_select')

	def help_create(self):
		tools.print_help_string('sql_create')

	def help_insert(self):
		tools.print_help_string('sql_insert')

	def help_update(self):
		tools.print_help_string('sql_update')
	
	def help_desc(self):
		#print "\tlist table's attribute\n\tdesc <table name>"
                tools.print_help_string('sql_desc')
	def help_show(self):
		#print "\tlist all BigObject tables in workspace\n\tshow tables"
                tools.print_help_string('sql_show')
	def help_starschema(self):
		#print "\tshow table's metainfo including related tables\n\tstarschema <table name>"
                tools.print_help_string('sql_starschema')
	def help_copy(self):
		tools.print_help_string('sql_copy')

	def help_load(self):
		tools.print_help_string('sql_load')
        
        def help_syntaxout(self):
                tools.print_help_string('sql_syntaxout')


def main():
	host = "localhost"
	port = "9090"
	token = ""
	bo_url = os.environ.get('BIGOBJECT_URL')
	if bo_url != None:
		url_object = urlparse(bo_url)
		token = url_object.password
		host = url_object.hostname
		port = url_object.port

	#cmd = baseCmd()
	#cmd.setremote(host, port , token, "bosh>")
	newcmd = associateCmd()
	newcmd.bosrv_url = bo_url
	newcmd.host = host
	newcmd.port = port
	newcmd.token = token
	newcmd.timeout = 9999
	#newcmd.algorithm = 'cos_sim'
	newcmd.prompt = "bosh>"
	newcmd.intro = "\nWelcome to the BigObject shell\n\nenter 'help' for listing commands\nenter 'quit'/'exit' to exit bosh"
	#newcmd.use_rawinput = False

	try:
		newcmd.cmdloop()
		#cmd.cmdloop()
	except KeyboardInterrupt:
		print "exiting by KeyboardInterrupt"
		newcmd.writehist()
	print "Thanks for using bosh..."

if __name__ == '__main__':
        main()
