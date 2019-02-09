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
from .phjMiscFuncs import phjReadTextFromFile
from .phjCleanData import phjParseDateVar



# Primary functions
# =================

# The controls that are selected to go with cases could be either
# consultation controls (i.e. a random selection of consultations from
# any animals not represented in the cases dataset) or patient
# controls (i.e. a random selection of animals that are not represented in
# the case dataset). In the latter case, consultation-specific information
# needs to be collapsed on patient ID to produce patient-based information.

# It is assumed the cases and controls are stored in the same dataframe and
# that the data can be extracted using a suitable SQL query to produce a flat file
# dataframe. The dataframe will have the following structure:
# 
# 
#     | consultID |       date | patientID | match | freetext | var2 | var3 |
#     |-----------|------------|-----------|-------|----------|------|------|
#     |      1001 | 2017-01-23 |      7324 |  catA |        a |  454 |  low |
#     |      1002 | 2017-01-25 |      7324 |  catB |        b |  345 |  low |
#     |      1003 | 2017-01-29 |      7324 |  catA |        c |  879 |  low |
#     |      1004 | 2017-02-05 |      9767 |  catB |        a |  276 |  mid |
#     |      1005 | 2017-02-11 |      9767 |  catB |        b |  478 |  mid |
#     |      1006 | 2017-02-28 |      3452 |  catA |        c |  222 |  mid |
#     |      1007 | 2017-03-23 |      5322 |  catA |        a |  590 |   hi |
#     |      1008 | 2017-03-23 |      5322 |  catB |        b |  235 |   hi |
#     |      1009 | 2017-04-02 |      5322 |  catB |        c |  657 |   hi |
#     etc.
# 
# 
# General workflow
# ----------------
#
# These functions were written to streamline a commonly-encountered workflow in our
# research group. The following provides a brief description of the workflow used to
# analyse case-control datasets.
# 
# 1. IDENTIFY CASES
#    The first step is to identify cases within the data set.
#    • The whole database (or a partial excerpt) is downloaded and stored in a pandas
#      dataframe. The data set consists of consultation ID, date of consultation,
#      patient ID, freetext clinical narrative, variables to be used for matching (if
#      required) and any other variables of interest.
#    
#    • Potential cases are identified using a screen regex applied to the freetext
#      clinical narrative.
#    
#    • The researcher manually reads consultations of potenial cases to confirm that
#      they are cases. The consultation numbers of confirmed cases are recorded either
#      alone or as a slice of the dataframe.
# 
# 2. IDENTIFY POTENIAL CONTROLS
#    The potential controls may be drawn from a larger range of data than was used
#    to select the cases. As a result, it is important that the potential controls do not
#    include any consultations that would have been identified as cases had they been
#    included in the initial screening of cases.
#    
#    • Identify all consultations that would have been identified as a potential CASE
#      using the screen regex and identify the corresponding patient ID.
#    
#    • Identify all corresponding patient IDs for consultations identified as confirmed
#      cases.
#    
#    • Remove all consultations from confirmed and potential case patients (regardless of
#      whether the individual consultation was positive or negative. If a patient has one
#      consultation where the regex identifies a match, all consultations from that animal
#      should be excluded from the list of potential controls. The remaining consultations
#      are, therefore, potential cases.
# 
# 3. SELECT CONTROL DATASET
#    • Select suitable controls from the dataframe of potential controls, either
#      unmatched or matched on give variables. The controls can be either consultation
#      controls (where individual consultations are selected from the dataframe) or
#      patient controls (where patients are selected).
# 
#    • When selecting patient controls, it is necessary to collapse the consultation-based
#      dataframe down to a patient-based on patient ID. A default, a collapsed dataframe
#      will contain a 'count' variable to indicate how many consultations were recorded
#      for each patient, the dates of the first and last consultations, and the last
#      recorded entry for all other variables. This can, however, be altered as necessary.
# 
# 4. MERGE CASE-CONTROL DATASET WITH ORIGINAL DATAFRAMES
#    The initial selection of case control dataset returns and minimalist dataframe that
#    contains the bare minimum variables to be able to make the selection. After the
#    case-control dataframe has been selected, it is necessary to merge with the original
#    dataframe to return a complete dataset that contains all the original variables.
# 
# POINTS TO NOTE
# • Collapsing a consultation-based dataframe to a patient-based dataframe requires a
#   lot of computer processing that can be slow. As a result collapsing the
#   consultation-based dataframe to a patient-based dataframe is only
#   done after the controls have been selected; this ensures that only an minimal amount
#   of computer processing is required to collapse the dataset.
# 
# • The list of confirmed cases can be passed to the function either as a list (or series)
#   with not other variables, or as a dataframe which contains several variables, one of
#   which is the consultation ID or patient ID (depending on whether the required control
#   dataset consists of consultations or patients).
# 
# • Two dataframes need to be passed to the functions, one is a dataframe of 'ALL' data
#   (including all necessary variables) and the other is a dataframe (or series or list)
#   of confirmed cases. If the confirmed cases are all included in the dataframe of 'ALL'
#   data then the final returned dataset (containing all the necessary other variables of
#   interest) will be recreated from the dataframe of 'ALL' data. This means that any
#   edits included in the dataframe of confirmed cases will be lost in favour of
#   recreating the data from source. However, if the dataframe of cases contains some
#   consultations or patients that are not included in the original dataframe then the
#   returned dataframe will contain the data included in confirmed cases dataframe.
# 
# 
# Selecting consultation controls
# -------------------------------
# There are two main functions that can be used to create a case-control dataset:
# 1. phjSelectCaseControlDataset()
#    This function takes, as arguments, two dataframes, one of confirmed cases and the
#    other of potential controls. It then returns a 'skeleton' dataframe containing the
#    minimal number of variables (e.g. ID, case/control and group membership (if a
#    matched control set was required). It will be necessary to merge this skeleton with
#    appropriate dataframes to produce a complete case-control dataset that contains all
#    the necessary variables required for further analysis.
# 
# 2. phjGenerateCaseControlDataset()
#    This function ultimates calls the phjSelectCaseControlDataset() function but it
#    also attempts to automate a large proportion of the required pre- and post-
#    production faffing around. For example, the function will determine whether a
#    consultation-based or patient-based dataset is required, it will generate the
#    dataframe of potential controls automatically and will merge the skeleton dataframe
#    returned by phjSelectCaseControlDataset() function to produce a dataframe that is
#    complete with all the variables that were included in the original dataframes.
# 
# 
# Passing suitable case data
# --------------------------
# The function should be passed a full dataframe containing 'ALL' the data. In fact, some
# of the confirmed cases need not be included in the dataframe of 'ALL' data (but there
# some limitations if this is the case). The requested case-control dataset can be either
# 'consultation-based' or 'patient-based'. In each of these cases, the confirmed cases
# can be passed in one of several formats (but, in some situations, returning a valid
# case-control dataset may not be feasible).
# 
# 1. Consultation-based dataset requested
#    ====================================
#    • Cases passed as a SERIES of consultation ID numbers, all of which are included in
#      the dataframe of 'ALL' data.
#      – SUCCESS. Returned dataframe will contain variables reconstructed from 'ALL' data.
# 
#    • Cases passed as a SERIES of consultation ID numbers, some of which are not included
#      in the dataframe of 'ALL' data.
#      – FAILED. Required variables missing for some cases.
# 
#    • Cases passed as a DATAFRAME containing several variables, one of which is the
#      CONSULTATION ID and all consultations are a subset of the consultations
#      in the dataframe of 'ALL' data.
#      – SUCCESS
# 
#    • Cases passed as a DATAFRAME containing several variables, one of which is the
#      CONSULTATION ID but not all consultations are included in the dataframe of 'ALL' data.
#      – FAILED
 
#    • Cases passed as a DATAFRAME containing all the same variables as included in the
#      'ALL' dataframe. Not all consultations are included in the dataframe of 'ALL' data.
#      – SUCCESS
# 
# 2. Patient-based dataset requested
#    ===============================
#    • Cases passed as a SERIES of case PATIENT IDs that are a subset of the information
#      in the dataframe of 'ALL' data.
#      – SUCCESS
# 
#    • Cases passed as a SERIES of case PATIENT IDs that are NOT a subset of the
#      information in the dataframe of 'ALL' data (e.g. there may be extra rows).
#      – FAILED
# 
#    • Cases passed as a DATAFRAME containing several variables, one of which is the
#      PATIENT ID and all patients are a subset of the patients in the dataframe of
#      'ALL' data.
#      – SUCCESS
# 
#    • Cases passed as a DATAFRAME containing several variables, one of which is the
#      PATIENT ID but not all patients are a subset of the patients in the dataframe of
#      'ALL' data.
#      – FAILED
# 
#    • Cases passed as a DATAFRAME containing numerous variables, one of which is the
#      PATIENT ID and all patients are a subset of the patients
#      in the dataframe of 'ALL' data. The variables are the same as those
#      that will be produced when the consultation dataframe is collapsed
#      based on patient ID data.
#      – SUCCESS
# 
#    • Cases passed as a DATAFRAME containing numerous variables, one of which is the
#      PATIENT ID but the patients are NOT a subset of the patients
#      in the dataframe of 'ALL' data. The variables are the same as those
#      that will be produced when the consultation dataframe is collapsed
#      based on patient ID data.
#      – SUCCESS



