from setuptools import setup
from setuptools import find_packages

import pkg_resources

try:
    pkg_resources.get_distribution('pypandoc')
except pkg_resources.DistributionNotFound:
    pypandocPresent = False
    print("Error: Pypandoc package not available.")
else:
    pypandocPresent = True
    import pypandoc


# Converts the Markdown README in the RST format that PyPi expects.
# Had some issues with pypandoc. Needed to install pandoc first.
# In the meantime, catch exceptions as follows:
if pypandocPresent == True:
	try:
		long_description = pypandoc.convert('README.md', 'rst')
	except (IOError, ImportError):
		print("README.md file could not be converted to produce a long description.")
		long_description = 'Not available.'
else:
	long_description = 'Not available.'
	
setup(name = 'epydemiology',
      packages = ['epydemiology'], # this must be the same as the name above
      # packages=find_packages(exclude=[list_of_things_to_exclude]),
      version = '0.1.29',
      description = 'A library of Python code for epidemiologists',
      long_description = long_description,
      author = 'Phil Jones',
      author_email = 'phjones@me.com',
      url = 'https://github.com/lvphj/epydemiology', # use the URL to the github repo
      download_url = 'https://github.com/lvphj/epydemiology/archive/0.1.29.tar.gz',
      license = 'MIT',
      keywords = ['database','epidemiology','case-control study','odds ratio','relative risk','risk ratio','proportions','confidence intervals','UK postcodes','disease trends'],
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
      install_requires=['numpy','pandas>=0.19.2','openpyxl'],
      )
