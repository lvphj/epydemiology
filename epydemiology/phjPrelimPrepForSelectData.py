import pkg_resources

try:
    pkg_resources.get_distribution('numpy')
except pkg_resources.DistributionNotFound:
    numpyPresent = False
    print("Error: Numpy package not available.")
else:
    numpyPresent = True
    import numpy as np


try:
    pkg_resources.get_distribution('pandas')
except pkg_resources.DistributionNotFound:
    pandasPresent = False
    print("Error: Pandas package not available.")
else:
    pandasPresent = True
    import pandas as pd


import collections
import re


from .phjMiscFuncs import phjGetStrFromArgOrFile
from .phjCleanData import phjParseDateVar



# The controls that are selected to go with cases could be either
# consultation controls (i.e. a random selection of consultations from
# any animals not represented in the cases dataset) or animal
# controls (i.e. a random selection of animals that are not represented in
# the case dataset). In the latter case, consultation-specific information
# will need to be collapsed over animal to produce animal-based information.

# It is assumed the cases and controls are stored in the same dataframe.
# The dataframe will have the following structure:
# 
# 
#     | consultID |       date | patientID | case | var1 | var2 | var3 |
#     |-----------|------------|-----------|------|------|------|------|
#     |      1001 | 2017-01-23 |      7324 |   no |    a |  454 |  low |
#     |      1002 | 2017-01-25 |      7324 |  yes |    b |  345 |  low |
#     |      1003 | 2017-01-29 |      7324 |   no |    c |  879 |  low |
#     |      1004 | 2017-02-05 |      9767 |  yes |    a |  276 |  mid |
#     |      1005 | 2017-02-11 |      9767 |  yes |    b |  478 |  mid |
#     |      1006 | 2017-02-28 |      3452 |   no |    c |  222 |  mid |
#     |      1007 | 2017-03-23 |      5322 |   no |    a |  590 |   hi |
#     |      1008 | 2017-03-23 |      5322 |  yes |    b |  235 |   hi |
#     |      1009 | 2017-04-02 |      5322 |  yes |    c |  657 |   hi |
#     etc.
# 
# 
# General workflow
# ----------------
# 1. IDENTIFY CASES
#    Download all (or partial) data from database and store in pandas dataframe.
#                |
#               \|/ 
#                V
# 2. Use screening regex to identify potential cases in whole – or partial – database
#                |
#               \|/ 
#                V
# 3. Manually read consultations of potenial cases and identify confirmed cases.
#    Record the consultation numbers and patient IDs of confirmed cases.
#                |
#               \|/ 
#                V
# 4. IDENTIFY POTENIAL CONTROLS
#    The potential controls may be drawn from a larger range of data than was used
#    to select the cases. As a result, it is important that the potential controls do not
#    include any consultations that would have been identified as cases had they been
#    included in the initial screening of cases.
#    Therefore, identify all consultations that would be identified as a potential CASE
#    using the screen regex.
#                |
#               \|/ 
#                V
# 5. Identify all patient IDs for consultations identified as confirmed cases
#                |
#               \|/ 
#                V
# 6. Identify all patient IDs from all consultations identified as potential cases
#    using the screening regex
#                |
#               \|/ 
#                V
# 7. Remove all consultations from potential case patients. The remaining consultations
#    are, therefore, potential cases.
#
# 
# 
# Selecting consultation controls
# -------------------------------
# The workflow that involves selecting a random sample of consultations
# from consultations not included in the cases and which would not have
# been selected as a case. 
# 
# 
def phjGetPotentialControls(phjTempDF,                    # A pandas dataframe containing all data from which controls can be selected. May also contain cases as well (these will be excluded).
                            phjCasesPatientIDSer = None,  # A pandas series containing patient ID for all confirmed cases
                            phjScreeningRegexStr = None,
                            phjScreeningRegexPathAndFileName = None,
                            phjConsultationIDVarName = None,
                            phjPatientIDVarName = None,
                            phjFreeTextVarName = None,
                            phjControlType = 'consultation',   # Other option would be 'patient'
                            phjPrintResults = False):
    ### THINGS TO CHECK
    ### phjPatientIDVarName is a string and not a list and that is contained in dataframe
    
    # Get regex used to screen for original potential cases
    phjScreeningRegex = phjGetRegexStr(phjRegexStr = phjScreeningRegexStr,
                                       phjRegexPathAndFileName = phjScreeningRegexPathAndFileName,
                                       phjPrintResults = phjPrintResults)
    
    if phjScreeningRegex is not None:
        # Compile regex
        phjRegex = re.compile(phjScreeningRegex,flags=re.I|re.X)
        
        # Run regex against freetext field and create a binary mask to identify all
        # consultations that match the regex
        phjRegexMask = phjTempDF[phjFreeTextVarName].str.contains(phjRegex)
        
        # Retrieve patient IDs for consultations where freetext field contains a match
        phjCasesPatientID = phjTempDF.loc[phjRegexMask,phjPatientIDVarName]
        
        # Combine with Patient IDs passed to function to produce an array of all
        # patient IDs that should not be included in potential control dataframe
        phjCasesPatientIDArr = phjCasesPatientID.append(phjCasesPatientIDSer).unique()
        
        # Create a mask of all patients that could be included in potentials control
        # list. (This is, in fact, the inverse of the output from .isin() method)
        phjControlConsultationsMask = ~phjTempDF[phjPatientIDVarName].isin(phjCasesPatientIDArr)
        
        # Use the mask to remove all cases patients from the dataframe
        # Only retain the consultation ID and the patient ID variables
        phjControlConsultationsDF = phjTempDF.loc[phjControlConsultationsMask,[phjConsultationIDVarName,phjPatientIDVarName]].reset_index(drop = True)
        
        if phjControlType == 'consultation':
            # Return the dataframe of patient IDs that have already been calculated
            phjPotentialControlsDF = phjControlConsultationsDF
            
        elif phjControlType == 'patient':
            # Need to consolidate based on patient ID.
            # Return dataframe consisting of patient ID and a variable giving the count
            # of the consultations
            phjPotentialControlsDF = phjControlConsultationsDF.groupby(phjPatientIDVarName).agg('count').rename(columns = {phjConsultationIDVarName:'consultation_count'}).reset_index(drop = False)
            
        else:
            print("Option entered for requested control type ('{0}') is not recognised.".format(phjControlType))
            phjPotentialControlsDF = None
    
    else:
        print('Could not identify the screening regex.')
        phjPotentialControlsDF = None
    
    
    return phjPotentialControlsDF