# The following function attempts to automate the selection of case-control datasets.
def phjGenerateCaseControlDataset(phjAllDataDF,             # A dataframe containing all variables. Controls will be drawn from this dataframe. Cases may – or may not – be included as well.
                                  phjPatientIDVarName,
                                  phjConsultationIDVarName,
                                  phjConsultationDateVarName,
                                  phjFreeTextVarName,
                                  phjCasesDF,               # A dataframe containing all confirmed cases. If not included in phjAllDataDF then needs to contain all variables for analysis as well (with columns having the same names as in phjAllDataDF).
                                  phjMatchingVariablesList = None,   # Needs to be a list - but in future allow for just a string
                                  phjControlsPerCaseInt = 1,
                                  phjScreeningRegexStr = None,
                                  phjScreeningRegexPathAndFileName = None,
                                  phjControlType = 'consultation',   # The only other option would be 'patient'
                                  phjAggDict = None,
                                  phjPrintResults = False):
    
    try:
        # 1. Check whether entered parameters have been set to the correct type
        assert isinstance(phjAllDataDF,pd.DataFrame), "Parameter 'phjAllDataDF' needs to be a Pandas dataframe."
        assert isinstance(phjPatientIDVarName,str), "Parameter 'phjPatientIDVarName' needs to be a string."
        assert isinstance(phjConsultationIDVarName,str), "Parameter 'phjConsultationIDVarName' needs to be a string."
        assert isinstance(phjConsultationDateVarName,str), "Parameter 'phjConsultationDateVarName' needs to be a string."
        assert isinstance(phjFreeTextVarName,str), "Parameter 'phjFreeTextVarName' needs to be a string."
        assert isinstance(phjCasesDF,pd.DataFrame), "Parameter 'phjCasesDF' needs to be a Pandas dataframe."
        
        if phjMatchingVariablesList is not None:
            assert isinstance(phjMatchingVariablesList,(list,str)), "Parameter 'phjMatchingVariablesList' needs to be a string of a single column heading or a list of column headings."
        
        assert isinstance(phjControlsPerCaseInt,int), "Parameter 'phjControlsPerCaseInt' needs to be an integer."
        
        if phjScreeningRegexStr is not None:
            assert isinstance(phjScreeningRegexStr,str), "Parameter 'phjScreeningRegexStr' needs to be a string."
        
        if phjScreeningRegexPathAndFileName is not None:
            assert isinstance(phjScreeningRegexPathAndFileName,str), "Parameter 'phjScreeningRegexPathAndFileName' needs to be a string."
        
        assert phjControlType in ['consultation','patient'], "Parameter 'phjControlType' can only take the value 'consultation' or 'patient'. The value '{0}' is not recognised.".format(phjControlType)
        
        if phjAggDict is not None:
            assert isinstance(phjAggDict,dict), "Parameter phjAggDict needs to be a dictionary."
            # N.B. Other checks on the contents of phjAggDict are done in the phjCollapseOnPatientID() function
        
        assert isinstance(phjPrintResults,bool), "Parameter 'phjPrintResults' needs to be a boolean (True, False) value."
        
        
        # 2. Check whether entered parameters have been set to an appropriate value
        assert phjControlType in ['consultation','patient'], "Parameter 'phjControlType' can only take the value 'consultation' or 'patient'. The value '{0}' is not recognised.".format(phjControlType)
        
        # If phjMatchingVariablesList is not None then it must be a str or a list (as checked
        # previously). If it is a list, check that none of the elements is None.
        if phjMatchingVariablesList is not None:
            if isinstance(phjMatchingVariablesList,list):
                # Check if any items in matching variables list is None
                assert None not in phjMatchingVariablesList, "List of matching variables cannot contain None values."
        
        
        # 3. Check that columns that are referenced by parameters do exist and that new
        #    columns that will be created don't already exist
        
        # Create lists of all columns that need to be present and need to be absent in
        # different scenarios.
        
        # If the control type is 'consultation' or 'patient' then the required columns in the
        # dataframe containing ALL the data are:
        #   i. consultation ID variable name
        #  ii. patient ID variable name
        # iii. freetext field
        #  iv. consultation date
        #   v. matching variables (if required)
        
        # Dictionary of required variables (excluding matching variables) when
        # desired control type is 'consultation'.
        phjBaselineVarsDict = {'phjConsultationIDVarName':phjConsultationIDVarName,
                               'phjPatientIDVarName':phjPatientIDVarName,
                               'phjFreeTextVarName':phjFreeTextVarName,
                               'phjConsultationDateVarName':phjConsultationDateVarName}
        
        if phjMatchingVariablesList is not None:
            if isinstance(phjMatchingVariablesList,list):
                phjColumnsPresentList = list(phjBaselineVarsDict.values()) + phjMatchingVariablesList
                
            elif isinstance(phjMatchingVariablesList,str):
                phjColumnsPresentList = list(phjBaselineVarsDict.values()) + [phjMatchingVariablesList]
            
            # If control type is 'consultation' then matched case-control dataframes will create
            # columns called 'case' and 'group'; if control type is 'patient' then will also
            # need to create a column called 'count'.
            if phjControlType == 'consultation':
                phjColumnsAbsentList = ['case','group']
            
            elif phjControlType == 'patient':
                phjColumnsAbsentList = ['case','group','count']
        
        else:
            # i.e. list of matching variables is None
            phjColumnsPresentList = list(phjBaselineVarsDict.values())
            phjColumnsAbsentList = None
        
        # Check that all the required columns are present or absent from the
        # complete dataframe containing ALL the data.
        assert phjCheckColumns(phjDF = phjAllDataDF,
                               phjDFDescriptorStr = 'all_data',
                               phjColumnsPresentList = phjColumnsPresentList,
                               phjColumnsAbsentList = phjColumnsAbsentList,
                               phjPrintResults = phjPrintResults), "Parameter check for column headings has failed. Not all required variables are appropriately contained in the dataframe."
    
    
    except AssertionError as e:
        print ("An AssertionError has occurred. ({0})".format(e))
        
        phjCaseControlDF = None
        
    else:
        
        
        ###############################################################################
        ### STEPS 1 and 2                                                           ###
        ### =============                                                           ###
        ### Get appropriate dataframes of verified cases and potential controls     ###
        ### and produce a case-control dataframe containing only minimal variables. ###
        ###############################################################################
        
        #############################################
        ### CONSULTATION-BASED CASE-CONTROL STUDY ###
        #############################################
        if phjControlType == 'consultation':
            
            # STEP 1: Get dataframes of verified cases and potential controls
            # ===============================================================
            phjVerifiedCasesDF = phjGetVerifiedConsultationCases(phjAllDataDF = phjAllDataDF,
                                                                 phjCasesDF = phjCasesDF,   # Can be a dataframe ideally but could also be a series, array or list but, based on initial checks, anything other than a dataframe will cause an AssertionError.
                                                                 phjConsultationIDVarName = phjConsultationIDVarName,   # Either consultation ID or patient ID depending on control type
                                                                 phjPrintResults = phjPrintResults)
            
            if phjVerifiedCasesDF is not None:
                
                # Define which columns to keep in the dataframe for preliminary analysis
                phjRequiredColumnsList = phjColumnsPresentList
                phjRequiredColumnsList.remove(phjFreeTextVarName)
                
                phjPotentialControlsDF = phjGetPotentialControls(phjDF = phjAllDataDF,   # A pandas dataframe containing all data from which controls can be selected. May also contain cases as well (these will be excluded).
                                                                 phjCasesPatientIDSer = phjVerifiedCasesDF[phjPatientIDVarName],   # A pandas series containing patient ID for all confirmed cases
                                                                 phjScreeningRegexStr = phjScreeningRegexStr,
                                                                 phjScreeningRegexPathAndFileName = phjScreeningRegexPathAndFileName,
                                                                 phjConsultationIDVarName = phjConsultationIDVarName,
                                                                 phjConsultationDateVarName = phjConsultationDateVarName,
                                                                 phjPatientIDVarName = phjPatientIDVarName,
                                                                 phjRequiredColumnsList = phjRequiredColumnsList,   # Required columns that are needed to run the case-control functions (minus the freetext field)
                                                                 phjFreeTextVarName = phjFreeTextVarName,
                                                                 phjControlType = 'consultation',   # Other option would be 'patient'
                                                                 phjAggDict = phjAggDict,
                                                                 phjPrintResults = phjPrintResults)
            
            else:
                phjPotentialControlsDF = None
            
            # At this point, should have dataframes of verified cases and potential controls
            if phjPrintResults == True:
                print("\nphjVerifiedCasesDF")
                print(phjVerifiedCasesDF)
                print("\nphjPotentialControlsDF")
                print(phjPotentialControlsDF)
            
            
            # STEP 2: Get an appropriate dataframe of case-control subjects
            # =============================================================
            if (phjVerifiedCasesDF is not None) and (phjPotentialControlsDF is not None):
                
                # Get a skeleton case-control dataset
                phjSkeletonCaseControlDF = phjSelectCaseControlDataset(phjCasesDF = phjVerifiedCasesDF,
                                                                       phjPotentialControlsDF = phjPotentialControlsDF,
                                                                       phjUniqueIdentifierVarName = phjConsultationIDVarName,
                                                                       phjMatchingVariablesList = phjMatchingVariablesList,
                                                                       phjControlsPerCaseInt = phjControlsPerCaseInt,
                                                                       phjPrintResults = phjPrintResults)
            
            else:
                phjSkeletonCaseControlDF = None
        
        
        ########################################
        ### PATIENT-BASED CASE-CONTROL STUDY ###
        #########################################
        elif phjControlType == 'patient':
            
            # STEP 1: Get dataframes of verified cases and potential controls
            # ===============================================================
            phjVerifiedCasesDF = phjGetVerifiedPatientCases(phjAllDataDF = phjAllDataDF,
                                                            phjCasesDF = phjCasesDF,   # Can be a dataframe ideally but could also be a series, array or list.
                                                            phjConsultationIDVarName = phjConsultationIDVarName,
                                                            phjConsultationDateVarName = phjConsultationDateVarName,
                                                            phjPatientIDVarName = phjPatientIDVarName,
                                                            phjFreeTextVarName = phjFreeTextVarName,
                                                            phjAggDict = phjAggDict,
                                                            phjPrintResults = phjPrintResults)
            
            if phjVerifiedCasesDF is not None:
                # Define which columns to keep in the dataframe for preliminary analysis
                phjRequiredColumnsList = phjColumnsPresentList
                phjRequiredColumnsList.remove(phjFreeTextVarName)
                
                phjPotentialControlsDF = phjGetPotentialControls(phjDF = phjAllDataDF,   # A pandas dataframe containing all data from which controls can be selected. May also contain cases as well (these will be excluded).
                                                                 phjCasesPatientIDSer = phjVerifiedCasesDF[phjPatientIDVarName],   # A pandas series containing patient ID for all confirmed cases
                                                                 phjScreeningRegexStr = phjScreeningRegexStr,
                                                                 phjScreeningRegexPathAndFileName = phjScreeningRegexPathAndFileName,
                                                                 phjConsultationIDVarName = phjConsultationIDVarName,
                                                                 phjConsultationDateVarName = phjConsultationDateVarName,
                                                                 phjPatientIDVarName = phjPatientIDVarName,
                                                                 phjRequiredColumnsList = phjRequiredColumnsList,   # Required columns that are needed to run the case-control functions (minus the freetext field)
                                                                 phjFreeTextVarName = phjFreeTextVarName,
                                                                 phjControlType = 'patient',
                                                                 phjAggDict = phjAggDict,
                                                                 phjPrintResults = phjPrintResults)
            
            
            else:
                # Otherwise phjVerifiedCasesDF is None
                phjPotentialControlsDF = None
            
            # At this point, should have dataframes of verified cases and potential controls
            if phjPrintResults == True:
                print("\nphjVerifiedCasesDF")
                print(phjVerifiedCasesDF)
                print("\nphjPotentialControlsDF")
                print(phjPotentialControlsDF)
            
            
            # STEP 2: Get an appropriate dataframe of case-control subjects
            # =============================================================
            if (phjVerifiedCasesDF is not None) and (phjPotentialControlsDF is not None):
                
                # Get a skeleton case-control dataset
                # (i.e. a dataset containing just be bare minimum variables, for example
                #       unique identifier, case, group and matching variables.)
                phjSkeletonCaseControlDF = phjSelectCaseControlDataset(phjCasesDF = phjVerifiedCasesDF,
                                                                       phjPotentialControlsDF = phjPotentialControlsDF,
                                                                       phjUniqueIdentifierVarName = phjPatientIDVarName,
                                                                       phjMatchingVariablesList = phjMatchingVariablesList,
                                                                       phjControlsPerCaseInt = phjControlsPerCaseInt,
                                                                       phjPrintResults = phjPrintResults)
            
            else:
                phjSkeletonCaseControlDF = None
        
        
        # Print skeleton case-control dataset
        if phjPrintResults == True:
            print("\nSkeleton case-control dataset")
            print(phjSkeletonCaseControlDF)
        
        
        ############################################################################################
        ### STEP 3                                                                               ###
        ### ======                                                                               ###
        ### Join skeleton case-control dataframe with full dataframe(s) to retrieve all columns. ###
        ############################################################################################
        
        if phjSkeletonCaseControlDF is not None:
            
            if phjControlType == 'consultation':
                
                # There are several options available when joining the minimal case-control
                # study data with dataframe containing the full set of variables.
                #  i. If all the consultations are included in the full dataset then use
                #     the full dataframe to recreate the case-control dataset with all
                #     variables.
                # ii. If the consultations are not included in the full dataset and the
                #     columns in the cases DF are the same as the columns in the full
                #     dataset then recreate the case-control dataset with all variables
                #     (i.e. the same as above for now but could change in the future).
                
                # Get list of columns from the skeleton case control dataframe
                phjSkeletonCaseControlColumnsList = [c for c in phjSkeletonCaseControlDF.columns.values if c in [phjConsultationIDVarName,'group','case']]
                
                if set(phjSkeletonCaseControlDF[phjConsultationIDVarName]).issubset(phjAllDataDF[phjConsultationIDVarName]):
                    # Both the following if...else statements do the same thing; kept separate
                    # to allow for the option to merge with separate dataframes in future.
                    # For example, if the cases are a subset of the main dataset and the
                    # columns in the cases dataframe are the same, it may be desirable to
                    # merge with the cases dataframe (which may have updated or different
                    # content) rather than merge with the overall dataframe.
                    if set(phjVerifiedCasesDF.columns.values) == set(phjAllDataDF.columns.values):
                        phjCaseControlDF = phjSkeletonCaseControlDF[phjSkeletonCaseControlColumnsList].merge(phjAllDataDF,
                                                                                                             on = phjConsultationIDVarName,
                                                                                                             how = 'left')
                    
                    else:
                        phjCaseControlDF = phjSkeletonCaseControlDF[phjSkeletonCaseControlColumnsList].merge(phjAllDataDF,
                                                                                                             on = phjConsultationIDVarName,
                                                                                                             how = 'left')
                
                else:
                    # If list of case consultations is NOT a subset of the full dataset
                    # then it is necessary that all variables/columns are retrieved from
                    # the phjVerifiedCasesDF for the cases and from the phjAllDataDF for
                    # the controls.
                    if set(phjVerifiedCasesDF.columns.values) == set(phjAllDataDF.columns.values):
                        
                        phjGroupsList = []
                        
                        phjTempCaseControlGroups = phjSkeletonCaseControlDF.groupby('case')
                        for name, group in phjTempCaseControlGroups:
                            if name == 1:
                                group = group[phjSkeletonCaseControlColumnsList].merge(phjVerifiedCasesDF,
                                                                                       on = phjConsultationIDVarName,
                                                                                       how = 'left')
                            elif name == 0:
                                group = group[phjSkeletonCaseControlColumnsList].merge(phjAllDataDF,
                                                                                       on = phjConsultationIDVarName,
                                                                                       how = 'left')
                            
                            phjGroupsList.append(group)
                        
                        phjCaseControlDF = pd.concat(phjGroupsList)
                    
                    else:
                        print("\nThe cases are not a subset of all the data and the two dataframes do not contain the same columns. Therefore, verified cases cannot be identified.")
                        phjCaseControlDF = None
            
            
            elif phjControlType == 'patient':
                
                # Get a list of all column headings that will be included in a dataframe
                # of patients that is created by collapsing the consultation data
                # on patient ID (except 'case' and 'group' column headings)
                phjPatientColumnsList = phjGetCollapsedPatientDataframeColumns(phjAllDataDF = phjAllDataDF,
                                                                               phjConsultationIDVarName = phjConsultationIDVarName,
                                                                               phjConsultationDateVarName = phjConsultationDateVarName,
                                                                               phjPatientIDVarName = phjPatientIDVarName,
                                                                               phjFreeTextVarName = phjFreeTextVarName,
                                                                               phjAggDict = phjAggDict,
                                                                               phjPrintResults = phjPrintResults)
                
                # Columns 'case' and 'group' shouldn't be present but just to make sure...
                phjPatientColumnsList = [c for c in phjPatientColumnsList if c not in ['case','group']]
                
                
                # Get a list of the required column headings from the skeleton dataframe.
                # Only the patient ID, case and group variables need to be retained
                # from the left-hand dataframe before being joined to the right-hand
                # dataframe. But the 'group' variable may not be included if the requested
                # case-control dataset is unmatched. Therefore, create a list of
                # columns to include in the left-hand dataframe.
                phjSkeletonCaseControlColumnsList = [c for c in phjSkeletonCaseControlDF.columns.values if c in [phjPatientIDVarName,'group','case']]
                
                
                if set(phjSkeletonCaseControlDF[phjPatientIDVarName]).issubset(phjAllDataDF[phjPatientIDVarName]):
                    # Both the following if...else statements do the same thing; kept separate
                    # to allow for the option to merge with separate dataframes in future
                    # (as discussed above).
                    if set(phjVerifiedCasesDF.columns.values) == set(phjPatientColumnsList):
                        # Get a list of all the patient IDs that have been included in the minimal
                        # case-control dataframe. This will be used to create a mask that can be used
                        # to extract all the required rows of data from the dataframe of all data,
                        # either all the consultations belonging to the patients or all the summary
                        # data collapsed based on patient ID.
                        phjTempPatientMask = phjAllDataDF[phjPatientIDVarName].isin(phjSkeletonCaseControlDF[phjPatientIDVarName])
                        phjTempIncludedPatientsDF = phjAllDataDF.loc[phjTempPatientMask,:]
                        
                        phjTempIncludedPatientsDF = phjCollapseOnPatientID(phjAllDataDF = phjTempIncludedPatientsDF,
                                                                           phjPatientIDVarName = phjPatientIDVarName,
                                                                           phjConsultationIDVarName = phjConsultationIDVarName,
                                                                           phjConsultationDateVarName = phjConsultationDateVarName,
                                                                           phjFreeTextVarName = phjFreeTextVarName,
                                                                           phjAggDict = phjAggDict,
                                                                           phjPrintResults = phjPrintResults)
                        
                        phjCaseControlDF = phjSkeletonCaseControlDF[phjSkeletonCaseControlColumnsList].merge(phjTempIncludedPatientsDF,
                                                                                                             on = phjPatientIDVarName,
                                                                                                             how = 'left')
                    
                    else:
                        # Otherwise, the columns in cases dataframe are NOT the same as
                        # the columns in the patients dataframe; in which case, do
                        # exactly the same as above. For now at least.
                        phjTempPatientMask = phjAllDataDF[phjPatientIDVarName].isin(phjSkeletonCaseControlDF[phjPatientIDVarName])
                        phjTempIncludedPatientsDF = phjAllDataDF.loc[phjTempPatientMask,:]
                        
                        phjTempIncludedPatientsDF = phjCollapseOnPatientID(phjAllDataDF = phjTempIncludedPatientsDF,
                                                                           phjPatientIDVarName = phjPatientIDVarName,
                                                                           phjConsultationIDVarName = phjConsultationIDVarName,
                                                                           phjConsultationDateVarName = phjConsultationDateVarName,
                                                                           phjFreeTextVarName = phjFreeTextVarName,
                                                                           phjAggDict = phjAggDict,
                                                                           phjPrintResults = phjPrintResults)
                        
                        phjCaseControlDF = phjSkeletonCaseControlDF[phjSkeletonCaseControlColumnsList].merge(phjTempIncludedPatientsDF,
                                                                                                             on = phjPatientIDVarName,
                                                                                                             how = 'left')
                
                else:
                    # Otherwise, patients in the skeleton case-control dataset are not
                    # a subset of the patients included in the full dataset.
                    
                    # If the columns in the cases dataframe and the collapsed dataframe
                    # are the same then can merge cases with the originally supplied
                    # cases dataframe and the controls with the collapsed dataframe.
                    if set(phjVerifiedCasesDF.columns.values) == set(phjPatientColumnsList):
                        
                        # Create a dataframe of patients (collapsed on patient ID) for
                        # selected controls only (the cases will be matched with the original
                        # dataframe of cases).
                        phjTempPatientMask = phjAllDataDF[phjPatientIDVarName].isin(phjSkeletonCaseControlDF.loc[phjSkeletonCaseControlDF['case'] == 0,
                                                                                                                 phjPatientIDVarName])
                        phjTempIncludedPatientsDF = phjAllDataDF.loc[phjTempPatientMask,:]
                        
                        phjTempIncludedPatientsDF = phjCollapseOnPatientID(phjAllDataDF = phjTempIncludedPatientsDF,
                                                                           phjPatientIDVarName = phjPatientIDVarName,
                                                                           phjConsultationIDVarName = phjConsultationIDVarName,
                                                                           phjConsultationDateVarName = phjConsultationDateVarName,
                                                                           phjFreeTextVarName = phjFreeTextVarName,
                                                                           phjAggDict = phjAggDict,
                                                                           phjPrintResults = phjPrintResults)
                        
                        phjGroupsList = []
                        
                        phjTempCaseControlGroups = phjSkeletonCaseControlDF.groupby('case')
                        for name, group in phjTempCaseControlGroups:
                            if name == 1:
                                group = group[phjSkeletonCaseControlColumnsList].merge(phjVerifiedCasesDF,
                                                                                       on = phjPatientIDVarName,
                                                                                       how = 'left')
                            elif name == 0:
                                group = group[phjSkeletonCaseControlColumnsList].merge(phjTempIncludedPatientsDF,
                                                                                       on = phjPatientIDVarName,
                                                                                       how = 'left')
                            
                            phjGroupsList.append(group)
                    
                        phjCaseControlDF = pd.concat(phjGroupsList)
                
                
                    else:
                        print("\nThe cases are not a subset of all the data and the two dataframes do not contain the same columns. Therefore, verified cases cannot be identified.")
                        phjCaseControlDF = None
        
            else:
                # phjControlType is neither 'consultation' nor 'patient'.
                # Nothing should reach this point because unrecognised control type
                # should have been filtered out long ago. But hey.
                print("\nRequested control type ('{0}') is not recognised.".format(phjControlType))
                phjCaseControlDF = None
    
        else:
            # Otherwise, skeleton case-control dataframe is None
            print("\nA case-control dataset could not be created.")
            phjCaseControlDF = None
    
    
        if phjPrintResults == True:
            print("\nFull case-control dataframe")
            print(phjCaseControlDF)
    
    
    return phjCaseControlDF



