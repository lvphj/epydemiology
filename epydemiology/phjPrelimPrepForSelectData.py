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
#     |      1002 |      7324 |  yes |    a |  454 |  low |
#     |      1003 |      7324 |   no |    a |  454 |  low |
#     |      1004 |      7324 |   no |    a |  454 |  low |
