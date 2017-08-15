from setuptools import setup
from setuptools import find_packages
import pypandoc

# Converts the Markdown README in the RST format that PyPi expects.
# Had some issues with pypandoc. Needed to install pandoc first.
# In the meantime, catch exceptions as follows:
try:
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''

setup(name = 'epydemiology',
      packages = ['epydemiology'], # this must be the same as the name above
      # packages=find_packages(exclude=[list_of_things_to_exclude]),
      version = '0.1.20',
      description = 'A library of Python code for epidemiologists',
      long_description = long_description,
      author = 'Phil Jones',
      author_email = 'phjones@me.com',
      url = 'https://github.com/lvphj/epydemiology', # use the URL to the github repo
      download_url = 'https://github.com/lvphj/epydemiology/archive/0.1.20.tar.gz',
      license = 'MIT',
      keywords = ['database','mysql','epidemiology','case-control study','odds ratio','relative risk','risk ratio'],
      classifiers = [# How mature is this project? Common values are
                     #   3 - Alpha
                     #   4 - Beta
                     #   5 - Production/Stable
                     'Development Status :: 3 - Alpha',
                     
                     # Indicate who your project is intended for
                     'Intended Audience :: Science/Research',
                     'Topic :: Scientific/Engineering :: Medical Science Apps.',
                     
                     # Pick your license as you wish (should match "license" above)
                     'License :: OSI Approved :: MIT License',
                     
                     # Specify the Python versions you support here. In particular, ensure
                     # that you indicate whether you support Python 2, Python 3 or both.
                     'Programming Language :: Python :: 3',
                     'Programming Language :: Python :: 3.4'],
      install_requires=['numpy','pandas>=0.19.2','openpyxl','pymysql'],
      )