def phjSelectCaseControlDataset(phjCasesDF,
                                phjPotentialControlsDF,
                                phjUniqueIdentifierVarName,
                                phjMatchingVariablesList = None,
                                phjControlsPerCaseInt = 1,
                                phjPrintResults = False):
    
    # Print summary of parameters passed to function
    # ==============================================
    if phjPrintResults == True:
        print('\n*** WARNING: Setting phjPrintResults to True causes a lot of output   ***')
        print('*** to be printed. With Jupyter-Notebook, this seems to be associated ***')
        print('*** with losing connection with the kernel and, as such, may cause    ***')
        print('*** the function to not complete correctly.                           ***')
        
        print('\nSummary of parameters passed to phjSelectCaseControlDataset() function')
        print('======================================================================')
        with pd.option_context('display.max_rows', 6, 'display.max_columns', 6):
            print('\nCASES\n-----')
            print(phjCasesDF)
            print('\nPOTENTIAL CONTROLS\n------------------\n')
            print(phjPotentialControlsDF)
        print('Unique identifier variable = ', phjUniqueIdentifierVarName)
        print('Number of controls to be selected per case = ',phjControlsPerCaseInt)
        print('Variables to match = ',phjMatchingVariablesList)
        
        print('Number of potential controls = ',len(phjPotentialControlsDF.index))
        
        
    # Check on parameters passed to functions and, if OK, select datasets
    # ===================================================================
    # Run function phjParameterCheck() to make sure parameters passed to function make
    # sense. If the phjParameterCheck() function returns True then go ahead and create
    # case-control dataset. If returns False then return None.
    if phjParameterCheck(phjCasesDF = phjCasesDF,
                         phjPotentialControlsDF = phjPotentialControlsDF,
                         phjUniqueIdentifierVarName = phjUniqueIdentifierVarName,
                         phjMatchingVariablesList = phjMatchingVariablesList,
                         phjControlsPerCaseInt = phjControlsPerCaseInt):
        
        if phjMatchingVariablesList is None:
            # Select UNMATCHED controls
            phjTempCaseControlDF = phjSelectUnmatchedCaseControlSubjects(phjCasesDF = phjCasesDF,
                                                                         phjPotentialControlsDF = phjPotentialControlsDF,
                                                                         phjUniqueIdentifierVarName = phjUniqueIdentifierVarName,
                                                                         phjMatchingVariablesList = phjMatchingVariablesList,
                                                                         phjControlsPerCaseInt = phjControlsPerCaseInt,
                                                                         phjPrintResults = phjPrintResults)
        
        else:
            # Select MATCHED controls
            phjTempCaseControlDF = phjSelectMatchedCaseControlSubjects( phjCasesDF = phjCasesDF,
                                                                        phjPotentialControlsDF = phjPotentialControlsDF,
                                                                        phjUniqueIdentifierVarName = phjUniqueIdentifierVarName,
                                                                        phjMatchingVariablesList = phjMatchingVariablesList,
                                                                        phjControlsPerCaseInt = phjControlsPerCaseInt,
                                                                        phjPrintResults = phjPrintResults)
    
    else:
        # If phjParameterCheck() returns False then return None from this function
        phjTempCaseControlDF = None
    
    
    return phjTempCaseControlDF



