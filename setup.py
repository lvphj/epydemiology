from distutils.core import setup
setup(
    name = ‘epydemiology’,
    packages = [‘epydemiology’], # this must be the same as the name above
    version = ‘0.1.0’,
    description = ‘Python code for epidemiology’,
    long_description = ‘A library of Python functions for epidemiologist to select case-control datasets, calculate odds ratios and other features.’,
    author = ‘Phil Jones’,
    author_email = ‘phjones@me.com’,
    url = 'https://github.com/lvphj/epydemiology', # use the URL to the github repo
    download_url = 'https://github.com/lvphj/epydemiology/archive/0.1.0.tar.gz', # I'll explain this in a second
    license = ‘MIT’,
    keywords = [‘epidemiology’,’case-control study’,’odds ratio’,’relative risk’,’risk ratio’],
    classifiers = [# How mature is this project? Common values are
                   #   3 - Alpha
                   #   4 - Beta
                   #   5 - Production/Stable
                   'Development Status :: 3 - Alpha',
                   
                   # Indicate who your project is intended for
                   ‘Intended Audience :: Science/Research’,
                   ‘Topic :: Scientific/Engineering :: Medical Science Apps.’,
                   
                   # Pick your license as you wish (should match "license" above)
                   'License :: OSI Approved :: MIT License',
                   
                   # Specify the Python versions you support here. In particular, ensure
                   # that you indicate whether you support Python 2, Python 3 or both.
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.4',
                   ],
    packages=find_packages(exclude=None),
    install_requires=[‘pandas>=0.19.2’],
)