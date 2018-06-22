
from distutils.core import setup

setup(
    name='CalFresh',
    version='1.0',
    author='Eric Day',
    author_email='ericday87@gmail.com',
    url='www.calfreshdb.org',
    packages=['calfresh'],
    license='MIT License',
    long_description=open('README.txt').read(),
    install_requires=[
        'BeautifulSoup4 >= 4.6.0',
        'editdistance == 0.1.4',
        'numpy >= 1.7.0',
        'openpyxl >= 2.4.7',
        'pandas >= 0.20.1',
        'requests >= 2.14.2',
        'xlrd >= 1.0.0',
    ],
)
