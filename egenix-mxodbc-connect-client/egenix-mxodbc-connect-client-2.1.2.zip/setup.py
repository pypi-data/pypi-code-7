#!/usr/bin/env python

""" Distutils Setup File for the mxODBC Connect Client.

"""
#
# Run web installer, if needed
#
import mxSetup, os
mxSetup.run_web_installer(
    os.path.dirname(os.path.abspath(__file__)),
    landmarks=('mx', 'PREBUILT'))

#
# Load configuration(s)
#
import egenix_mxodbc_connect_client
configurations = (egenix_mxodbc_connect_client,)

#
# Run distutils setup...
#
import mxSetup
mxSetup.run_setup(configurations)
