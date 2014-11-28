import gspread


class GWSheet(object):
	def __init__(self, wbook, wsheet):
		self._wbook=wbook
		self._wsheet=wsheet
		self._cells=[]

	@property
	def wbook(self):
	    return self._wbook

	@property
	def wsheet(self):
	    return self._wsheet

	@property
	def nbRows(self):
	    return self.wsheet.row_count
	@nbRows.setter
	def nbRows(self, value):
	    self.wsheet.resize(rows=value)

	@property
	def nbCols(self):
	    return self.wsheet.col_count
	@nbCols.setter
	def nbCols(self, value):
	    self.wsheet.resize(cols=value)

	def range(self, arange):
		return self.wsheet.range(arange)

	def __getitem__(self, key):
		try:
			return self.wsheet.acell(key).value
		except:
			pass

	def __setitem__(self, key, value):
		try:
			return self.wsheet.update_acell(key, value)
		except:
			pass

	def set(self, aref, value):
		try:
			return self.wsheet.update_acell(aref, value)
		except:
			pass

	def setat(self, row, col, value):
		try:
			return self.wsheet.update_cell(row, col, value)
		except:
			pass

	def update(self):
		try:
			if self._cells:
				self.wsheet.update_cells(self._cells)
				self._cells=[]
		except:
			pass

	def vwrite(self, values, a0='a1'):
		try:
			size=len(values)

			(r0,c0)=self.wsheet.get_int_addr(a0)
			r1=r0+size-1

			if self.nbRows<r1:
				self.nbRows=r1

			a1=self.wsheet.get_addr_int(r1,c0)

			cells=self.range('%s:%s' % (a0,a1))
			for cell in cells:
				cell.value=values[cell.row-r0]

			self._cells.extend(cells)
			return a1r
		except:
			pass

	def hwrite(self, values, a0='a1'):
		try:
			size=len(values)

			(r0,c0)=self.wsheet.get_int_addr(a0)
			c1=c0+size-1

			if self.nbCols<c1:
				self.nbCols=c1

			a1=self.wsheet.get_addr_int(r0,c1)

			cells=self.range('%s:%s' % (a0,a1))
			for cell in cells:
				cell.value=values[cell.col-c0]
			self._cells.extend(cells)
			return a1
		except:
			pass

	def aoffset(self, aref, rows=0, cols=0):
		(r0,c0)=self.wsheet.get_int_addr(aref)
		return self.wsheet.get_addr_int(r0+rows, c0+cols)

	def right(self, aref, cols=1):
		return self.aoffset(aref, cols=cols)

	def left(self, aref, cols=1):
		return self.aoffset(aref, cols=-cols)

	def down(self, aref, rows=1):
		return self.aoffset(aref, rows=rows)

	def up(self, aref, rows=1):
		return self.aoffset(aref, rows=-rows)


class GWBook(object):
	def __init__(self, gs, wbook):
		self._gspread=gs
		self._wbook=wbook

	@property
	def wbook(self):
	    return self._wbook

	@property
	def service(self):
	    return self._gspread.service

	def wsheet(self, index=0):
		try:
			wsheet=self.wbook.get_worksheet(index)
			return GWSheet(self, wsheet)
		except:
			pass

	@property
	def wsheet1(self):
	    return self.wsheet(0)


class GSpread(object):
	def __init__(self, user, password):
		self._user=user
		self._password=password
		self._gspread=None
		self.login()

	@property
	def service(self):
	    return self._gspread

	def login(self, force=False):
		if not force and self._gspread:
			return self._gspread
		try:
			self._gspread=gspread.login(self._user, self._password)
		except:
			pass

	def wbook(self, name):
		try:
			wbook=self.service.open(name)
			return GWBook(self, wbook)
		except:
			pass


