from setuptools import setup, find_packages
setup(
      name="cloudbackup",
      packages=[
          "cloudbackup",
          "cloudbackup.commands",
          "cloudbackup.drivers",
          "cloudbackup.drivers.s3",
          "cloudbackup.progressbar",
      ],
      entry_points={
          "console_scripts":[
              'cloudbackup = cloudbackup.commands:execute_from_command_line'
          ]
      },
      install_requires = ["boto"],
      version = "0.0.1",
      description="Upload/Restore stream from cloud storages.",
      author="Youta EGUSA",
      author_email="develop@chibiegg.net",
      url="https://github.com/chibiegg/cloudbackup",
      keywords=["s3"],
      classifiers=[
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 3",
                   ]
)

