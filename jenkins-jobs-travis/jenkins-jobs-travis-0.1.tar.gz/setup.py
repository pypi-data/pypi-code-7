from setuptools import setup

setup(
    name='jenkins-jobs-travis',
    version='0.1',
    description='Jenkins Job Builder Travis YML Build Step',
    url='https://github.com/asmundg/jenkins-jobs-travis',
    author='Aasmund Grammeltvedt',
    author_email='asmundg@big-oil.org',
    license='MIT license',
    install_requires=[],
    entry_points={
        'jenkins_jobs.builders': [
            'travis = jenkins_jobs_travis.travis:travis']},
    packages=['jenkins_jobs_travis'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'])