def phjGetRegexStr(phjRegexStr = None,
                   phjRegexPathAndFileName = None,
                   phjAllowedAttempts = 3,
                   phjPrintResults = False):
    
    phjTempRegex = phjGetStrFromArgOrFile(phjStr = phjRegexStr,
                                          phjPathAndFileName = phjRegexPathAndFileName,
                                          phjAllowedAttempts = phjAllowedAttempts,
                                          phjPrintResults = phjPrintResults)
    
    # Check whether regex string compiles
    if phjTempRegex is not None:
        try:
            re.compile(phjTempRegex)
        except re.error:
            print('The regex given did not compile.')
            phjTempRegex = None
    
    return phjTempRegex



def phjCollapseOnPatientID(phjAllDataDF,       # Dataframe containing all columns of data to be collapsed based on patient ID
                           phjConsultationIDVarName = None,
                           phjConsultationDateVarName = None,
                           phjPatientIDVarName = None,
                           phjFreeTextVarName = None,
                           phjAggDict = None,
                           phjPrintResults = False):
    
    # The phjAggDict will be assumed to be 'last' unless otherwise defined. Some examples are:
    # i.   'count'
    # ii.  lambda x: ' /// '.join(x.fillna('EMPTY FIELD'))   # concatenates fields separated by ' /// '
    # iii. ['first','last']                                  # finds first and last (and creates a multi-index)
    # iv.  lambda x:x.value_counts().index[0]                # Gets the most common (i.e. mode)
    # v.   np.sum
    # vi.  np.max
    # vii. np.min
    
    if phjConsultationDateVarName is not None:
        # Ensure date of consultation variable is in datetime format
        phjAllDataDF = phjParseDateVar(phjTempDF = phjAllDataDF,
                                       phjDateVarName = phjConsultationDateVarName,   # This can be a string or a list of variable names
                                       phjDateFormat = '%Y-%m-%d',
                                       phjMissingValue = 'missing',
                                       phjPrintResults = phjPrintResults)
    
    # Construct a dict for aggregating variables.
    # The consultation variable will be counted and the free text field will be concatenated.
    # Everything else will be concatenated by taking the last in the list unless otherwise defined
    # in the phjAggDict argument (in which case, the user-defined options will replace these
    # values). If the consultation date variable is defined, two columns will be produced,
    # one for the first consultation, one for the last.
    phjColList = phjAllDataDF.columns.values.tolist()
    phjColList = [c for c in phjColList if c != phjPatientIDVarName]
    phjCollapseAggDict = collections.OrderedDict((c,'last') for c in phjColList)   # This creates an ordered dict using a list comprehension-type syntax
    phjCollapseAggDict[phjConsultationIDVarName] = 'count'
    phjCollapseAggDict[phjConsultationDateVarName] = ['first','last']
    phjCollapseAggDict[phjFreeTextVarName] = lambda x: ' /// '.join(x.fillna('EMPTY FIELD'))
    
    # Update phjCollapseAggDict with the phjAggDict items supplied by user. The values in
    # phjAggDict will replace those in phjCollapseAggDict.
    if phjAggDict is not None:
        phjCollapseAggDict = phjCollapseAggDict.update(phjAggDict)
    
    # Sort data based on patient ID and date of consultation and groupby patient ID
    phjAllDataDF = phjAllDataDF.sort_values([phjPatientIDVarName,phjConsultationDateVarName],
                                            axis = 0,
                                            ascending = True).groupby(phjPatientIDVarName).agg(phjCollapseAggDict).reset_index(drop = False)
    
    # Flatten a column multi-index if there is one.
    # This will produce names of columns that are appended with agg function (e.g. '_last', '_<lambda>', etc.).
    # May decide to rename columns back to something more similar to original, bearing in
    # mind that simply removing some suffixes may leave multiple columns with the same name.

    phjAllDataDF.columns = ['_'.join(col).strip() for col in phjAllDataDF.columns.values]
    
    # If there is a column multi-index, the names of the columns will be named such as:
    # 'patient_', 'gender_last','freetext_<lambda>' etc. The following produces a dict
    # that will replace necessary column headings with something more readable. If there
    # is not a column multi-index, the headings will not require changing and the keys
    # in this dict will not match any columns and therefore no columns will be renamed.
    phjRenameDict = phjGetRenameCollapsedColumnsDict(phjPatientIDVarName = phjPatientIDVarName,
                                                     phjConsultationIDVarName = phjConsultationIDVarName,
                                                     phjAggDict = phjCollapseAggDict,
                                                     phjPrintResults = phjPrintResults)
    
    phjAllDataDF = phjAllDataDF.rename(columns = phjRenameDict)
    
    
    return phjAllDataDF



