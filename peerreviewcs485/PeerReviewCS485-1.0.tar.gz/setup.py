import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
	name = "PeerReviewCS485",
	version = "1.0",
	packages = find_packages(),
	author = "CS 485",
	author_email = "b.k.bolte@emory.edu",
	description = "PeerReview Django app",
	url = "http://peerreview.readthedocs.org/en/latest/",
	include_package_data = True,
)
