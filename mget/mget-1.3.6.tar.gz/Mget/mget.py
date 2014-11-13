#!/usr/bin/env python3

import time
import os, sys
from .utils import *
from .downloader import *
from .extractor import *

class MGetDL(FileDownloader):
	def __init__(self, opts, info):
		super(MGetDL, self).__init__(info)

		if opts.verbose: common.debug_info(info)
		self.info = info
		self.params = opts
		self.defurl = self.info.get('defurl')
		self.client = client.Client(self.info)
		self.ie_result = self.get_ie_result(self.defurl)
		self.url = self.ie_result.get('url', self.defurl)

		self.info['filename'] = self.params.filename or \
					self.ie_result.get('filename') or self.info.get('def_page')

		self.cursize = self.getLocalFilesize(self.info.get("filename")) or 0
		self.quitsize = self.params.quitsize
		self.site = self.ie_result.get('site')
		self.hostname = self.ie_result.get('hostname')
		self._try = 0

	def get_ie_result(self, url):
		try: return get_info(url, self.client, self.info)
		except ExtractorError as err:
			if self.info.get('debug_mget'): common.report_error(err._trace())
			else: common.report_error(str(err))
			exit(2)

	def __downloadFile__(self, urlObj):
		tmpfilename = info.get("filename")
		tmpfilename1 = self.temp_name(tmpfilename)

		self.mode = 'wb' if self.cursize == 0 else 'ab'
		info['start_time'] = time.time()

		if (info.get("quit_size") == 100.0 and \
		not os.path.exists(tmpfilename)) or os.path.exists(tmpfilename1):
			tmpfilename = tmpfilename1

		try:
			with open(tmpfilename, self.mode) as fileObj:
				dl = MGetDownloader(urlObj, fileObj, info)
				dl.start()

		except (sock_timeout, sock_error) as err:
			common._error(str(err) + "\n")
			return self.__retry__()

		except (ContentTooShortError, DownloadError) as err:
			common.report_error(str(err))
			if info.get('retryerror', False): return self.__retry__()
			else:
				self.cursize = self.getLocalFilesize(tmpfilename)
				self.quitting(tmpfilename.encode(),\
								self.cursize,info.get('filesize'))
				if self.info.get('ignore'): return False
				else: exit(2)

		except (KeyboardInterrupt, SystemExit):
			self.cursize = self.getLocalFilesize(tmpfilename)
			self.quitting(tmpfilename.encode(),\
								self.cursize,info.get('filesize'))
			exit(1)

		except (IOError, OSError) as err:
			detail.report_error(err)
			exit(1)

		except (TypeError, ValueError, NameError) as err:
			self.cursize = self.getLocalFilesize(tmpfilename)
			self.quitting(tmpfilename.encode(),\
								self.cursize,info.get('filesize'))
			if self.info.get('debug_mget'):
				common.write_string(FormatTrace(sys.exc_info()))
			else: common.report_error(str(err))

			if self.info.get('ignore'): return False
			else: exit(2)

		finally:
			if self.params.cookiefile: self.cookiejar.save(ignore_discard=True)
			urlObj.close()

		if tmpfilename.endswith (".part"): self.try_rename(tmpfilename, info.get("filename"))
		return True

	def __retry__(self):
		progress = self.get_progress(self.cursize,info.get('filesize', 0))
		if progress >= self.params.quitsize: common.write_string(common.FILE_EXIST)

		self._try += 1
		self.cursize = self.getLocalFilesize(info.get("filename"))
		self.trying(self._try,self.cursize,info.get('filesize'))
		time.sleep(info.get('waitretry', 1))

		if self.cursize != info.get('filesize'):
			self.init_(url=self.url)
			common.report("Retrying download-%02d at: %d [%s]" % \
			(info.get('cur_download', 1), self.cursize, self.format_size(self.cursize)))
			self.resume(retrying=True)
		return True

	def resume(self, retrying = False):
		if retrying:
			common.report("Re-connecting to %s..." % self.hostname)
			_info = self.client.getInfos(self.url, self.cursize)
			if _info is None: return False

			info['cursize'] = self.cursize
			info['resuming'] = True if self.cursize != 0 else False
			info.update(_info)

			self.print_info(info)

		self.__downloadFile__(info.get('urllibObj'))

	def start(self):
		global info
		if self.info.get('restart'): self.cursize = 0; self.mode = 'wb'
		if self.params.geturl or self.params.embedurl: common.report(self.url); return True

		self.init_(url=self.url)
		common.report("Connecting to %s..." % self.hostname)
		info = self.client.getInfos(self.url, self.cursize)

		if info is None: return False

		info["ext"] = os.path.splitext(self.info.get("filename"))[1][1:]
		info['cursize'] = self.cursize
		info['resuming'] = True if self.cursize != 0 else False
		info['expected'] = self.get_expected(info.get('filesize'), self.params.quitsize)
		info.update(self.info)
		self.cookiejar = info.get('cookiejar')

		if os.path.exists(info.get("filename")):
			if info.get("nofilesize") or not self.info.get('continue'):
				info["filename"] = common.EXFilename(info.get("filename"))
				self.cursize = self.getLocalFilesize(info.get("filename")) or 0

		if info.get('dump_head'):
			common._stderr(info.get('headers'));
			if self.params.cookiefile: self.cookiejar.save(ignore_discard=True)
			return True

		if info.get('write_info'):
			common.write_info(info);
			if self.params.cookiefile: self.cookiejar.save(ignore_discard=True)
			return True

		self.print_info(info)

		if info.get('dump_info'):
			if self.params.cookiefile: self.cookiejar.save(ignore_discard=True)
			return True

		if self.cursize - 100 < info.get('filesize') < self.cursize + 100:
			if not info.get("nofilesize"):
				if self.info.get('debug_mget'): common.report("Quit size reached!")
				common.write_string(common.FILE_EXIST, False); return True

		if info.get('quit_size') != 100.0:
			progress = self.get_progress(self.cursize,info.get('filesize', 0))
			if progress >= self.params.quitsize:
				if self.info.get('debug_mget'):
					common.report("Quit size reached!")
				common.write_string(common.FILE_EXIST, False); return True

		self.__downloadFile__(info.get('urllibObj'))
		self.cursize = self.getLocalFilesize(info.get("filename"))

		if info.get("rename") is not None and info.get("quit_size") == 100.0:
			self.try_rename(info.get("filename"), info.get("rename"))
			info["filename"] = info.get("rename")

		_opts= {
		'speed': self.calc_speed(time.time()-info['start_time'],self.cursize-info['cursize']),
		'filename': info.get("filename").encode(),
		'cursize': self.cursize,
		'filesize': info.get('filesize')}

		self.done_dl(**_opts)

		return info

	def __exit__(self, *args):
		if self.params.cookiefile: self.cookiejar.save()
