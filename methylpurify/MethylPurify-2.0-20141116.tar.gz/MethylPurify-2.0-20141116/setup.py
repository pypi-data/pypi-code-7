"""
MethylPurify_v2
------------------

This script is used for predicting subclone purity.


Get Dependent data
````````````````````
Get the version of genome fasta that you mapped your fastqs, 
we support hg18 and hg19 genome fasta now, take hg19 as an example

.. code:: python
   
     ## use built-in script
     cd methylpurify/db
     bash genome.sh hg19


Get Dependent software
````````````````````````
* `samtools <http://samtools.sourceforge.net>`_, version 0.2.0
* `numpy <http://www.numpy.org>`_, version 1.8.2
* `pyfasta`, version 0.5.2

Easy to start 
`````````````````````
Input: BAM file, this should be mapped with BSMap with -R option
* `BSMap <https://code.google.com/p/bsmap/>`_

Currently, we only support hg19 and hg18 genome index mapped BAM file.

If your fastq mapping is done with hg19 index, use following command:

.. code:: python

      MethylPurify -f input.bam -b 300 -c 10 -s 50 -i methylpurify/db/CGI_hg19_slop1000.bed -g /path/to/hg19.fa --cnv


The results would be placed into *input* folder: alpha1.pred, MethylProfile.bed


Options
````````````````
* -f: input BAM file
* -c: coverage level
* -b: genome bin size
* -s: sampling times
* -g: species genome fasta file
* -i: CG island specified, can use methylpurify/db/CGI_hg19_slop1000.bed for hg19, methylpurify/db/CGI_hg18_slop1000.bed for hg18
* --cnv: use cnv data or not, only available for hg19, for other assembly, do not use this


"""

from setuptools import setup, find_packages


setup(
    name='MethylPurify',
    version='2.0',
    packages=find_packages(),
    url='',
##    license='MIT',
    author='Xiaoqi Zheng',
    author_email='zheng.shnu@gmail.com',
    description='Methylation subclone detection',
    long_description = __doc__,
    scripts = ['methylpurify/bin/MethylPurify'],
    install_requires=["pyfasta"],
    package_data = {"methylpurify" : ["db/*txt", "db/*bed", "db/genome.sh"]},
    keywords = "genomics methylation cancer",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ],
    )
