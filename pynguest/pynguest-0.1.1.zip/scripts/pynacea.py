import tkinter
import time
import os
import re
from pkg_resources import Requirement, resource_filename
import pynguest

CONFIG_PATH = resource_filename(Requirement.parse("pynguest"), "pynguest_config.ini")

def main():
	try:
		shared_dir = get_shared_directory()
	except:
		with open(CONFIG_PATH, 'w') as f:
			f.write('[settings]\n')
			f.write('shared_dir = None')
		shared_dir = 'None'
		if (shared_dir == 'None' or
		len(sys.argv) == 2 and sys.argv[1] == 'config'):
			if shared_dir == 'None':
				print('Shared directory is currently not set')
			else:
				print('Shared directory is currently {}'.format(shared_dir))
			shared_dir = input('Enter the shared directory between the virtual'
			" machine and the host operating system (press 'q' to quit): ")
			if shared_dir != 'q':
				save_directory(shared_dir)
			print('Directory {} successfully saved!'.format(shared_dir))
		else:
			g = PynServerGui(shared_dir)
		
def get_shared_directory():
	config = configparser.ConfigParser()
	config.read(CONFIG_PATH)
	return(config['settings']['shared_dir'])
	
def save_directory(value):
	config = configparser.ConfigParser()
	config.read(CONFIG_PATH)
	config['settings']['shared_dir'] = value
	with open(CONFIG_PATH, 'w') as configfile:
		config.write(configfile) 
		
class PynGuestGui:
	def __init__(self, buffer_dir):
		'''
		A simple GUI to catch key inputs (such as those sent from voice
		recognition software) and pass them to the provided buffer file
		'''
		self.buffer_dir = buffer_dir
		self.root = tkinter.Tk()
		self.root.title('PynGuest')
		self.text_box = tkinter.Text(self.root)
		self.content = ''
		self.entry_time = 0
		self.text_box.focus()
		self.root.bind('<Key>', self.enter_key)
		self.text_box.pack()
		self.root.after(20, self.send_input)
		self.root.mainloop()
		
	def send_input(self):
		self.root.after(20, self.send_input)
		self.content = self.text_box.get('1.0', tkinter.END).strip()
		if self.content and time.clock() - self.entry_time > .1:
			buffer_name = self.get_next_filename()
			with open(buffer_name, 'w') as f:
				print('Sending {}'.format(self.content))
				f.write('{}\n'.format(self.content))
			self.text_box.delete('1.0', tkinter.END)
			self.content = ''
		
	def get_next_filename(self):
		nums = [int(f[1:]) for f in os.listdir(self.buffer_dir) if not os.path.isdir(f) and re.match(r'o\d+$', f)]
		if nums:
			name = 'o{}'.format(max(nums) + 1)
		else:
			name = 'o1'
		return os.path.join(self.buffer_dir, name)
	
	def enter_key(self, *args):
		self.entry_time = time.clock()

def get_drives(drive_letters):
	import ctypes
	kernel32 = ctypes.windll.kernel32
	volumeNameBuffer = ctypes.create_unicode_buffer(1024)
	fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
	serial_number = None
	max_component_length = None
	file_system_flags = None
	drive_letters = get_drive_letters()
	rc = kernel32.GetVolumeInformationW(
		ctypes.c_wchar_p("F:\\"),
		volumeNameBuffer,
		ctypes.sizeof(volumeNameBuffer),
		serial_number,
		max_component_length,
		file_system_flags,
		fileSystemNameBuffer,
		ctypes.sizeof(fileSystemNameBuffer)
	)
	print(volumeNameBuffer.value)
	
def get_drive_letters():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter + ':\\')
        bitmask >>= 1
    return drives		
		
if __name__ == '__main__':
	main()
