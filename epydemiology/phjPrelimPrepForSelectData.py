import numpy as np
import pandas as pd

# The controls that are selected to got with cases could be either
# consultation controls (i.e. a random selection of consultations from
# any animals not represented in the cases dataset) or animal
# controls (i.e. a random selection of animals that are not represented in
# the case dataset). In the latter case, consultation-specific information
# will need to be collapsed over animal to produce animal-based information.

# It is assumed the cases and controls are stored in the same dataframe.
# The dataframe will have the following structure:
# 
# 
#     | consultID | patientID | case | var1 | var2 | var3 |
#     |-----------|-----------|------|------|------|------|
#     |      1001 |      7324 |   no |    a |  454 |  low |
#     |      1002 |      7324 |  yes |    b |  345 |  low |
#     |      1003 |      7324 |   no |    c |  879 |  low |
#     |      1004 |      9767 |  yes |    a |  276 |  mid |
#     |      1005 |      9767 |  yes |    b |  478 |  mid |
#     |      1006 |      3452 |   no |    c |  222 |  mid |
#     |      1007 |      5322 |   no |    a |  590 |   hi |
#     |      1008 |      5322 |  yes |    b |  235 |   hi |
#     |      1009 |      5322 |  yes |    c |  657 |   hi |
#     etc.
#
# Selecting consultation controls
# -------------------------------
# The workflow that involves selecting 
# 
# 
