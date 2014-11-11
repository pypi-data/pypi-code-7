# coding=utf-8

import sys
import os

def main():
	vep_core_dir = os.path.dirname(os.path.realpath(__file__))
	sys.path.append(vep_core_dir)
	sys.path.append(os.path.join(vep_core_dir, "Serendip"))
	sys.path.append(os.path.join(vep_core_dir, "Ity"))
	from Serendip import app
	app.run(threaded=True)

if __name__ == '__main__':
	main()