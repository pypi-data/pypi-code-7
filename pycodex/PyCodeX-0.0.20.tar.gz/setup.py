from setuptools import setup

conf = {
    'name' : 'PyCodeX',
    'version' : '0.0.20',
    'description' : 'CodeX Python Libraries',
    'author' : 'Anthony De Leon',
    'author_email' : 'tonton.dev001@gmail.com',
    'url' : 'https://github.com/tontonskie/pycodex',
    'packages' : [
        'codex', 
        'codex.tornado',
        'codex.tornado.form'
    ],
    'package_dir' : {
        'codex' : 'codex',
        'codex.tornado' : 'codex/tornado',
        'codex.tornado.form' : 'codex/tornado/form'
    },
    'install_requires' : [
        'pytz',
        'tornado'
    ]
}

setup(**conf)