def phjCollapseOnPatientID(phjAllDataDF,       # Dataframe containing all columns of data to be collapsed based on patient ID
                           phjPatientIDVarName,
                           phjConsultationIDVarName = None,
                           phjConsultationDateVarName = None,
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
    
    
    # Need to check that:
    # phjAllDataDF is a dataframe.
    # phjPatientIDVarName is a string that is contained in the dataframe
    # Check that phjPatientIDVarName is NOT included in the phjAggDict. 
    # Check that other variables are also contained in the dataframe.
    
    
    try:
        # 1. Check whether entered parameters have been set to the correct type:
        assert isinstance(phjAllDataDF,pd.DataFrame), "Parameter 'phjAllDataDF' needs to be a Pandas dataframe."
        assert isinstance(phjPatientIDVarName,str), "Parameter 'phjPatientIDVarName' needs to be a string."
        
        if phjConsultationIDVarName is not None:
            assert isinstance(phjConsultationIDVarName,str), "Parameter 'phjConsultationIDVarName' needs to be a string."
        
        if phjConsultationDateVarName is not None:
            assert isinstance(phjConsultationDateVarName,str), "Parameter 'phjConsultationDateVarName' needs to be a string."
        
        if phjFreeTextVarName is not None:
            assert isinstance(phjFreeTextVarName,str), "Parameter 'phjFreeTextVarName' needs to be a string."
        
        if phjAggDict is not None:
            assert isinstance(phjAggDict,dict), "Parameter phjAggDict needs to be a dictionary."
            
        assert isinstance(phjPrintResults,bool), "Parameter 'phjPrintResults' needs to be a boolean (True, False) value."
        
        # 2. Check whether entered parameters have been set to an appropriate value
        # None
        
        # 3. Check that columns that are referenced by parameters do exist and that new
        #    columns that will be created don't already exist
        phjFullColumnsList = phjAllDataDF.columns.values
        
        assert phjPatientIDVarName in phjFullColumnsList, "The patient ID variable ('{0}') is required to collapse the dataframe but it is not present in the list of columns.".format(phjPatientIDVarName)
        
        if phjConsultationIDVarName is not None:
            assert phjConsultationIDVarName in phjFullColumnsList, "The variable '{0}' is not present in the dataframe.".format(phjConsultationIDVarName)
        
        if phjConsultationDateVarName is not None:
            assert phjConsultationDateVarName in phjFullColumnsList, "The variable '{0}' is not present in the dataframe.".format(phjConsultationDateVarName)
        
        if phjFreeTextVarName is not None:
            assert phjFreeTextVarName in phjFullColumnsList, "The variable '{0}' is not present in the dataframe.".format(phjFreeTextVarName)
        
        if phjAggDict is not None:
            phjAggVarsList = [k for k,v in phjAggDict.items()]
            
            # Check that the phjPatientIDVarName variable is not included in the phjAggDict dictionary
            for k,v in phjAggDict.items():
                assert k != phjPatientIDVarName, "The patient ID variable '{0}' cannot be included in the dictionary defining aggregation functions.".format(phjPatientIDVarName)
            
                # It turns out that a dataframe can have multiple columns with the same name. Whilst this is an
                # intended behaviour, it can cause some problems. Therefore, try to avoid this situation where possible.
                # In the aggregation dictionary, most variables will be aggregated using a single method (e.g. last,
                # min, etc.). However, in some cases, a single variable may be aggregated using several methods
                # (e.g. consultation date will be aggregated using both 'first' and 'last' methods). In this example,
                # two columns will be produced which will be labelled as datevar_first and datevar_last. We need to make
                # sure that these new columns do not already exist in the dataframe.
                # Currently not implemented.
                # if isinstance(v,list)...
        
    except AssertionError as e:
        print ("An AssertionError has occurred. ({0})".format(e))
        
        phjGroupedDF = None
    
    else:
        
        if phjConsultationDateVarName is not None:
            # Ensure date of consultation variable is in datetime format
            phjAllDataDF = phjParseDateVar(phjDF = phjAllDataDF,
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
        
        
        # Initially create an ordered dict where each variable reports the 'last' entry
        phjCollapseAggDict = collections.OrderedDict((c,'last') for c in phjColList)   # This creates an ordered dict using a list comprehension-type syntax
        
        
        # Modify the dict so some of the important variables will be collapsed using different
        # methods (e.g. count, first and last dates and concatenating text)
        phjCollapseAggDict[phjConsultationIDVarName] = 'count'
        
        if phjConsultationDateVarName is not None:
            phjCollapseAggDict[phjConsultationDateVarName] = ['first','last']
        
        if phjFreeTextVarName is not None:
            phjCollapseAggDict[phjFreeTextVarName] = lambda x: ' /// '.join(x.fillna('EMPTY FIELD'))
        
        # Update phjCollapseAggDict with the phjAggDict items supplied by user. The values in
        # phjAggDict will replace those in phjCollapseAggDict.
        # Then remove any column names in phjCollapseAggDict that doesn't exist in dataframe.
        if phjAggDict is not None:
            phjCollapseAggDict.update(phjAggDict)
            phjCollapseAggDict = collections.OrderedDict((k,v) for k,v in phjCollapseAggDict.items() if k in phjAllDataDF.columns.values.tolist())
        
        
        # Sort data based on patient ID and date of consultation and groupby patient ID.
        # Variables are aggregated based on definitions in the phjCollapseAggDict.
        phjGroupedDF = phjAllDataDF.sort_values([phjPatientIDVarName,phjConsultationDateVarName],
                                                axis = 0,
                                                ascending = True).groupby(phjPatientIDVarName).agg(phjCollapseAggDict)
        
        # Set phjMultiIndex to True or False
        phjMultiIndex = phjGroupedDF.columns.nlevels > 1
        
        
        # Flatten a column multi-index if there is one.
        if phjMultiIndex == True:
            
            # This will produce names of columns that are appended with agg function (e.g. '_last', '_<lambda>', etc.).
            # May decide to rename columns back to something more similar to original, bearing in
            # mind that simply removing some suffixes may leave multiple columns with the same name.
            phjGroupedDF.columns = ['_'.join(col).strip() for col in phjGroupedDF.columns.values]
        
        
        # If there is a column multi-index, the names of the columns will be named such as:
        # 'patient_', 'gender_last','freetext_<lambda>' etc. The following produces a dict
        # that will replace necessary column headings with something more readable. If there
        # is not a column multi-index, the headings will not require changing and the keys
        # in this dict will not match any columns and therefore no columns will be renamed.
        phjRenameDict = phjGetRenameCollapsedColumnsDict(phjPatientDataframeColumnHeadingsList = phjGroupedDF.columns.values,
                                                         phjPatientIDVarName = phjPatientIDVarName,
                                                         phjConsultationIDVarName = phjConsultationIDVarName,
                                                         phjAggDict = phjCollapseAggDict,
                                                         phjMultiIndex = phjMultiIndex,
                                                         phjPrintResults = phjPrintResults)
        
        phjGroupedDF = phjGroupedDF.rename(columns = phjRenameDict)
        phjGroupedDF = phjGroupedDF.reset_index(drop = False)
        
        if phjPrintResults == True:
            print("Dataframe grouped on patient ID\n")
            print(phjGroupedDF)
    
    return phjGroupedDF



# Secondary functions
# ===================
def phjCheckColumns(phjDF,
                    phjDFDescriptorStr = None,      # An optional parameter used to describe the dataframe being checked in feedback
                    phjColumnsPresentList = None,
                    phjColumnsAbsentList = ['case','group'],
                    phjPrintResults = False):
    
    # This function checks that columns that need to be present in a dataframe are present
    # and columns that need to be absent are absent.
    
    # Start by assuming that phjTempCheckVar is True and set to False if any of the checks fail
    phjTempCheckVar = True
    
    # Convert the column headings in the dataframe to a list
    phjFullColumnsList = phjDF.columns.values
    
    # Check that parameters that need to be included in column heading list are indeed present
    if set(phjColumnsPresentList).issubset(phjFullColumnsList) == False:
        print("\nNot all required columns are present in the '{0}' dataframe.".format(phjDFDescriptorStr))
        
        for c in phjColumnsPresentList:
            if c not in phjFullColumnsList:
                print("Column '{0}' does not exist in the '{1}' dataframe.".format(c,phjDFDescriptorStr))
        
        phjTempCheckVar = False
    
    else:
        print("\nAll necessary columns are present in the '{0}' dataframe.".format(phjDFDescriptorStr))
        
    # Check that parameters that need to NOT be included in column heading list are indeed absent
    if phjColumnsAbsentList is not None:
        for c in phjColumnsAbsentList:
            if c in phjFullColumnsList:
                print("\nColumn '{0}' needs to be created but already exists in the '{1}' dataframe. Please rename this column and try again.".format(c,phjTempDescriptorStr))
                
                phjTempCheckVar = False
    
    
    return phjTempCheckVar



def phjGetVerifiedConsultationCases(phjAllDataDF,
                                    phjCasesDF,   # Can be a dataframe ideally but could also be a series, array or list.
                                    phjConsultationIDVarName = None,   # Either consultation ID or patient ID depending on control type
                                    phjPrintResults = False):
    
    # Check whether all the consultations in the cases are a subset of the consultations
    # in the full dataframe. If the list of consultations is a subset of those found in
    # the full dataframe then return a dataframe containing all the cases; otherwise
    # check that the suppled dataframe of cases contains all the required variables and
    # return the cases dataframe as it was supplied by the user.
    
    # It is tempting – and I have nearly succumbed on several occasions – to have this
    # function return a dataframe containing only the bare minimum of variables. However,
    # at a later point, the dataframe of verified cases (returned from this function) will
    # be used to merge to the case-control dataset and, therefore, all variables should be
    # included at this stage to avoid the need for duplicated effort later on.
    if isinstance(phjCasesDF,pd.DataFrame):
        
        # If unique identifier is incorrect then verified cases are returned as None
        if (phjConsultationIDVarName is None) or (phjConsultationIDVarName not in phjCasesDF.columns.values):
            print("\nUnique identifier needs to be defined when cases are passed as a dataframe.")
            phjVerifiedCasesDF = None
            
        else:
            # If the list of cases is a subset of the data in the full dataframe then
            # check that the columns in both dataframes match and, if so, return the
            # original cases dataframe; if not, return a dataframe of cases where the
            # columns have been recreated from the dataframe of all data.
            # (N.B. What happens if extra columns are included in the cases
            #       dataframe. In this situation, those columns may be lost.
            #       Therefore, could address this in future.)
            # (N.N.B. Actually decided to return a slice of the original dataframe
            #         regardless of whether the dataframe of cases contained all the
            #         necessary columns or not.)
            if set(phjCasesDF[phjConsultationIDVarName]).issubset(phjAllDataDF[phjConsultationIDVarName]):
                
                if set(phjCasesDF.columns.values) == set(phjAllDataDF.columns.values):
                    #phjVerifiedCasesDF = phjCasesDF
                    phjCasesMask = phjAllDataDF[phjConsultationIDVarName].isin(phjCasesDF[phjConsultationIDVarName])
                    phjVerifiedCasesDF = phjAllDataDF.loc[phjCasesMask,:]
                
                else:
                    phjCasesMask = phjAllDataDF[phjConsultationIDVarName].isin(phjCasesDF[phjConsultationIDVarName])
                    phjVerifiedCasesDF = phjAllDataDF.loc[phjCasesMask,:]
            
            else:
                # If list of case consultations is NOT a subset of the full dataset
                # then it is necessary that all variables/columns in the full dataframe
                # are also contained in the cases dataframe.
                if set(phjCasesDF.columns.values) == set(phjAllDataDF.columns.values):
                    phjVerifiedCasesDF = phjCasesDF
                
                else:
                    print("\nThe cases are not a subset of all the data and the two dataframes do not contain the same columns. Therefore, verified cases cannot be identified.")
                    phjVerifiedCasesDF = None
    
    # If the phjCasesDF is actually any other iterable (e.g.list, array, Series) then
    # must check if cases are a subset of the rows in the full dataframe. If so, recreate
    # a verified dataframe; if not, return None. 
    elif not isinstance(phjCasesDF,str):
        
        if set(phjCasesDF).issubset(phjAllDataDF[phjConsultationIDVarName]):
            
            phjCasesMask = phjAllDataDF[phjConsultationIDVarName].isin(phjCasesDF)
            phjVerifiedCasesDF = phjAllDataDF.loc[phjCasesMask,:]
        
        else:
            print("\nThe cases are not a subset of all the data and, therefore, a verified dataframe of cases (with all variables) cannot be created.")
            phjVerifiedCasesDF = None
            
    else:
        print("\nThe object containing cases is not recognised.")
        phjVerifiedCasesDF = None
    
    
    return phjVerifiedCasesDF



def phjGetCollapsedPatientDataframeColumns(phjAllDataDF,       # Dataframe containing all columns of data to be collapsed based on patient ID
                                           phjConsultationIDVarName = None,
                                           phjConsultationDateVarName = None,
                                           phjPatientIDVarName = None,
                                           phjFreeTextVarName = None,
                                           phjAggDict = None,
                                           phjPrintResults = False):
    
    # This function simply returns a list of the column headings that will be created
    # when the dataframe of consultations is collapsed on patient ID. There is probably
    # a clever way to work this out based on the given arguments but this function takes
    # the pragmatic approach of selecting a small sample of consultations, collapsing
    # them on patient ID and then returning the column headings of the resulting dataframe.
    # Why a random sample of 5 patients (or, indeed, any number greater than 1)? Not sure.
    # I wanted to minimise any unforeseen problems of a single patient containing all
    # NaN values or some other unexpected data; a sample of 5 should contain some valid
    # data that can be used to collapse the dataframe based on patient ID.
    phjTempUniquePatientsSer = phjAllDataDF.loc[:,phjPatientIDVarName]
    
    if len(phjTempUniquePatientsSer) > 5:
        
        phjTempPatientSample = phjTempUniquePatientsSer.sample(n = 5)
        print(phjTempPatientSample)
        
        phjTempMask = phjAllDataDF[phjPatientIDVarName].isin(phjTempPatientSample)
        
        phjTempSampleDF = phjAllDataDF.loc[phjTempMask,:]
    
    else:
        # Otherwise, original dataframe contains 10 or fewer patients and therefore
        # use all the data
        phjTempSampleDF = phjAllDataDF
        
    phjTempSampleDF = phjCollapseOnPatientID(phjAllDataDF = phjTempSampleDF,       # Dataframe containing all columns of data to be collapsed based on patient ID
                                             phjPatientIDVarName = phjPatientIDVarName,
                                             phjConsultationIDVarName = phjConsultationIDVarName,
                                             phjConsultationDateVarName = phjConsultationDateVarName,
                                             phjFreeTextVarName = phjFreeTextVarName,
                                             phjAggDict = phjAggDict,
                                             phjPrintResults = phjPrintResults)
    
    phjTempCollapsedColumnsList = phjTempSampleDF.columns.values
    
    if phjPrintResults == True:
        print("\nColumn headings in collapsed patient-based dataframe")
        print(phjTempCollapsedColumnsList)
    
    return phjTempCollapsedColumnsList



def phjGetVerifiedPatientCases(phjAllDataDF,
                               phjCasesDF,
                               phjConsultationIDVarName = None,
                               phjConsultationDateVarName = None,
                               phjPatientIDVarName = None,
                               phjFreeTextVarName = None,
                               phjAggDict = None,
                               phjPrintResults = False):
    
    # If requesting a patient-based case control study then the provided list of
    # cases MUST be a subset of the whole dataset. A dataframe of verified patient cases
    # is generated from the whole dataframe of all consultations by collapsing columns
    # based on patient ID.
    
    # It is tempting – and I have nearly succumbed on several occasions – to have this
    # function return a dataframe containing only the bare minimum of variables. However,
    # at a later point, the dataframe of verified cases (returned from this function) will
    # used to merge to the case-control dataset and, therefore, all variables should be
    # included at this stage to avoid the need for duplicated effort later on.
    
    if isinstance(phjCasesDF,pd.DataFrame):
    
        # If unique identifier is incorrect then verified cases are returned as None
        if (phjPatientIDVarName is None) or (phjPatientIDVarName not in phjCasesDF.columns.values):
            print("\nUnique identifier needs to be defined when cases are passed as a dataframe.")
            phjVerifiedCasesDF = None
            
        else:
        
            if set(phjCasesDF[phjPatientIDVarName]).issubset(phjAllDataDF[phjPatientIDVarName]):
                
                phjCasesMask = phjAllDataDF[phjPatientIDVarName].isin(phjCasesDF[phjPatientIDVarName])
                
                phjVerifiedCasesDF = phjCollapseOnPatientID(phjAllDataDF = phjAllDataDF.loc[phjCasesMask,:],   # Dataframe containing all columns of data to be collapsed based on patient ID
                                                            phjPatientIDVarName = phjPatientIDVarName,
                                                            phjConsultationIDVarName = phjConsultationIDVarName,
                                                            phjConsultationDateVarName = phjConsultationDateVarName,
                                                            phjFreeTextVarName = phjFreeTextVarName,
                                                            phjAggDict = phjAggDict,
                                                            phjPrintResults = phjPrintResults)
            
            else:
                # Otherwise the patient IDs supplied are not a subset of the whole list
                # of patients supplied in phjAllDataDF.
                # If the cases dataframe contains the same columns as the dataframe of
                # patients will contain when the consultation dataframe is collapsed on
                # patient ID.
                
                # Get a list of all column headings that will be included in a dataframe
                # of patients that is created by collapsing the consultation data
                # on patient ID (except 'case' and 'group' column headings)
                phjPatientColumnsList = phjGetCollapsedPatientDataframeColumns(phjAllDataDF = phjAllDataDF,
                                                                               phjConsultationIDVarName = phjConsultationIDVarName,
                                                                               phjConsultationDateVarName = phjConsultationDateVarName,
                                                                               phjPatientIDVarName = phjPatientIDVarName,
                                                                               phjFreeTextVarName = phjFreeTextVarName,
                                                                               phjAggDict = phjAggDict,
                                                                               phjPrintResults = phjPrintResults)
                
                # Columns 'case' and 'group' shouldn't be present but just to make sure...
                phjPatientColumnsList = [c for c in phjPatientColumnsList if c not in ['case','group']]
                
                if set(phjCasesDF.columns.values) == set(phjPatientColumnsList):
                    phjVerifiedCasesDF = phjCasesDF
                    
                else:
                    print("\nNot all case patient IDs are included in the dataframe containing all the data.\nFor patient-based case control studies, this is a requirement.")
                    phjVerifiedCasesDF = None
    
    elif not isinstance(phjCasesDF,str):
        
        if set(phjCasesDF).issubset(phjAllDataDF[phjPatientIDVarName]):
            
            phjCasesMask = phjAllDataDF[phjPatientIDVarName].isin(phjCasesDF)
            
            phjVerifiedCasesDF = phjCollapseOnPatientID(phjAllDataDF = phjAllDataDF.loc[phjCasesMask,:],   # Dataframe containing all columns of data to be collapsed based on patient ID
                                                        phjPatientIDVarName = phjPatientIDVarName,
                                                        phjConsultationIDVarName = phjConsultationIDVarName,
                                                        phjConsultationDateVarName = phjConsultationDateVarName,
                                                        phjFreeTextVarName = phjFreeTextVarName,
                                                        phjAggDict = phjAggDict,
                                                        phjPrintResults = phjPrintResults)
        
        else:
            phjVerifiedCasesDF = None
    
    else:
        print("\nThe object containing cases is not recognised.")
        phjVerifiedCasesDF = None
    
    
    return phjVerifiedCasesDF



def phjCheckCases(phjAllDataDF,
                  phjCasesDF,
                  phjUniqueIdentifierVarName,   # Either consultation ID or patient ID depending on control type
                  phjPrintResults = False):
    
    # Check whether all the consultations/patients
    # present are a subset of the consultations/patients in the full dataframe.
    # If the list of consultations/patients is a subset of those found in
    # the full dataframe then no other further columns are required since all the
    # required variables can be retrieved from the full dataframe.
    if set(phjCasesDF[phjUniqueIdentifierVarName]).issubset(phjAllDataDF[phjUniqueIdentifierVarName]):
        
        # Check if the columns in the cases dataframe are the same as the
        # columns in the full dataframe; if not, create a cases dataframe
        # by getting data from the full dataframe.
        # (N.B. What happens if extra columns are included in the cases
        #       dataframe. In this situation, those columns will be lost.
        #       Therefore, could address this in future.)
        if set(phjCasesDF.columns.values) != set(phjAllDataDF.columns.values):
            phjCaseConsultationsMask = phjAllDataDF[phjUniqueIdentifierVarName].isin(phjCasesDF[phjUniqueIdentifierVarName])
            phjCasesDF = phjAllDataDF.loc[phjCaseConsultationsMask,:]
    
    else:
        # If the case consultations are NOT a subset of the full dataset
        # then it is necessary that all variables are contained within the
        # cases dataframe.
        if set(phjCasesDF.columns.values) != set(phjAllDataDF.columns.values):
            print("\nThe complete dataframe and the dataframe of cases do not contain the same columns.")
            phjCasesDF = None
    
    return phjCasesDF



def phjGetPotentialControls(phjDF,                      # A pandas dataframe containing all data from which controls can be selected. May also contain cases as well (these will be excluded).
                            phjCasesPatientIDSer = None,    # A pandas series containing patient ID for all confirmed cases
                            phjScreeningRegexStr = None,
                            phjScreeningRegexPathAndFileName = None,
                            phjConsultationIDVarName = None,
                            phjConsultationDateVarName = None,
                            phjPatientIDVarName = None,
                            phjRequiredColumnsList = None,
                            phjFreeTextVarName = None,
                            phjControlType = 'consultation',   # Other option would be 'patient'
                            phjAggDict = None,
                            phjPrintResults = False):
    ### THINGS TO CHECK
    ### phjPatientIDVarName is a string and not a list and that is contained in dataframe
    ### phjCasesPatientSer is a Pandas series not a dataframe
    
    # Get regex used to screen for original potential cases
    phjScreeningRegex = phjGetRegexStr(phjRegexStr = phjScreeningRegexStr,
                                       phjRegexPathAndFileName = phjScreeningRegexPathAndFileName,
                                       phjPrintResults = phjPrintResults)
    
    if phjScreeningRegex is not None:
        # Compile regex
        phjRegex = re.compile(phjScreeningRegex,flags=re.I|re.X)
        
        # Run regex against freetext field and create a binary mask to identify all
        # consultations that match the regex.
        # NA values are set to FALSE.
        phjRegexMask = phjDF[phjFreeTextVarName].str.contains(phjRegex, na = False)
        
        # Retrieve patient IDs for consultations where freetext field contains a match
        phjCasesPatientID = phjDF.loc[phjRegexMask,phjPatientIDVarName]
        
        # Combine with Patient IDs passed to function to produce an array of all
        # patient IDs that should not be included in potential control dataframe
        #phjCasesPatientIDArr = phjCasesPatientID.append(phjCasesPatientIDSer).unique()
        phjCasesPatientIDArr = phjCasesPatientID.append(phjCasesPatientIDSer).unique()
        
        # Create a mask of all patients that could be included in potentials control
        # list. (This is, in fact, the inverse of the output from .isin() method)
        phjControlConsultationsMask = ~phjDF[phjPatientIDVarName].isin(phjCasesPatientIDArr)
        
        # Use the mask to remove all cases patients from the dataframe
        # Only retain the required columns variables
        phjControlConsultationsDF = phjDF.loc[phjControlConsultationsMask,phjRequiredColumnsList].reset_index(drop = True)
        
        if phjControlType == 'consultation':
            # Return the dataframe of patient IDs that have already been calculated
            phjPotentialControlsDF = phjControlConsultationsDF
            
        elif phjControlType == 'patient':
            
            # Need to consolidate based on patient ID.
            # Return dataframe consisting of patient ID and a variable giving the count
            # of the consultations
            # phjPotentialControlsDF = phjControlConsultationsDF.groupby(phjPatientIDVarName).agg('count').rename(columns = {phjConsultationIDVarName:'consultation_count'}).reset_index(drop = False)
            phjPotentialControlsDF = phjCollapseOnPatientID(phjAllDataDF = phjControlConsultationsDF,   # Dataframe containing all columns of data to be collapsed based on patient ID
                                                            phjPatientIDVarName = phjPatientIDVarName,
                                                            phjConsultationIDVarName = phjConsultationIDVarName,
                                                            phjConsultationDateVarName = phjConsultationDateVarName,
                                                            phjFreeTextVarName = None,
                                                            phjAggDict = phjAggDict,
                                                            phjPrintResults = phjPrintResults)
            
            
        else:
            print("Option entered for requested control type ('{0}') is not recognised.".format(phjControlType))
            phjPotentialControlsDF = None
    
    else:
        print('Could not identify the screening regex.')
        phjPotentialControlsDF = None
    
    
    return phjPotentialControlsDF



def phjPrintIndexHeading(i):
    # If the phjPrintResults parameter is passed as True, then output is printed to
    # window. As the algorithm steps through each case (labelled i), this function
    # prints a heading giving the number of the case being processed.
    print('\n' + '*'*12 + '*'*len(str(i)))
    print('*** i = ' + str(i) + ' ***')
    print('*'*12 + '*'*len(str(i)))
    
    return



def phjParameterCheck(phjCasesDF,
                      phjPotentialControlsDF,
                      phjUniqueIdentifierVarName,
                      phjMatchingVariablesList,
                      phjControlsPerCaseInt):
    
    # Get list of column names from cases and controls dataframes
    phjCasesDFColumnNamesList = phjCasesDF.columns.values.tolist()
    phjPotentialControlsDFColumnNamesList = phjPotentialControlsDF.columns.values.tolist()
    
    
    # Start off by assuming that the parameters are all OK and set the phjTempCheckVar
    # variable to True. Then make checks and, if the check fails, set the phjTempCheckVar
    # to False.
    phjTempCheckVar = True
    
    # Check that phjMatchingVariablesList is a list and not a string
    if (not isinstance(phjMatchingVariablesList,list)) & (phjMatchingVariablesList is not None):
    # if (phjMatchingVariablesList is None):
        print('The phjMatchingVariablesList parameter passed to this function was not the default (None) value and was not a list.')
        phjTempCheckVar = False
        
    # Check that phjControlsPerCase is an int
    if not isinstance(phjControlsPerCaseInt,int):
        print('The phjControlsPerCase parameter passed to this function was not an integer.')
        phjTempCheckVar = False
    
    # Check that 'group' and 'case' columns do not already exist in dataframe.
    # This function will return a database that includes columns entitled 'group'
    # and 'case'. Therefore, it is important to check that these names are
    # not included in the original dataframe columns. In fact, it would only be
    # necessary to check that 'group' and 'case' are not in the phjUniqueIdentifier
    # or the phjMatchingVariablesList since these are the only columns that are included
    # in the returned dataframe. However, columns named 'group' or 'case' in the original
    # database would lead to confusion. Therefore, recommend that columns 'group' and
    # 'case' should be renamed before running this function.
    if (('group' in phjCasesDFColumnNamesList) | ('case' in phjCasesDFColumnNamesList) | 
        ('group' in phjPotentialControlsDFColumnNamesList) | ('case' in phjPotentialControlsDFColumnNamesList)):
        print("This function aims to return a dataframe with added columns called 'group' and 'case'. However, columns with these names already exist. Please rename these columns and re-run this function.")
        phjTempCheckVar = False
        
    # Check that phjUniqueIdentifier is contained within both phjCasesDF and
    # phjPotentialControlsDF. If not, then return None.
    if ((phjUniqueIdentifierVarName not in phjCasesDFColumnNamesList) | (phjUniqueIdentifierVarName not in phjPotentialControlsDFColumnNamesList)):
        print('The variable ', phjUniqueIdentifierVarName, ' is not contained in the cases and/or potential controls dataframes.')
        phjTempCheckVar = False
        
    # Check that phjUniqueIdentifierVarName columns in both case and controls dataframe
    # contains unique values.
    # Firstly, join unique identifier columns into a single series and then compare
    # total length with length of unique series.
    phjTempSeries = pd.concat([phjCasesDF[phjUniqueIdentifierVarName],phjPotentialControlsDF[phjUniqueIdentifierVarName]],axis = 0)
    
    if (phjTempSeries.size > phjTempSeries.unique().size):
        print("The unique identifier variable does not contain unique values.")
        phjTempCheckVar = False
    
    # Check that the variable names in the phjMatchingVariablesList are all contained
    # within both phjCasesDF and phjPotentialControlDF.
    if isinstance(phjMatchingVariablesList,list):
        for phjTempListItem in phjMatchingVariablesList:
            if ((phjTempListItem not in phjCasesDFColumnNamesList) | (phjTempListItem not in phjPotentialControlsDFColumnNamesList)):
                print('The variable ', phjTempListItem, 'is not in the cases and/or potential controls dataframes.')
                phjTempCheckVar = False
            
    return phjTempCheckVar



def phjAddRecords(phjTempCaseControlDF,
                  phjUniqueIdentifierVarName,
                  phjUniqueIdentifierValue,
                  phjMatchingVariablesList,
                  phjMatchingVariablesValues,
                  phjTempRowCounter,
                  phjCaseVarName = 'case',
                  phjCaseValue = None,
                  phjGroupVarName = 'group',
                  phjGroupValue = None,
                  phjPrintResults = False):
    
    if phjPrintResults == True:
        print('\nPrint passed parameters')
        print('-----------------------')
        print('phjUniqueIdentifierVarName',phjUniqueIdentifierVarName)
        print('phjUniqueIdentifierValue',phjUniqueIdentifierValue)
        print('phjMatchingVariablesList',phjMatchingVariablesList)
        print('phjMatchingVariablesValues',phjMatchingVariablesValues)
        print('phjTempRowCounter',phjTempRowCounter)
        print('phjCaseVarName',phjCaseVarName)
        print('phjCaseValue',phjCaseValue)
        print('phjGroupVarName',phjGroupVarName)
        print('phjGroupValue',phjGroupValue)
    
    phjTempCaseControlDF.ix[phjTempRowCounter,phjUniqueIdentifierVarName] = phjUniqueIdentifierValue
    phjTempCaseControlDF.ix[phjTempRowCounter,phjGroupVarName] = phjGroupValue
    phjTempCaseControlDF.ix[phjTempRowCounter,phjCaseVarName] = phjCaseValue
    
    for phjTempVar in phjMatchingVariablesList:
        phjTempCaseControlDF.ix[phjTempRowCounter,phjTempVar] = phjMatchingVariablesValues[phjTempVar].tolist()
    
    return phjTempCaseControlDF



def phjSelectUnmatchedCaseControlSubjects(phjCasesDF,
                                          phjPotentialControlsDF,
                                          phjUniqueIdentifierVarName,
                                          phjMatchingVariablesList = None,
                                          phjControlsPerCaseInt = 1,
                                          phjPrintResults = False):
    
    phjRequestedNumberOfControls = phjControlsPerCaseInt * len(phjCasesDF.index)
    
    # If length of potential controls dataframe is less than or equal to the number
    # of controls requested then return the whole dataframe
    if len(phjPotentialControlsDF.index) <= phjRequestedNumberOfControls:
        print("The number of potential controls was too small to make a random selection. Therefore, all potential controls have been used.")
        phjTempCaseControlDF = pd.concat([phjCasesDF[phjUniqueIdentifierVarName],
                                          phjPotentialControlsDF[phjUniqueIdentifierVarName]],
                                         keys = [1,0],
                                         names = ['case']).reset_index(0)
    
    else:
        phjTempCaseControlDF = pd.concat([phjCasesDF[phjUniqueIdentifierVarName],
                                          phjPotentialControlsDF[phjUniqueIdentifierVarName].sample(n = phjRequestedNumberOfControls,
                                                                                                    replace = False,
                                                                                                    axis = 0)],
                                         keys = [1,0],
                                         names = ['case']).reset_index(0)
    
    phjTempCaseControlDF = phjTempCaseControlDF.reset_index(drop = True)
    
    return phjTempCaseControlDF



def phjSelectMatchedCaseControlSubjects(phjCasesDF,
                                        phjPotentialControlsDF,
                                        phjUniqueIdentifierVarName,
                                        phjMatchingVariablesList,
                                        phjControlsPerCaseInt = 1,
                                        phjPrintResults = False):
    # Algorithm outline
    # =================
    # 1. Create an empty dataframe in which selected cases and controls will be stored.
    # 2. Step through each case in the phjCasesDF dataframe, one at a time.
    # 3. Get data from matched variables for the case and store in a dict
    # 4. Create a mask for the controls dataframe to select all controls that match the cases in the matched variables
    # 5. Apply mask to controls dataframe and count number of potential matches
    # 6. Add cases and controls to dataframe
    # 7. Remove added control records from potential controls database so single case cannot be selected more than once
    # 8. Return dataframe containing list of cases and controls. This dataframe only
    #    contains columns with unique identifier, case and group id. It will,
    #    therefore need to be merged with the full database to get all other columns.
    
    # 1. Create empty dataframe
    # -------------------------
    # Create empty dataframe of known dimensions to hold cases and control data
    # Required length calculated as number of cases plus number of controls
    # (i.e. cases x number of matched controls). The variable list is the list
    # of matched variables plus a column to signify group and a column to signify
    # whether a case or a control and the unique identifier variable.
    phjTempCaseControlDFLength        = len(phjCasesDF.index) + (len(phjCasesDF.index) * phjControlsPerCaseInt)
    phjTempCaseControlDFColumnsList    = [phjUniqueIdentifierVarName] + ['group','case'] + phjMatchingVariablesList
    phjTempCaseControlDF            = pd.DataFrame( index = range(0,phjTempCaseControlDFLength),
                                                    columns = phjTempCaseControlDFColumnsList)
    
    if phjPrintResults == True:
        print('Temp case-control dataframe column list = ', phjTempCaseControlDFColumnsList)
        
    # Set counter to keep track of which row to add data to.
    phjTempRowCounter = 0
    
    # 2. Step through each case in the phjCasesDF dataframe, one at a time
    # --------------------------------------------------------------------
    for i in phjCasesDF.index:
        if phjPrintResults == True:
            # Print a heading for the ith case and number of potential controls
            phjPrintIndexHeading(i)
            print('\nLength of phjPotentialControls = ',phjPotentialControlsDF.index.size)
        
        # Reset some variables
        # --------------------
        # Reset number of available controls to np.nan
        phjTempNumberAvailableControls = np.nan
        
        # Clear phjTempDict (which will hold dict of case data.
        # N.B. using myDict = {} will create a new instance of myDict but other
        # references will still point to the old version of myDict with its original
        # data. (See http://stackoverflow.com/questions/369898/difference-between-dict-clear-and-assigning-in-python)
        # In contrast, myDict.clear() will clear the data.
        # But Python doesn't have a way to check if a variable has been defined
        # since it expects all variables to be defined before use. But can try to
        # access a variable and, if it fails, an exception will be raised.
        try:
            phjTempDict.clear()
        except NameError:
            phjTempDict = {}
        
        
        # 3. Get data from matched variables for the case
        # -----------------------------------------------
        # Create a dict for the data held in the matching variables in each case
        phjTempDict = phjCasesDF.ix[i,phjMatchingVariablesList].to_dict()
        
        # The above dict is of the form: {'var1': 'a', 'var2': 3}. However, this needs
        # to be passed to a df.isin() function and, as such, needs to be of the form:
        # {'var1': ['a'], 'var2': [3]}. Make this conversion using a dictionary
        # comprehension (as suggested by zondo 12 Mar 2016 - see:
        # http://stackoverflow.com/questions/35961614/converting-a-dict-to-a-dict-of-lists-in-python ).
        phjTempDict = {key: [value] for key, value in phjTempDict.items()}
        
        if phjPrintResults == True:
            print('\nphjTempDict =')
            print(phjTempDict)
        
        
        # 4. Create a mask for the controls dataframe
        # -------------------------------------------
        # Create a mask for the controls dataframe to select all controls that match the cases on the matched variables
        # phjTempMask = pd.DataFrame([phjPotentialControlsDF[key] == val for key, val in phjTempDict.items()]).T.all(axis=1)
        phjTempMask = phjPotentialControlsDF[phjMatchingVariablesList].isin(phjTempDict).all(axis=1)
        
        
        # 5. Apply mask to controls DF and count length
        # ---------------------------------------------
        phjTempMatchingControlsDF = phjPotentialControlsDF[phjTempMask]
        
        phjTempNumberAvailableControls = len(phjTempMatchingControlsDF.index)
        
        if phjPrintResults == True:
            print('\nNumber of available controls = ',phjTempNumberAvailableControls)
            with pd.option_context('display.max_rows', 6, 'display.max_columns', 6):
                print('\nMatching controls')
                print(phjTempMatchingControlsDF)
        
        
        # 6. Add cases and controls to dataframe
        # --------------------------------------
        # Python doesn't have switch-case structure. Use if...elif...else structure instead.
        # If there are no suitable controls then the case is not included
        # If the number of suitable controls is less than required then add all available
        # If there are more than request number of controls then select a random sample
        
        # i. If no controls then dump case (i.e. don't add it to the dataframe)
        # - - - - - - - - - - - - - - - - 
        if phjTempNumberAvailableControls == 0:
            if phjPrintResults == True:
                # Presumably don't include case in the final dataframe
                print('Available controls = 0. Case not included in final dataframe.')
            else:
                pass
        
        # ii. If less than (or equal to) requested number of controls then add all controls to dataframe
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        elif (phjTempNumberAvailableControls > 0) & (phjTempNumberAvailableControls <= phjControlsPerCaseInt):
            if phjPrintResults == True:
                print('\nAvailable controls = ', phjTempNumberAvailableControls, '. Requested number of controls = ',phjControlsPerCaseInt, '.')
                
            # Add case to dataframe
            # - - - - - - - - - - -
            phjTempCaseControlDF = phjAddRecords(phjTempCaseControlDF,
                                                 phjUniqueIdentifierVarName = phjUniqueIdentifierVarName,
                                                 phjUniqueIdentifierValue = phjCasesDF.ix[i,phjUniqueIdentifierVarName],
                                                 phjMatchingVariablesList = phjMatchingVariablesList,
                                                 phjMatchingVariablesValues = phjCasesDF.ix[[i],phjMatchingVariablesList],
                                                 phjTempRowCounter = [phjTempRowCounter],
                                                 phjCaseVarName = 'case',
                                                 phjCaseValue = [1],
                                                 phjGroupVarName = 'group',
                                                 phjGroupValue = [i],
                                                 phjPrintResults = phjPrintResults)
            
            if phjPrintResults == True:
                print('\nCase\n----')
                print(phjTempCaseControlDF.ix[phjTempRowCounter,:])
            
            # Increment row counter by 1
            phjTempRowCounter = phjTempRowCounter + 1
            
            # Add all available controls to the final dataframe
            # - - - - - - - - - - - - - - - - - - - - - - - - -
            if phjPrintResults == True:
                print('\nControls\n--------')
                print('All matching controls')
                with pd.option_context('display.max_rows', 6, 'display.max_columns', 6):
                    print(phjTempMatchingControlsDF)
            
            phjTempCaseControlDF = phjAddRecords(phjTempCaseControlDF,
                                                 phjUniqueIdentifierVarName = phjUniqueIdentifierVarName,
                                                 phjUniqueIdentifierValue = phjTempMatchingControlsDF[phjUniqueIdentifierVarName].tolist(),
                                                 phjMatchingVariablesList = phjMatchingVariablesList,
                                                 phjMatchingVariablesValues = phjCasesDF.ix[[i],phjMatchingVariablesList],
                                                 phjTempRowCounter = range(phjTempRowCounter, (phjTempRowCounter + phjTempNumberAvailableControls)),
                                                 phjCaseVarName = 'case',
                                                 phjCaseValue = [0]*phjTempNumberAvailableControls,
                                                 phjGroupVarName = 'group',
                                                 phjGroupValue = [i]*phjTempNumberAvailableControls,
                                                 phjPrintResults = phjPrintResults)
            
            if phjPrintResults == True:
                print('\nControls in dataframe')
                print(phjTempCaseControlDF.loc[phjTempRowRange])
            
            # 7. Delete selected controls from dataframe!!!
            # ------------------------------------------
            phjPotentialControlsDF = phjPotentialControlsDF[~phjPotentialControlsDF[phjUniqueIdentifierVarName].isin(phjTempMatchingControlsDF[phjUniqueIdentifierVarName].tolist())]
            
            # Increment row counter by number of available controls
            phjTempRowCounter = phjTempRowCounter + phjTempNumberAvailableControls
            
        
        # iii. If more than requested number of controls then add selection of controls to dataframe
        # ------------------------------------------------------------------------------------------
        elif (phjTempNumberAvailableControls > phjControlsPerCaseInt):
            if phjPrintResults == True:
                print('\nAvailable controls = ', phjTempNumberAvailableControls, '. Requested number of controls = ',phjControlsPerCaseInt, '.')
            
            # Add case to dataframe
            # - - - - - - - - - - -
            phjTempCaseControlDF = phjAddRecords(phjTempCaseControlDF,
                                                 phjUniqueIdentifierVarName = phjUniqueIdentifierVarName,
                                                 phjUniqueIdentifierValue = phjCasesDF.ix[i,phjUniqueIdentifierVarName],
                                                 phjMatchingVariablesList = phjMatchingVariablesList,
                                                 phjMatchingVariablesValues = phjCasesDF.ix[[i],phjMatchingVariablesList],
                                                 phjTempRowCounter = [phjTempRowCounter],
                                                 phjCaseVarName = 'case',
                                                 phjCaseValue = [1],
                                                 phjGroupVarName = 'group',
                                                 phjGroupValue = [i],
                                                 phjPrintResults = phjPrintResults)
            
            if phjPrintResults == True:
                print('\nCase\n----')
                print(phjTempCaseControlDF.ix[phjTempRowCounter,:])
            
            # Increment row counter by 1
            phjTempRowCounter = phjTempRowCounter + 1
            
            # Add random selection of controls to dataframe
            # - - - - - - - - - - - - - - - - - - - - - - -
            phjTempSampleMatchingControlsDF = phjTempMatchingControlsDF.sample( n = phjControlsPerCaseInt,
                                                                                replace = False,
                                                                                axis = 0)
            
            if phjPrintResults == True:
                print('\nControls\n--------')
                print('All matching controls')
                with pd.option_context('display.max_rows', 6, 'display.max_columns', 6):
                    print(phjTempSampleMatchingControlsDF)
            
            phjTempRowRange = range(phjTempRowCounter, (phjTempRowCounter + phjControlsPerCaseInt))
            
            phjTempCaseControlDF = phjAddRecords(phjTempCaseControlDF,
                                                 phjUniqueIdentifierVarName = phjUniqueIdentifierVarName,
                                                 phjUniqueIdentifierValue = phjTempSampleMatchingControlsDF[phjUniqueIdentifierVarName].tolist(),
                                                 phjMatchingVariablesList = phjMatchingVariablesList,
                                                 phjMatchingVariablesValues = phjCasesDF.ix[[i],phjMatchingVariablesList],
                                                 phjTempRowCounter = range(phjTempRowCounter, (phjTempRowCounter + phjControlsPerCaseInt)),
                                                 phjCaseVarName = 'case',
                                                 phjCaseValue = [0]*phjControlsPerCaseInt,
                                                 phjGroupVarName = 'group',
                                                 phjGroupValue = [i]*phjControlsPerCaseInt,
                                                 phjPrintResults = phjPrintResults)
            
            if phjPrintResults == True:
                print('\nControls in dataframe')
                print(phjTempCaseControlDF.loc[phjTempRowRange])
            
            # 7. Delete selected controls from dataframe!!!
            # ------------------------------------------
            phjPotentialControlsDF = phjPotentialControlsDF[~phjPotentialControlsDF[phjUniqueIdentifierVarName].isin(phjTempSampleMatchingControlsDF[phjUniqueIdentifierVarName].tolist())]
            
            # Increment row counter by number of controls requested per case
            phjTempRowCounter = phjTempRowCounter + phjControlsPerCaseInt
            
            
        # iv. If none of the above criteria about number of available controls is met
        # ---------------------------------------------------------------------------
        else:
            if phjPrintResults == True:
                # Report that something went wrong
                print('Something went wrong')
            else:
                phjTempCaseControlDF = None
    
    return phjTempCaseControlDF



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
    
    if phjPrintResults == True:
        print('\nRegex string used to screen cases:')
        print(phjTempRegex)
    
    return phjTempRegex



def phjGetRenameCollapsedColumnsDict(phjPatientDataframeColumnHeadingsList,
                                     phjPatientIDVarName,
                                     phjConsultationIDVarName,
                                     phjAggDict,
                                     phjMultiIndex = True,
                                     phjPrintResults = False):
    
    # If the agg functions is a list then will generate a multi-index. There are also
    # some single functions that will generate a multi-index (e.g. 'describe'). After
    # collapsing a multi-index, the column heading will be of the form varname_func.
    # In general, if a function results in a multi-index then the column headings
    # should remain in the form varname_func to ensure multiple functions performed
    # on a single column can be differentiated (e.g. varname_first and varname_last).
    # However, if the function does not result in a multi-index then the column heading
    # should be changed from varname_func to varname (so it matches the headings produced
    # by aggregation functions that do not produce a multi-index); this will, therefore,
    # more closely match the column headings that have not been collapsed from a multi-index.

    # Create a temporary dataframe consisting of variable name and function name
    # for datasets that generated a multi-index.
    # If there is a multi-index, the level 0 and level 1 component will have been
    # joined by '_'. This function splits the names back into variable and function
    # components, discarded those that have 2 or more columns for a single variable
    # and renames the single columns using the variable names only. I appreciate that
    # description is unintelligible. Try this description instead. A multi-index
    # my be represented as follows:
    #
    #    -------------------------------
    #    | var1 | var2          | var3 |
    #    |------|---------------|------|
    #    | last | first | last  | max  |
    #    |------|---------------|------|
    #
    # When the multi-index is collapsed, it will produce the following columns:
    #
    #    |-----------|------------|-----------|----------|
    #    | var1_last | var2_first | var2_last | var3_max |
    #    |-----------|------------|-----------|----------|
    #
    # This function takes a list of column headings and splits them into a
    # dataframe that looks like:
    # 
    #    |------|-------|-------|
    #    | col  | func  | count |
    #    |------|-------|-------|
    #    | var1 |  last |     1 |
    #    | var2 | first |     2 |
    #    | var2 |  last |     2 |
    #    | var3 |   max |     1 |
    #    |------|-------|-------|
    #
    # variables with 2 or more occurrences will be left unchanged because it is
    # important to be able to differentiate which column is which. However, variables
    # with only 1 occurrence will be renamed to the name of the original column.
    # Hence, in the above example, var1_last will be renamed to var1 and var3_max
    # will be renamed to var3 but var2_first and var2_last will remain.
    
    if phjMultiIndex == False:
        # If the aggregated dataframe has just a single level of column index then
        # column headings will be the name of the original column. The only column
        # that would need to be renamed is the consultation ID variable which should
        # be labelled 'count'.
        phjRenameDict = {}
        phjRenameDict[phjConsultationIDVarName] = 'count'
        
    else:
        # Split the elements in the column headings list to create a dataframe
        # containing variable name and function
        phjRenameDF = pd.DataFrame([[i.rsplit('_',1)[0],i.rsplit('_',1)[1]] for i in phjPatientDataframeColumnHeadingsList],
                                   columns = ['var','func'])

        # Create a column that contains the count of functions for each variable
        phjRenameGroupbyDF = phjRenameDF.groupby('var').agg({'func':"count"}).reset_index(drop = False)
        phjRenameGroupbyDF = phjRenameGroupbyDF.rename(columns = {'func':'count'})
        phjRenameDF = phjRenameDF.merge(phjRenameGroupbyDF,how='left',left_on='var',right_on='var')

        # Keep only those variables with a single row
        phjRenameDF = phjRenameDF.loc[phjRenameDF['count'] == 1,:]

        # Create a dictionary to use to rename the variable (i.e. var_func to var)
        phjVarFuncList = phjRenameDF[['var','func']].values.tolist()
        phjRenameDict = {i[0]+'_'+i[1]:i[0] for i in phjVarFuncList}

        # If the consultation ID variable is counted to indicate how many
        # consultations were present for each patient then the column will be
        # named 'consultID_count' (or something similar) after collapsing. The
        # above dictionary comprehension likely contains a 
        phjRenameDict['_'.join([phjConsultationIDVarName,'count'])] = 'count'

        # In a dataframe with a multi-index, the patient ID column may be renamed from
        # 'patientID' to 'patientID_' when collapsing the multi-index to a single index.
        # This dict entry will ensure the patient ID column is renamed.
        # N.B. The following may not be required in the latest version of the code
        #      because the patient ID variable name is created from the index when
        #      the index is reset. But won't do any harm.
        phjRenameDict[phjPatientIDVarName + '_'] = phjPatientIDVarName
    
    
    if phjPrintResults == True:
        print('\nDictionary used to rename the dataframe columns:')
        print(phjRenameDict)

  
    return phjRenameDict



if __name__ == '__main__':
    main()
