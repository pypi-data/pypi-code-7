from tkinter import *
import time

BUFFER_PATH = r'\\VBOXSVR\pynportal\buffer.txt'

def main():
	g = PynServerGui()

class PynServerGui:
	def __init__(self):
		'''
		A simple GUI to catch input from NS and send it to the buffer file
		'''
		self.root = Tk()
		self.root.title('Pynlistener')
		self.text_box = Text(self.root)
		self.content = ''
		self.entry_time = 0
		self.text_box.focus()
		self.root.bind('<Key>', self.enter_key)
		self.text_box.pack()
		self.root.after(20, self.send_input)
		self.root.mainloop()
		
	def send_input(self):
		self.root.after(20, self.send_input)
		self.content = self.text_box.get('1.0', END).strip()
		if self.content and time.clock() - self.entry_time > .1:
			with open(BUFFER_PATH, 'a') as f:
				f.write('{}\n'.format(self.content))
			self.text_box.delete('1.0', END)
			self.content = ''
		
		
	def enter_key(self, *args):
		self.entry_time = time.clock()
		
if __name__ == '__main__':
	main()