def phjGetRenameCollapsedColumnsDict(phjPatientIDVarName,
                                     phjConsultationIDVarName,
                                     phjAggDict,
                                     phjPrintResults = False):
    
    phjRenameDict = {}
    
    for k,v in phjAggDict.items():
        
        # In a column multi index, the patient ID column will be renamed from 'patientID'
        # to 'patientID_'. This dict entry will ensure the patient ID column is renamed.
        phjRenameDict[phjPatientIDVarName + '_'] = phjPatientIDVarName
        
        # If the agg functions is a list then will generate a multi-index and therefore do
        # not rename columns. If the column is the consultation ID then label with '_count'
        # suffix. For all other columns, rename the column back to the original.
        if not isinstance(v,list):
            
            # If the consultation ID variable is counted to indicate how many
            # consultations were present for each patient then the column will be
            # named 'consultID_count' (or something similar). In this version, the
            # column will be renamed with the same heading but it could be changed
            # in future by editing the following line.
            if (k == phjConsultationIDVarName) and (v == 'count'):
                phjRenameDict['_'.join([phjConsultationIDVarName,'count'])] = '_'.join([phjConsultationIDVarName,'count'])
            
            # If the aggregation process has involved a lambda function, the column
            # heading will be 'column1_<lambda>'. The column should be rename to not
            # included the '<lambda>' label.
            elif bool(re.search('<lambda>', str(v))):
                phjRenameDict[k + '_<lambda>'] = k
            
            # For other columns (which, for the most part, will be labelled as
            # 'column2_last') the columns should be renamed with just the original
            # column heading
            else:
                phjRenameDict['_'.join([k,str(v)])] = k
                
    if phjPrintResults == True:
        print('\nDictionary used to rename the dataframe columns:')
        print(phjRenameDict)
        print('\n')
    
    return phjRenameDict



