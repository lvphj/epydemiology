"""
Functions to check postcode variable in Pandas dataframe
========================================================

These functions take a dataframe containing postcode information and attempts
to correct errors and extract outward (first half), inward (second half) and
postcode area (first letters) components of the postcode.

"""

# Import required packages
# ========================

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


try:
    pkg_resources.get_distribution('epydemiology')
except pkg_resources.DistrbutionNotFound:
    epydemiologyPresent = False
    print("Error: Epydemiology package not available.")
else:
    epydemiologyPresent = True
    import epydemiology as epy


# Checking that pyxdameraulevenshtein package is installed does not work using the
# above method because attribute .DistributionNotFound is not present.
try:
    import pyxdameraulevenshtein as pyxdl
except ImportError:
    print("Error: pyxdameraulevenshtein package not installed. Some features may not be available.")


import re
import math



# Define functions to check UK postcodes
# ======================================

def phjCleanUKPostcodeVariable(phjTempDF,
                               phjRealPostcodeSer = None,
                               phjOrigPostcodeVarName = 'postcode',
                               phjNewPostcodeVarName = 'postcodeClean',
                               phjNewPostcodeStrLenVarName = 'postcodeCleanStrLen',
                               phjPostcodeCheckVarName = 'postcodeCheck',
                               phjMissingValueCode = 'missing',
                               phjMinDamerauLevenshteinDistanceVarName = 'minDamLevDist',
                               phjBestAlternativesVarName = 'bestAlternatives',
                               phjPostcode7VarName = 'postcode7',
                               phjPostcodeAreaVarName = 'postcodeArea',
                               phjSalvageOutwardPostcodeComponent = True,
                               phjCheckByOption = 'format',
                               phjDropExisting = False,
                               phjPrintResults = True):
    
    
    if phjMissingValueCode is None:
        # The missing value code can not be np.nan because the DataFrame.update() function will
        # not update NaN values and, as a result, some changes are likely to be missed.
        print('Missing value code can not be NaN. Please re-run the function with a string value.')
        
        # Return an unchanged dataframe
        phjTempWorkingDF = phjTempDF
        
    else:
        # Create a working dataframe containing postcode variable only and
        # making sure that new columns that will be created (e.g. to store cleaned
        # postcodes) don't already exist. If phjDropExisting is set to True,
        # pre-existing columns will be dropped from th original dataframe before
        # joining the data from the working dataframe.
        phjTempWorkingDF = phjCreateWorkingPostcodeDF(phjTempDF = phjTempDF,
                                                      phjRealPostcodeSer = phjRealPostcodeSer,
                                                      phjOrigPostcodeVarName = phjOrigPostcodeVarName,
                                                      phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                      phjNewPostcodeStrLenVarName = phjNewPostcodeStrLenVarName,
                                                      phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                      phjMinDamerauLevenshteinDistanceVarName = phjMinDamerauLevenshteinDistanceVarName,
                                                      phjBestAlternativesVarName = phjBestAlternativesVarName,
                                                      phjPostcode7VarName = phjPostcode7VarName,
                                                      phjPostcodeAreaVarName = phjPostcodeAreaVarName,
                                                      phjCheckByOption = phjCheckByOption,
                                                      phjDropExisting = phjDropExisting,
                                                      phjPrintResults = phjPrintResults)
        
        
        # Only continue to clean-up postcode values if a valid working directory is returned.
        if phjTempWorkingDF is not None:
            # Some basic clean-up house-keeping
            phjTempWorkingDF = phjUKPostcodeBasicCleanUp(phjTempDF = phjTempWorkingDF,
                                                         phjOrigPostcodeVarName = phjOrigPostcodeVarName,
                                                         phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                         phjMissingValueCode = phjMissingValueCode,
                                                         phjPrintResults = phjPrintResults)
            
            
            # Add a variable containing the length of the cleaned postcode string - this will
            # be useful at some point in the future
            phjTempWorkingDF[phjNewPostcodeStrLenVarName] = phjTempWorkingDF[phjNewPostcodeVarName].str.len()
            
            
            # Check whether postcodes are either correctly formatted (if checking by
            # format) or are real postcodes (if checking by dictionary)
            if (phjCheckByOption == 'format') or (phjCheckByOption == 'dictionary'):
                if phjCheckByOption == 'format':
                    # Identify correctly (and incorrectly) formatted postcodes
                    phjTempWorkingDF = phjUKPostcodeFormatCheck(phjTempDF = phjTempWorkingDF,
                                                                phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                                phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                                phjPostcodeComponent = 'all',
                                                                phjPrintResults = phjPrintResults)
                
                else:
                    # The function that created the working dafaframe has already checked that the user
                    # has passed a Series of postcodes.
                    # Start by converting the Series of all postcodes to an numpy array. A numpy arr is
                    # required because the Cython function pyxdameraulevenshtein() – see later – requires
                    # a numpy array against which to check.
                    
                    # Add postcode series to a dataframe and create column with spaces and punctuation removed
                    phjRealPostcodeDF = pd.DataFrame(phjRealPostcodeSer.rename('pcd'))
                    phjRealPostcodeDF['pcdMin'] = phjRealPostcodeDF['pcd'].replace('''[\W_]+''',value='',regex = True).str.upper()
                    phjRealPostcodeArr = np.array(phjRealPostcodeDF['pcdMin'])

                    # Create array of unique postcode districts for future use
                    phjPostcodeDistrictArr = np.array(phjRealPostcodeDF['pcdMin'].str.extract(pat = '''(?P<pcdDistrict>^\w{2,4})\w{3}$''',
                                                                                              flags = re.I,
                                                                                              expand = True)['pcdDistrict'].unique())


                    # Check if new postcode strings are real postcodes
                    # and, if so, set phjPostcodeCheckVarName to True
                    phjTempWorkingDF = phjUKPostcodeRealityCheck(phjTempDF = phjTempWorkingDF,
                                                                 phjRealPostcodeArr = phjRealPostcodeArr,
                                                                 phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                                 phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                                 phjMissingValueCode = phjMissingValueCode,
                                                                 phjPrintResults = phjPrintResults)
            
            
            if phjPrintResults == True:
                print("\nCorrectly and incorrectly formatted postcodes (BEFORE ERROR CORRECTION):")
                print(phjTempWorkingDF.loc[phjTempWorkingDF[phjNewPostcodeVarName].notnull(),phjPostcodeCheckVarName].value_counts())
                print(phjTempWorkingDF)
                print('\n')
            
            
            # Deal with postcode entries that do not match postcode regex (i.e. not formatted correctly)
            phjTempWorkingDF = phjUKPostcodeCorrectCommonErrors(phjTempDF = phjTempWorkingDF,
                                                                phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                                phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                                phjPrintResults = phjPrintResults)
            
            
            # Check whether CORRECTED postcodes are either correctly formatted (if checking by
            # format) or are real postcodes (if checking by dictionary)
            if (phjCheckByOption == 'format') or (phjCheckByOption == 'dictionary'):
                if phjCheckByOption == 'format':
                    # Identify correctly (and incorrectly) formatted postcodes
                    phjTempWorkingDF = phjUKPostcodeFormatCheck(phjTempDF = phjTempWorkingDF,
                                                                phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                                phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                                phjPostcodeComponent = 'all',
                                                                phjPrintResults = phjPrintResults)
                
                else:
                    # Check if new postcode strings are real postcodes
                    # and, if so, set phjPostcodeCheckVarName to True
                    phjTempWorkingDF = phjUKPostcodeRealityCheck(phjTempDF = phjTempWorkingDF,
                                                                 phjRealPostcodeArr = phjRealPostcodeArr,
                                                                 phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                                 phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                                 phjMissingValueCode = phjMissingValueCode,
                                                                 phjPrintResults = phjPrintResults)
            
            
            if phjPrintResults == True:
                print("\nCorrectly and incorrectly formatted postcodes (AFTER ERROR CORRECTION):")
                print(phjTempWorkingDF.loc[phjTempWorkingDF[phjNewPostcodeVarName].notnull(),phjPostcodeCheckVarName].value_counts())
                print(phjTempWorkingDF)
                print('\n')
            
            
            # Produce variable containing 7-character postcode
            phjTempWorkingDF = phjPostcodeFormat7(phjTempDF = phjTempWorkingDF,
                                                  phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                  phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                  phjPostcode7VarName = phjPostcode7VarName,
                                                  phjPrintResults = phjPrintResults)
            
            
            # Create variables containing outward and inward parts of postcode.
            # This function extracts outward and inward postcode components using the
            # full regex that was designed to check the structure of the postcode. This
            # is, perhaps, a bit of overkill as correctly-formatted postcodes could be
            # split using a much simpler regex.
            phjTempWorkingDF = phjExtractPostcodeComponents(phjTempDF = phjTempWorkingDF,
                                                            phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                            phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                            phjPostcodeComponent = 'all',
                                                            phjPrintResults = phjPrintResults)
            
            
            # If checking by dictionary, get the best alternative postcodes using adjusted
            # Damerau-Levenshtein distances
            if phjCheckByOption == 'dictionary':
                # Try to identify the postcodes to which unidentitied postcode strings most closely match
                phjTempWorkingDF = phjGetBestAlternativePostcodes(phjTempDF = phjTempWorkingDF,
                                                                  phjRealPostcodeArr = phjRealPostcodeArr,
                                                                  phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                                  phjNewPostcodeStrLenVarName = phjNewPostcodeStrLenVarName,
                                                                  phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                                  phjMinDamerauLevenshteinDistanceVarName = phjMinDamerauLevenshteinDistanceVarName)
            
            
            # If requested, attempt to salvage the postcode outward (postcode area)
            if phjSalvageOutwardPostcodeComponent == True:
                if phjCheckByOption == 'format':
                    # Some postcode entries may be just the outward part of the postcode (e.g. NP4, CH64, etc.).
                    # Such entries will not be identified as a correctly formatted postcode but it may be possible
                    # to salvage some information on the postcode district.
                    # To salvage postcode district, the string could only be 2, 3 or 4 characters long.
                    # Error correction will be applied and the format of the resulting string tested using the
                    # postcodeOutward group of the regular expression.
                    phjTempWorkingDF = phjSalvagePostcode(phjTempDF = phjTempWorkingDF,
                                                          phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                          phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                          phjPrintResults = phjPrintResults)
                    
                else:
                    # i.e. phjCheckByOption == 'dictionary
                    # Code not yet written
                    phjTempWorkingDF = phjTempWorkingDF
            
            
            # Extract postcode area from postcodeOutward variable
            phjTempWorkingDF = phjExtractPostcodeArea(phjTempDF = phjTempWorkingDF,
                                                      phjPostcodeAreaVarName = phjPostcodeAreaVarName,
                                                      phjPrintResults = phjPrintResults)
            
            
            # Finally, copy missing value code to postcodeClean variable if no postcode format has been extracted
            phjTempWorkingDF.loc[phjTempWorkingDF[phjPostcodeCheckVarName] == False,phjNewPostcodeVarName] = phjMissingValueCode
            
            
            if phjPrintResults == True:
                print('\nFinal working postcode dataframe\n================================\n')
                print(phjTempWorkingDF)
                print('\n')
            
            
            # To have reached this point in the function, the user has either given
            # permission to drop variables or the new column names do not occur in the
            # original dataframe.
            # Drop original postcode column from phjTempWorkingDF before adding newly-created
            # columns to original dataframe
            phjTempWorkingDF = phjTempWorkingDF.drop(phjOrigPostcodeVarName, axis = 1)
            
            # Remove pre-existing columns from original dataframe
            if phjDropExisting == True:
                for phjCol in phjTempWorkingDF.columns:
                    if phjCol in phjTempDF.columns:
                        phjTempDF = phjTempDF.drop(phjCol,axis=1)
            
            # Join the new working dataframe to the original dataframe based on index
            phjTempDF = phjTempDF.join(phjTempWorkingDF)
            
            
    # If a valid working dataframe was created then changes would have been made in above code
    # and copied to phjTempDF.
    # If working dataframe was not valid, then no changes would have been made and phjTempDF
    # would remain unaltered.
    # Either way, return phjTempDF.
    return phjTempDF



##########
##########

def phjCreateWorkingPostcodeDF(phjTempDF,
                               phjRealPostcodeSer = None,
                               phjOrigPostcodeVarName = 'postcode',
                               phjNewPostcodeVarName =  'postcodeClean',
                               phjNewPostcodeStrLenVarName = 'postcodeCleanStrLen',
                               phjPostcodeCheckVarName = 'postcodeCheck',
                               phjMinDamerauLevenshteinDistanceVarName = 'minDamLevDist',
                               phjBestAlternativesVarName = 'bestAlternatives',
                               phjPostcode7VarName = 'postcode7',
                               phjPostcodeAreaVarName = 'postcodeArea',
                               phjCheckByOption = 'format',
                               phjDropExisting = False,
                               phjPrintResults = False):
    
    # This function checks the dataframe passed to the phjCleanUKPostcode() function to
    # make sure that the phjOrigPostcodeVarName exists (i.e. a column of postcode data
    # exists). If a column of postcode data exists, the function creates a working directory
    # consisting of original postcodes, a column to contain to contain 'cleaned' data and
    # column of binary data to indicate whether the postcode is correctly formatted; other
    # required variables will be added as required. However, this function checks whether
    # additional column names already exist in original dataframe. If permission has not
    # been given to remove pre-existing columns then the function returns a
    # null working dataframe. If permission has been given to remove pre-existing
    # columns then a valid working directory is returned; pre-existing columns will be
    # removed before merging the working dataframe with original.
    
    # Initially assume that working directory should be returned
    phjReturnWorkingDF = True
    
    # Check whether named postcode variable actually exists...
    if phjOrigPostcodeVarName not in phjTempDF.columns:        # If postcode variable does not exist, return None
        print("Variable '{0}' does not exist in the dataframe. The variable should contain the original postcode data.".format(phjOrigPostcodeVarName))
        phjReturnWorkingDF = False
    
    else:
        # If checking postcodes 'by dictionary' then need to pass a Pandas Series containing all
        # possible postcodes (or, at least, all postcodes that you want to check against).
        # If the Series of postcodes has not been defined or is not a Series then a working dataframe
        # is not created.
        if (phjCheckByOption == 'dictionary') and (not isinstance(phjRealPostcodeSer,pd.Series)):
            if phjRealPostcodeSer is None:
                print("When checking postcodes by dictionary, please pass a Pandas series containing all postcodes.")
            else:
                print("When checking postcodes by dictionary, please pass a Pandas series containing all postcodes. The variable passed is not a Pandas series.")
            
            phjReturnWorkingDF = False
        
        else:
            # Create a list of column names that need to be added to the dataframe depending on whether
            # the postcodes are being check based on format (i.e. matches a regex) or by comparing with
            # a dictionary containing all real-life postcodes
            if (phjCheckByOption == 'format') or (phjCheckByOption == 'dictionary'):

                # Retrieve list of names of regex groups
                phjRegexGroupNamesList = phjGetPostcodeRegexGroupNamesList(phjPrintResults = False)

                if phjCheckByOption == 'format':
                    phjColumnList = [phjNewPostcodeVarName,
                                     phjNewPostcodeStrLenVarName,
                                     phjPostcodeCheckVarName,
                                     phjPostcode7VarName,
                                     phjPostcodeAreaVarName] + phjRegexGroupNamesList

                else:
                    # i.e. phjCheckByOption == 'dictionary'
                    phjColumnList = [phjNewPostcodeVarName,
                                     phjNewPostcodeStrLenVarName,
                                     phjPostcodeCheckVarName,
                                     phjMinDamerauLevenshteinDistanceVarName,
                                     phjBestAlternativesVarName,
                                     phjPostcode7VarName,
                                     phjPostcodeAreaVarName] + phjRegexGroupNamesList


                if phjDropExisting == False:
                    # If permission to drop pre-existing variables is not given, check whether
                    # original dataframe contains any columns of the same name as those columns
                    # that will need to be created.
                    phjPreExistingColumns = 0
                    for phjVarName in phjColumnList:
                        if phjVarName in phjTempDF.columns:
                            print("Column '{0}' needs to be added to the dataframe but the variable already exists; please delete the column and re-run the function.".format(phjVarName))
                            phjPreExistingColumns = phjPreExistingColumns + 1

                    if phjPreExistingColumns > 0:
                        phjReturnWorkingDF = False

            else:
                print("The phjCheckByOption variable '{0}' is not a recognised option.".format(phjCheckByOption))
                phjReturnWorkingDF = False
            
            
    if phjReturnWorkingDF is True:
        # Working dataframe only needs the original postcode variable, and some additional empty columns.
        # The other required columns will be created as required.
        phjWorkingDF = phjTempDF.loc[:,[phjOrigPostcodeVarName,
                                        phjNewPostcodeVarName,
                                        phjPostcodeCheckVarName]]
                                        
    else:
        phjWorkingDF = None
    
    return phjWorkingDF



def phjUKPostcodeBasicCleanUp(phjTempDF,
                              phjOrigPostcodeVarName = 'postcode',
                              phjNewPostcodeVarName = 'postcodeClean',
                              phjMissingValueCode = 'missing',
                              phjPrintResults = False):
    
    # Copy original postcode data to new variable
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjOrigPostcodeVarName]
    
    # Replace Python None values with Pandas phjMissingValueCode in original postcode variable
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].fillna(value = phjMissingValueCode)
    
    # Strip white space and punctuation and convert postcode text to all uppercase
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].replace('''[\W_]+''',value='',regex = True)
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].str.upper()
    
    # Empty cells should be replaced with missing value code.
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].replace('',value = phjMissingValueCode,regex = False)
    
    # Replace cells containing indication of missing or unknown with missing value code.
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].replace(re.compile('''^[\W_]*mis+i?n?g?[\W_]*$''',flags=re.I),value = phjMissingValueCode,regex = True)
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].replace(re.compile('''^[\W_]*(?:un|not)[\W_]*(?:k?nown)[\W_]*$''',flags=re.I),value = phjMissingValueCode,regex = True)
    
    # Postcodes that consist of all numbers should be changed to missing value code.
    phjTempDF[phjNewPostcodeVarName] = phjTempDF[phjNewPostcodeVarName].replace(re.compile('''^\s*\d+\s*$'''),value = phjMissingValueCode,regex = True)
    
    return phjTempDF



def phjUKPostcodeRegexDefinition(phjPrintResults = False):
    # The following Regex was taken from https://en.wikipedia.org/wiki/Talk:Postcodes_in_the_United_Kingdom
    # (accessed 22 Mar 2016). The page is also stored as PDF entitled:
    # "Talk/Postcodes in the United Kingdom - Wikipedia, the free encyclopedia".
    # Regex was originally given as:
    # '(GIR 0AA)|(((A[BL]|B[ABDFHLNRSTX]?|C[ABFHMORTVW]|D[ADEGHLNTY]|E[HNX]?|F[KY]|G[LUY]?|H[ADGPRSUX]|I[GMPV]|JE|K[ATWY]|L[ADELNSU]?|M[EKL]?|N[EGNPRW]?|O[LX]|P[AEHLOR]|R[GHM]|S[AEGKLMNOPRSTY]?|T[ADFNQRSW]|UB|W[ADFNRSV]|YO|ZE)[1-9]?[0-9]|((E|N|NW|SE|SW|W)1|EC[1-4]|WC[12])[A-HJKMNPR-Y]|(SW|W)([2-9]|[1-9][0-9])|EC[1-9][0-9]) [0-9][ABD-HJLNP-UW-Z]{2})'
    # However, this was modified slightly to allow for optional space between first and second
    # parts of postcode (even though all the whitespace has been removed in an earlier
    # step (see above) and restricting to beginning and end of string.
    # A new binary variable is created that contains 1 = correctly formated postcode and
    # 0 = incorrectly formatted postcode.
    # (N.B. The original did not find old Norwich postcodes of the form NOR number-number-letter
    # or old Newport postcodes of form NPT number-letter-letter but updated version does. Also,
    # the inward component changed to include 'V' in order to pick up NPT 0VA. Also, changed outward
    # regex to pick up W1 (as in W1 3PF) and WC99 (as in WC99 0LF and WC99 9AP.)
    # In the latest modification, the regex was changed so it consisted of two named components
    # recognising the outward (first half) and inward (second half) of the postcode. These
    # were compiled into a single regex, separated by whitespace (even though white space is
    # removed from the string before processing).

    postcodeOutwardRegex = '''(?P<postcodeOutward>(?:^GIR(?=\s*0AA$)) |                 # Identifies special postcode GIR 0AA
                                                  (?:^NOR(?=\s*[0-9][0-9][A-Z]$)) |     # Identifies old Norwich postcodes of format NOR number-number-letter
                                                  (?:^NPT(?=\s*[0-9][A-Z][A-Z]$)) |     # Identifies old Newport (South Wales) postcodes of format NPT number-letter-letter
                                                  (?:^(?:(?:A[BL]|B[ABDFHLNRSTX]?|C[ABFHMORTVW]|D[ADEGHLNTY]|E[HNX]?|F[KY]|G[LUY]?|H[ADGPRSUX]|I[GMPV]|JE|K[ATWY]|L[ADELNSU]?|M[EKL]?|N[EGNPRW]?|O[LX]|P[AEHLOR]|R[GHM]|S[AEGKLMNOPRSTY]?|T[ADFNQRSW]|UB|W[ADFNRSV]|YO|ZE)[1-9]?[0-9] |  # Identifies stardard outward code e.g. L4, L12, CH5, CH64
                                                      (?:(?:E|N|NW|SE|SW|W)1|EC[1-4]|WC[12])[A-HJKMNPR-Y]|(?:SW|W)(?:[1-9]|[1-9][0-9])|EC[1-9][0-9]|WC99))    # Identifies the odd London-based postcodes
                               )'''
    
    postcodeInwardRegex = '''(?P<postcodeInward>(?<=NOR)(?:\s*[0-9][0-9][A-Z]$) |      # Picks out the unusual format of old Norwich postcodes (including leading space)
                                                (?:[0-9][ABD-HJLNP-UVW-Z]{2}$)         # Picks out standard number-letter-letter end of postcode
                             )'''
    
    # KNOWN ISSUES
    # ============
    # The inward part of old Norwich postcodes may be returned with preceding white space.
    # This was because look behind can not be of variable length and, therefore, the
    # option of variable which space needed to be included in the captured group.
    #
    # The letter-letter combination in NPT areas currently allows all possible combinations
    # but this should be defined better.
    
    
    if phjPrintResults == True:
        print('\nOutward regex\n-------------\n{0}'.format(postcodeOutwardRegex))
        print('\nInward regex\n------------\n{0}'.format(postcodeInwardRegex))
        print('\n')
        
    return [postcodeOutwardRegex,postcodeInwardRegex]



def phjUKPostcodeRegexDefinition_DavidSingleton2017(phjPrintResults = False):
    # The following Regex was used by David Singleton and was originally given as:
    # ^((GIR 0AA)|((([A-PR-UWYZ][A-HK-Y]?[0-9][0-9]?)|(([A-PR-UWYZ][0-9][A-HJKSTUW])|([A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRV-Y]))) [0-9][ABD-HJLNP-UW-Z]{2}))$
    
    postcodeOutwardRegex = '''(?P<postcodeOutward>(?:^GIR(?=\s*0AA$)) |                 # Identifies special postcode GIR 0AA
                                                  (?:^(?:[A-PR-UWYZ][A-HK-Y]?[0-9][0-9]?)|(?:(?:[A-PR-UWYZ][0-9][A-HJKSTUW])|(?:[A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRV-Y])))
                               )'''
    
    postcodeInwardRegex = '''(?P<postcodeInward>(?:[0-9][ABD-HJLNP-UW-Z]{2}$)
                             )'''
    
    # KNOWN ISSUES
    # ============
    # Does not pick up old Norwich or Newport postcodes.
    # Does not pick up some London postcodes.
    
    
    if phjPrintResults == True:
        print('\nOutward regex\n-------------\n{0}'.format(postcodeOutwardRegex))
        print('\nInward regex\n------------\n{0}'.format(postcodeInwardRegex))
        print('\n')
        
    return [postcodeOutwardRegex,postcodeInwardRegex]



def phjGetPostcodeRegexGroupNamesList(phjPrintResults = False):
    # This function returns the names of regex groups as a list with the outward name first
    # and the inward name second.
    # Need to retrieve names from individual compiled regexes and add names to list one at a
    # time. If retrieve group names from complete regex in one go then the resulting
    # dictionary will contain names in unpredictable order (i.e. outward
    # group name may be after inward group name).
    postcodeOutwardRegex, postcodeInwardRegex = phjUKPostcodeRegexDefinition(phjPrintResults = False)
    
    postcodeOutwardRegex = re.compile(postcodeOutwardRegex,flags = re.I|re.X)
    postcodeOutwardRegexList = [k for k in postcodeOutwardRegex.groupindex.keys()]

    postcodeInwardRegex = re.compile(postcodeInwardRegex,flags = re.I|re.X)
    postcodeInwardRegexList = [k for k in postcodeInwardRegex.groupindex.keys()]
    
    # Combine into single list with outward name in first position and inward name in second position.
    phjRegexGroupNamesList = postcodeOutwardRegexList + postcodeInwardRegexList

    return phjRegexGroupNamesList



def phjGetCompiledPostcodeRegex(phjPostcodeComponent = 'all',
                                phjPrintResults = False):
    
    # This function returns returns a compiled regex for either the whole postcode regex
    # or a component of the postcode regex (outward or inward)
    
    # Retrieve postcode regex definitions for outward and inward parts and compile
    phjPostcodeOutwardRegex, phjPostcodeInwardRegex = phjUKPostcodeRegexDefinition(phjPrintResults = False)
    
    if phjPostcodeComponent == 'all':
        phjCompiledPostcodeRegex = re.compile(phjPostcodeOutwardRegex + '\s*' + phjPostcodeInwardRegex,flags = re.I|re.X)
    
    elif phjPostcodeComponent == 'outward':
        phjCompiledPostcodeRegex = re.compile(phjPostcodeOutwardRegex,flags = re.I|re.X)

    elif phjPostcodeComponent == 'inward':
        phjCompiledPostcodeRegex = re.compile(phjPostcodeInwardRegex,flags = re.I|re.X)

    else:
        print('phjPostcodeComponent option is invalid.')
        phjCompiledPostcodeRegex = None
    
    return phjCompiledPostcodeRegex



def phjUKPostcodeRealityCheck(phjTempDF,
                              phjRealPostcodeArr = None,
                              phjNewPostcodeVarName = 'postcodeClean',
                              phjPostcodeCheckVarName = 'postcodeCheck',
                              phjMissingValueCode = 'missing',
                              phjPrintResults = False):
    
    # This function populates the phjPostcodeCheckVarName column in the passed dataframe to indicate
    # (True or False) whether the postcode string exists in the array of real postcodes. Only those
    # rows that are null or False are tested (it is assummed that previously matched strings do not
    # need to be retested.

    if phjRealPostcodeArr is not None:
        phjTempDF.loc[((phjTempDF[phjPostcodeCheckVarName].isnull())|
                       (phjTempDF[phjPostcodeCheckVarName]==False))&
                      (phjTempDF[phjNewPostcodeVarName]!=phjMissingValueCode),[phjPostcodeCheckVarName]] = phjTempDF[phjNewPostcodeVarName].isin(phjRealPostcodeArr)
    
    else:
        phjTempDF = None
        
    return phjTempDF
    

    
def phjUKPostcodeFormatCheck(phjTempDF,
                             phjNewPostcodeVarName = 'postcodeClean',
                             phjPostcodeCheckVarName = 'postcodeCheck',
                             phjMissingValueCode = 'missing',
                             phjPostcodeComponent = 'all',
                             phjPrintResults = False):
    
    # This function populates the phjPostcodeCheckVarName column in the passed dataframe to indicate
    # (True or False) whether the postcode string matches the regex format. Only those rows that are
    # null or False are tested (it is assummed that previously matched strings do not need to be
    # retested.
    
    # The regex used for matching can be either the whole regex or a component (outward or inward).
    phjCompiledPostcodeRegex = phjGetCompiledPostcodeRegex(phjPostcodeComponent = phjPostcodeComponent,
                                                           phjPrintResults = False)
    
    # For those rows where the phjPostcodeCheckVarName column is null or False, if the
    # postcode string format matches the regex, enter True in phjPostcodeCheckVarName; else
    # enter False.
    if phjCompiledPostcodeRegex is not None:
        phjTempDF.loc[((phjTempDF[phjPostcodeCheckVarName].isnull())|
                       (phjTempDF[phjPostcodeCheckVarName]==False))&
                      (phjTempDF[phjNewPostcodeVarName]!=phjMissingValueCode),[phjPostcodeCheckVarName]] = phjTempDF[phjNewPostcodeVarName].str.contains(phjCompiledPostcodeRegex,na = False)

    return phjTempDF



def phjExtractPostcodeComponents(phjTempDF,
                                 phjNewPostcodeVarName = 'postcodeClean',
                                 phjPostcodeCheckVarName = 'postcodeCheck',
                                 phjPostcodeComponent = 'all',
                                 phjPrintResults = False):
    
    # This function returns postcode components from a variable containing postcode strings
    # based on named groups in the postcode regex.
    
    # Retrieve postcode regex definition names and compiled regex for appropriate postcode components.
    postcodeOutwardRegex, postcodeInwardRegex = phjUKPostcodeRegexDefinition(phjPrintResults = False)
    phjCompiledPostcodeRegex = phjGetCompiledPostcodeRegex(phjPostcodeComponent = phjPostcodeComponent,
                                                           phjPrintResults = False)
    
    # Create a temporary dataframe that contains extracted postcode components
    phjPostcodeComponentsDF = phjTempDF.loc[phjTempDF[phjPostcodeCheckVarName] == True,phjNewPostcodeVarName].str.extract(phjCompiledPostcodeRegex,
                                                                                                                                expand = True)
    # Add extracted postcode component(s) to original dataframe.
    # If the columns containing extracted data already exist in the database, then the
    # DataFrame.update() function can be used to update non-NA values. This may occur if,
    # for example, the function has already been run on a slice of the original dataframe.
    # If the columns do not already exist, then need to add new columns using DataFrame.join().
    # New columns are added one column at a time to avoid theoretical issues where one column
    # exists and the other does not.
    for phjCol in phjPostcodeComponentsDF.columns:
        if phjCol in phjTempDF.columns:
            phjTempDF.update(phjPostcodeComponentsDF.loc[:,[phjCol]])
        else:
            phjTempDF = phjTempDF.join(phjPostcodeComponentsDF.loc[:,[phjCol]])
    
    return phjTempDF



def phjUKPostcodeCorrectCommonErrors(phjTempDF,
                                     phjNewPostcodeVarName = 'postcodeClean',
                                     phjPostcodeCheckVarName = 'postcodeCheck',
                                     phjMissingValueCode = 'missing',
                                     phjPrintResults = False):
    
    # Creates a temporary dataframe containing incorrectly formatted postcodes only.
    # Common errors will be corrected and merged back to the original dataframe.
    phjTempUnformattedDF = phjTempDF.loc[(phjTempDF[phjPostcodeCheckVarName] == False) &
                                         (phjTempDF[phjNewPostcodeVarName].notnull()),[phjNewPostcodeVarName,phjPostcodeCheckVarName]]
    
    phjTempUnformattedDF[phjNewPostcodeVarName] = phjTempUnformattedDF[phjNewPostcodeVarName].map(lambda x: phjCorrectPostcodeErrors(x,
                                                                                                                                     phjMissingValueCode = phjMissingValueCode,
                                                                                                                                     phjRun = 1))

    # Update dataframe with newly corrected postcode strings. However, DataFrame.update() does not
    # update values that have been returned as NaN and, therefore, the missing value code must not
    # be set to np.nan.
    phjTempDF.update(phjTempUnformattedDF)
    
    return phjTempDF



def phjCorrectPostcodeErrors(x,
                             phjMissingValueCode = 'missing',
                             phjRun = 1):
    
    # This function is called by a lambda function. The lambda function steps through
    # postcode strings and substitutions are made at specific positions based on a
    # lookup dictionary.
    # N.B. The phjRun variable is not currently used but allows the option for several
    # rounds of error-corrections (using different lookup dictionaries) to be made
    # to try to salvage correctly formatted postcode strings (if required).
    
    # Make sure the postcode string does not contain white space or punctuation and is
    # converted to upper-case (this should have already been done but, hey, belt and braces.)
    x = re.sub(r'''[\W_]+''','',x.upper())
    
    # Convert string to list
    phjStrList = list(x)
    
    # Define dictionary of alpha->num and num->alpha conversions.
    # It would probably be better to define this outside the lambda
    # function so the dictionary does not have to be defined repeatedly.
    phjPostcodeReplacementsDict = {'alpha2num': {'B': '8',
                                                 'I': '1',
                                                 'L': '1',
                                                 'O': '0',
                                                 'S': '5',
                                                 'Z': '2'},
                                   'num2alpha': {'0': 'O',
                                                 '1': 'I',
                                                 '2': 'Z',
                                                 '5': 'S',
                                                 '8': 'B'} }
    
    # If string is 5-7 characters long, it is possible that the
    # postcode has been entered incorrectly. Therefore, try to correct
    # any common errors.
    if (len(x)>=5 and len(x)<=7):
        
        # Inward part of postcode (i.e. second half)
        # -----------------------
        # (The final 3 characters should be number-letter-letter.)
        
        # Third character from end (i.e. first character of inward part) should be a number
        phjStrList[-3] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[-3],phjStrList[-3])
        
        # Second character from end and final character should be letters
        phjStrList[-2] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[-2],phjStrList[-2])
        phjStrList[-1] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[-1],phjStrList[-1])
        
        # Outward part of postcode (i.e. first half of postcode)
        # ------------------------
        # First character (index=0) should always be a letter; assume this is always entered as a letter.
        if len(x)==5:
            # If string is 5 characters long then second character (index=1) should be a number
            phjStrList[0] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[0],phjStrList[0])
            phjStrList[1] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[1],phjStrList[1])
            
        elif len(x)==6:
            # Second character (index=1) could be either a letter or a number - therefore, leave unchanged.
            # Third character (index=2) should be a number
            phjStrList[0] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[0],phjStrList[0])
            phjStrList[2] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[2],phjStrList[2])
            
        else:
            # Second character (index=1) should be a letter
            # Third character (index=2) should be a number
            # Fourth character (index=3) should be a number
            phjStrList[0] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[0],phjStrList[0])
            phjStrList[1] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[1],phjStrList[1])
            phjStrList[2] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[2],phjStrList[2])
            phjStrList[3] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[3],phjStrList[3])
        
        phjReturnStr = ''.join(phjStrList)
        
        
    elif (len(x)>=2 and len(x)<=4):
        # This could be the outward part of the postcode
        # First character (index=0) should always be a letter.
        if len(x)==2:
            # If string is 2 characters long then second character (index=1) should be a number
            phjStrList[0] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[0],phjStrList[0])
            phjStrList[1] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[1],phjStrList[1])
            
        elif len(x)==3:
            # Second character (index=1) could be either a letter or a number - therefore, leave unchanged.
            # Third character (index=2) should be a number
            phjStrList[0] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[0],phjStrList[0])
            phjStrList[2] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[2],phjStrList[2])
            
        else:
            # Second character (index=1) should be a letter
            # Third character (index=2) should be a number
            # Fourth character (index=3) should be a number
            phjStrList[0] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[0],phjStrList[0])
            phjStrList[1] = phjPostcodeReplacementsDict['num2alpha'].get(phjStrList[1],phjStrList[1])
            phjStrList[2] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[2],phjStrList[2])
            phjStrList[3] = phjPostcodeReplacementsDict['alpha2num'].get(phjStrList[3],phjStrList[3])
            
        phjReturnStr = ''.join(phjStrList)
        
    else:
        # Postcode strings that are 1 character long or greater than 7 characters (excluding
        # white space and punctuation) are probably beyond all hope and are treated as missing.
        phjReturnStr = phjMissingValueCode
        
    return phjReturnStr



def phjPostcodeFormat7(phjTempDF,
                       phjNewPostcodeVarName = 'postcodeClean',
                       phjPostcodeCheckVarName = 'postcodeCheck',
                       phjPostcode7VarName = 'postcode7',
                       phjPrintResults = False):
    
    # This function creates a variable containing correctly formatted whole postcodes
    # in 7-character format. This format is commonly used in lookup tables that link
    # postcodes to other geographical data.
    
    # Copy correctly formatted WHOLE postcode strings to postcode7 variable
    phjTempDF[phjPostcode7VarName] = phjTempDF.loc[(phjTempDF[phjPostcodeCheckVarName] == True) &
                                                   (phjTempDF[phjNewPostcodeVarName].str.len() >= 5) &
                                                   (phjTempDF[phjNewPostcodeVarName].str.len() <= 7),phjNewPostcodeVarName]
    
    # Reformat postcode7 variable to 7 characters
    phjTempDF[phjPostcode7VarName] = phjTempDF[phjPostcode7VarName].str.replace(' ','').str.replace('(\w{3})$',r' \1').str.replace('^(\w{2}\s)',r'\1 ').str.replace('^(\w{4})\s',r'\1')
    
    return phjTempDF



def phjSalvagePostcode(phjTempDF,
                       phjNewPostcodeVarName = 'postcodeClean',
                       phjPostcodeCheckVarName = 'postcodeCheck',
                       phjMissingValueCode = 'missing',
                       phjPrintResults = False):
    
    phjNumberOfCorrectionRuns = 3
    
    # Create a temporary dataframe containing hitherto incorrectly formatted postcodes only.
    # Common errors will be corrected and outward postcode component will be test to determine
    # whether format is correct.
    phjTempUnformattedDF = phjTempDF.loc[(phjTempDF[phjPostcodeCheckVarName] == False) &
                                         (phjTempDF[phjNewPostcodeVarName].notnull()),[phjNewPostcodeVarName,
                                                                                       phjPostcodeCheckVarName]].copy()
    
    for i in range(1,phjNumberOfCorrectionRuns+1):
        # Create a scatch dataframe consisting of postcode entries that are not matched with regex (in this
        # case, just the outward component).
        phjTempScratchDF = phjTempUnformattedDF.loc[phjTempUnformattedDF[phjPostcodeCheckVarName] == False,:].copy()

        # Check if the incorrectly formatted postcode contains a valid outward postcode component at the start.
        # If so, the phjPostcodeCheckVarName variable will be set to True.
        phjTempScratchDF = phjUKPostcodeFormatCheck(phjTempDF = phjTempScratchDF,
                                                    phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                    phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                    phjPostcodeComponent = 'outward',
                                                    phjPrintResults = False)

        if i < phjNumberOfCorrectionRuns:
            # Correct common errors in postcodes that are still recorded as incorrectly formatted
            phjTempScratchDF[phjNewPostcodeVarName] = phjTempScratchDF[phjNewPostcodeVarName].map(lambda x: phjCorrectPostcodeErrors(x,
                                                                                                                                     phjMissingValueCode = phjMissingValueCode,
                                                                                                                                     phjRun = i))
        
        # Update phjTempUnformattedDF with changed variables in nphjTempScratchDF.
        # N.B. The DataFrame.updata() function does NOT update non
        phjTempUnformattedDF.update(phjTempScratchDF)
        
    # Update postcodeOutward variable with extracted contents of phjNewPostcodeVarName if format
    # matches with outward regex
    phjTempUnformattedDF = phjExtractPostcodeComponents(phjTempDF = phjTempUnformattedDF,
                                                        phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                        phjPostcodeCheckVarName = phjPostcodeCheckVarName,
                                                        phjPostcodeComponent = 'outward',
                                                        phjPrintResults = False)
    
    
    # If unformatted postcode strings have a correctly formatted outward postcode component extracted
    # from the original string, then the extracted string should be copied to the postcodeClean variable.
    
    # Retrieve postcode regex definition names.
    phjRegexGroupNamesList = phjGetPostcodeRegexGroupNamesList(phjPrintResults = False)
    
    if phjRegexGroupNamesList[0] in phjTempUnformattedDF.columns:
        phjTempUnformattedDF.loc[phjTempUnformattedDF[phjPostcodeCheckVarName] == True,phjNewPostcodeVarName] = phjTempUnformattedDF[phjRegexGroupNamesList[0]]
    
    
    # Update dataframe with newly corrected columns (phjNewPostcodeVarName and phjPostcodeCheckVarName)
    phjTempDF.update(phjTempUnformattedDF)
    
    return phjTempDF



def phjExtractPostcodeArea(phjTempDF,
                           phjPostcodeAreaVarName = 'postcodeArea',
                           phjPrintResults = False):
    
    # Retrieve list of names of regex groups and identify name of outward postcode variable
    phjRegexGroupNamesList = phjGetPostcodeRegexGroupNamesList(phjPrintResults = False)
    phjPostcodeOutwardVarName = phjRegexGroupNamesList[0]
    
    phjTempDF[phjPostcodeAreaVarName] = phjTempDF[phjPostcodeOutwardVarName].str.extract(re.compile('''(^[A-Z]+)''',flags=re.I),
                                                                                         expand = True)
    
    return phjTempDF


def phjGetBestAlternativePostcodes(phjTempDF,
                                   phjRealPostcodeArr = None,
                                   phjNewPostcodeVarName = 'postcodeClean',
                                   phjNewPostcodeStrLenVarName = 'postcodeCleanStrLen',
                                   phjPostcodeCheckVarName = 'postcodeCheck',
                                   phjMinDamerauLevenshteinDistanceVarName = 'minDamLevDist',
                                   phjBestAlternativesVarName = 'bestAlternatives',):
    
    phjTempDF[phjMinDamerauLevenshteinDistanceVarName] = np.nan
    phjTempDF[phjBestAlternativesVarName] = np.nan
    
    # Take slice dataframe and apply lambda function to calculate minimum Damerau-Levenshtein distance.
    # This may not be the best way to do this - perhaps define a slice of the dataframe under a different
    # name, apply the function and then update the original.
#    phjTempDF.loc[(phjTempDF[phjPostcodeCheckVarName] == False) &
#                  (phjTempDF[phjNewPostcodeVarName] != 'missing') &
#                  ((phjTempDF[phjNewPostcodeStrLenVarName] >= 4) &
#                   (phjTempDF[phjNewPostcodeStrLenVarName] <= 8)),[phjMinDamerauLevenshteinDistanceVarName]] = phjTempDF.loc[(phjTempDF[phjPostcodeCheckVarName] == False) &
#                                                                                                                             (phjTempDF[phjNewPostcodeVarName] != 'missing') &
#                                                                                                                             ((phjTempDF[phjNewPostcodeStrLenVarName] >= 4) &
#                                                                                                                              (phjTempDF[phjNewPostcodeStrLenVarName] <= 8)),:].apply(lambda x: phjGetMinDLDist(x,
#                                                                                                                                                                                                                phjNewPostcodeVarName = phjNewPostcodeVarName,
#                                                                                                                                                                                                                phjRealPostcodeArr = phjRealPostcodeArr),axis = 1)
    
    # Slice dataframe so it contains just corrected postcode strings between 4 and 8 characters long,
    # excluding 'missing', and which are not contained in the real postcode array.
    phjScratchDF = phjTempDF.loc[(phjTempDF[phjPostcodeCheckVarName] == False) &
                                 (phjTempDF[phjNewPostcodeVarName] != 'missing') &
                                 ((phjTempDF[phjNewPostcodeStrLenVarName] >= 4) &
                                  (phjTempDF[phjNewPostcodeStrLenVarName] <= 8)),:]
    
    
    # Calculate the minimum DL distance for the postcode being check (assessed against array of all postcodes)
    phjScratchDF[[phjMinDamerauLevenshteinDistanceVarName,
                  phjBestAlternativesVarName]] = phjScratchDF.apply(lambda x: phjCalcMinDamLevDistAndEdits(x,
                                                                                                           phjRealPostcodeArr = phjRealPostcodeArr,
                                                                                                           phjNewPostcodeVarName = phjNewPostcodeVarName,
                                                                                                           phjAllowedEdits = 1),axis = 1)
    
    phjTempDF.update(phjScratchDF)
    
    return phjTempDF


def phjCalcMinDamLevDistAndEdits(x,
                                 phjRealPostcodeArr = None,
                                 phjNewPostcodeVarName = 'postcodeClean',
                                 phjAllowedEdits = 1):
    
    print("Consider first postcode entry:",x[phjNewPostcodeVarName])
    
    # Convert the numpy array of postcodes to a Pandas dataframe
    phjPostcodeDF = pd.DataFrame(phjRealPostcodeArr,columns = ['pcdMin'])
    
    # Calculate distance from string to each postcode in dataframe
    phjPostcodeDF['tempDL'] = pyxdl.damerau_levenshtein_distance_ndarray(x[phjNewPostcodeVarName], phjRealPostcodeArr)
    
    # Calculate minimum DL distance
    phjMinDamLevDist = phjPostcodeDF['tempDL'].min(axis = 0)
    
    # If the minimum number of edits detected is less than or equal to the allowed number of edits 
    # then copy all those postcodes with the minimum number of edits to a temporary dataframe
    if phjMinDamLevDist <= phjAllowedEdits:
        phjPossPostcodesScratchDF = phjPostcodeDF.loc[phjPostcodeDF['tempDL'] == phjMinDamLevDist,:].copy()
        
        # For example:
        #
        #         pcdMin  tempDL
        #1549655  NN40GH       1
        #1574077  NP40AH       1
        #1574096  NP40BH       1
        #1574123  NP40HG       1
        #...

        #phjScratchDF['editCodes'] = phjScratchDF.apply(lambda row: phjDamerauLevenshteinEdits(phjStr1 = x[phjNewPostcodeVarName],
        #                                                                                      phjStr2 = row['pcdMin'],
        #                                                                                      phjCleanInputStrings = False,
        #                                                                                      phjIncludeEquivalenceEdits = False),axis=1)
        
        
        # N.B. Apply runs the functions on the first row twice to intelligently determine
        # whether it can take a fast or slow code path. Do not be alarmed if the results for
        # the first row are displayed twice in the output code.
        phjPossPostcodesScratchDF['editCodes'] = phjPossPostcodesScratchDF.apply(lambda row: phjCallDLEditsFunction(row,
                                                                                                                    phjStr1 = x[phjNewPostcodeVarName],
                                                                                                                    phjColHeading = 'pcdMin',
                                                                                                                    phjCleanInputStrings = False,
                                                                                                                    phjIncludeEquivalenceEdits = False),axis=1)

        
        
                
        phjPossPostcodesScratchDF['adjEdits'] = phjPossPostcodesScratchDF['editCodes'].map(lambda cell: phjAdjustEditCost(phjEditsList = cell))
    
        phjPossPostcodesScratchDF = phjPossPostcodesScratchDF.sort_values('adjEdits', axis=0, ascending=True, na_position='last')
        
        phjPossPostcodesList = phjPossPostcodesScratchDF['pcdMin'].head(3).tolist()
        
    else:
        phjPossPostcodesList = None
    
    print('   Returned list of edits: {0}\n'.format([phjMinDamLevDist,phjPossPostcodesList]))
    
    return pd.Series([phjMinDamLevDist,phjPossPostcodesList],index=['minDamLevDist','bestAlternatives'])


def phjCallDLEditsFunction(row,
                           phjStr1,
                           phjColHeading = 'pcd',
                           phjCleanInputStrings = True,
                           phjIncludeEquivalenceEdits = False):
    
    # This function was introduced simply to link the lambda function call to the
    # phjDamerauLevenshteinEdits() function. This was because function was written in a very
    # generic way to be able to compare two strings.
    
    phjEditList = phjDamerauLevenshteinEdits(phjStr1 = phjStr1,
                                             phjStr2 = row[phjColHeading],
                                             phjCleanInputStrings = phjCleanInputStrings,
                                             phjIncludeEquivalenceEdits = phjIncludeEquivalenceEdits)
    
    return phjEditList


def phjDamerauLevenshteinEdits(phjStr1,
                               phjStr2,
                               phjCleanInputStrings = True,
                               phjIncludeEquivalenceEdits = True):
    
    # Edit strings to remove white space and punctuation
    # and convert to uppercase
    if phjCleanInputStrings == True:
        phjStr1 = re.sub(r'''[\W_]''','',phjStr1.upper())
        phjStr2 = re.sub(r'''[\W_]''','',phjStr2.upper())
        
    # Create one-indexed Pandas arrays for input strings
    a = pd.Series(list(phjStr1),index=(range(1,len(phjStr1)+1)))
    b = pd.Series(list(phjStr2),index=(range(1,len(phjStr2)+1)))
    
    # Get Damerau-Levenshtein matrix
    d = phjDamerauLevenshteinMatrix(a = phjStr1,
                                    b = phjStr2)
    
    # Start in bottom right cell of DL matrix and walk through matrix
    # to calculate list of edits.
    # List of edits is created in reverse order.
    i = len(a)
    j = len(b)
    
    phjEditList = []

    while (i>0) | (j>0):
        
        if (i==0) | (j==0):
            # If either i==0 or j==0 then the path through the matrix has come up against
            # the edge of the table. Subsequent edits will therefore be either all
            # insertions (i==0) or all deletions (j==0)
            if (i==0):
                # An insertion at the very start of the string is coded here and the
                # code ia>b should be read as "insert 'a' between the start of the
                # string and 'b'". Other insertions are encoded below.
                if (d.loc[i,j] - d.loc[i,j-1] == 1):
                    phjEditList = ['i'+b[j]+'>'+a[i+1]] + phjEditList
                    # Move one cell to the left
                    i = i
                    j = j-1
                    
            # Or if j==0       
            else:
                if (d.loc[i,j] - d.loc[i-1,j] == 1):
                    phjEditList = ['d'+a[i]] + phjEditList
                    # Move one cell up
                    i = i-1
                    j = j

        else:
            # The characters at current position in first and second strings are the same
            if (a[i] == b[j]):
                # If the number of edits in the current cell is the same as the north-west cell
                # then this is an equivalence
                if d.loc[i,j] == d.loc[i-1,j-1]:
                    if phjIncludeEquivalenceEdits == True:
                        phjEditList = ['e'+a[i]+b[j]] + phjEditList
                    # Move to cell [i-1,j-1]
                    i = i-1
                    j = j-1

            # The characters at the current position in first and second strings are NOT the same
            else:
                # If the number of edits in the current cell is the same as the number in the
                # cells to the west, north-west and north (i.e. forming a square containing
                # equal numbers) then this represents a TRANSPOSITION of adjacent characters
                if (d.loc[i,j] == d.loc[i,j-1]) & (d.loc[i,j] == d.loc[i-1,j-1]) & (d.loc[i,j] == d.loc[i-1,j]):
                    phjEditList = ['t'+a[i-1]+a[i]] + phjEditList
                    # Move to cell [i-2,j-2]
                    i = i-2
                    j = j-2

                # If cell to the west is one edit less than current cell then this
                # is an INSERTION.
                # The code iabc should be read as "insert 'a' between 'b' and 'c'".
                # If the insertion is at the very end of the string then the code
                # iab< should be read as "insert 'a' between 'b' and the end of the
                # string.
                # An insertion at the very start of the string is coded above and the
                # code ia>b should be read as "insert 'a' between the start of the
                # string and 'b'".
                elif (d.loc[i,j] - d.loc[i,j-1] == 1):
                    if i == len(a):
                        phjEditList = ['i'+b[j]+a[i]+'<'] + phjEditList
                    else:
                        phjEditList = ['i'+b[j]+a[i]+a[i+1]] + phjEditList
                    # Move one cell to the left
                    i = i
                    j = j-1

                # If cell to the north-west is one edit less than current cell then this
                # is a SUBSTITUTION
                elif (d.loc[i,j] - d.loc[i-1,j-1] == 1):
                    phjEditList = ['s'+a[i]+b[j]] + phjEditList
                    # Move one cell to the left and one cell up
                    i = i-1
                    j = j-1

                # If cell to the north is one edit less than current cell then this
                # is a DELETION
                elif (d.loc[i,j] - d.loc[i-1,j] == 1):
                    phjEditList = ['d'+a[i]] + phjEditList
                    # Move one cell up
                    i = i-1
                    j = j

                # Else exit the loop
                else:
                    i = 0
                    j = 0
    
    
    return phjEditList


def phjDamerauLevenshteinMatrix(a,b):
    
    '''
    The following description of the algorithm in pseudocode used to calculate the Damerau-Levenshtein
    matrix was taken from Wikipedia (see: https://en.wikipedia.org/wiki/Damerau–Levenshtein_distance),
    accessed July 2017.
    
    
    algorithm DL-distance is
    input: strings a[1..length(a)], b[1..length(b)]
    output: distance, integer

    da := new array of |Σ| integers
    for i := 1 to |Σ| inclusive do
        da[i] := 0

    let d[−1..length(a), −1..length(b)] be a 2-d array of integers, dimensions length(a)+2, length(b)+2
    // note that d has indices starting at −1, while a, b and da are one-indexed.

    maxdist := length(a) + length(b)
    d[−1, −1] := maxdist
    for i := 0 to length(a) inclusive do
        d[i, −1] := maxdist
        d[i, 0] := i
    for j := 0 to length(b) inclusive do
        d[−1, j] := maxdist
        d[0, j] := j

    for i := 1 to length(a) inclusive do
        db := 0
        for j := 1 to length(b) inclusive do
            k := da[b[j]]
            ℓ := db
            if a[i] = b[j] then
                cost := 0
                db := j
            else
                cost := 1
            d[i, j] := minimum(d[i−1, j−1] + cost,  //substitution
                               d[i,   j−1] + 1,     //insertion
                               d[i−1, j  ] + 1,     //deletion
                               d[k−1, ℓ−1] + (i−k−1) + 1 + (j-ℓ−1)) //transposition
        da[a[i]] := i
    return d[length(a), length(b)]
    
    '''
    
    # Create one-indexed Pandas arrays for input strings
    a = pd.Series(list(a),index=(range(1,len(a)+1)))
    b = pd.Series(list(b),index=(range(1,len(b)+1)))
    
    # Create an alphabet list containing all unique characters used in input strings.
    # This is done by converting a list to a set (which is unique values) and then
    # converting back to a list. Note that the final list is unordered because sets
    # are unordered.
    sigma = list(set(list(a)+list(b)))
    
    # Create da variable, indexed by alphabet characters
    da = pd.Series([0]*len(sigma),index=sigma)
    
    # Create a Pandas dataframe with index and column ranging from -1 to length of string
    index=list(range(-1,len(a)+1))
    columns=list(range(-1,len(b)+1))
    d=pd.DataFrame(index=index,columns=columns)
    
    # Enter maximum distance into cell [-1,-1]
    maxdist=len(a)+len(b)
    d.loc[-1,-1]=maxdist
    
    # Enter maximum distance in top row and leftmost column
    # and enter the number of edits when one of the strings is empty
    for i in range(0,len(a)+1):
        d.loc[i,-1]=maxdist
        d.loc[i,0]=i
    
    for j in range(0,len(b)+1):
        d.loc[-1,j]=maxdist
        d.loc[0,j]=j
    
    # Fill in rest of table
    for i in range(1,len(a)+1):
        db=0
        for j in range(1,len(b)+1):
            k=da[b[j]]
            l=db
            if a[i] == b[j]:
                cost=0
                db=j
            else:
                cost=1
            d.loc[i,j]=min(d.loc[i-1,j-1]+cost,
                           d.loc[i,j-1]+1,
                           d.loc[i-1,j]+1,
                           d.loc[k-1,l-1]+(i-k-1)+1+(j-l-1))
        da[a[i]]=i
    
    # After the matrix has been calculated, label the rows and columns with string characters
    d.loc[-1,-1] = 's1'
    d.loc[0,-1] = '↓'
    d.loc[-1,0] = 's2 →'

    for i in range(1,len(a)+1):
        d.loc[i,-1]=a[i]

    for j in range(1,len(b)+1):
        d.loc[-1,j]=b[j]
    
    return d


def phjAdjustEditCost(phjEditsList):
    # Create dataframe containing one character per column, the first of which will be
    # the type of edit, either e, s, i or d.
    
    # i. Identify how many columns will be required (e.g. ['edit','key1','key2','key3])
    phjMaxChars = len(max(phjEditsList, key=len))
    phjColumnHeadings = ['edit']
    for i in range(1,phjMaxChars):
        phjColumnHeadings = phjColumnHeadings + ['key'+str(i)]
    
    # ii. Import each character of each string in the list into the dataframe
    phjEditDF = pd.DataFrame([list(edit) for edit in phjEditsList],columns=phjColumnHeadings)

    # Set adjCost column to 1 for all edits except equivalents (i.e. 'e') which is set to zero
    phjEditDF['cost'] = np.where(phjEditDF['edit']!='e',1,0)
    
    # Add a oolumn for adjusted edit costs
    phjEditDF['adjCost'] = np.nan

    # ...then add weighting of cost depending on key separation
    phjEditDF['adjCost'] = phjEditDF.apply(lambda row: phjCalcAdjEditCost(row),axis = 1)

    return phjEditDF['adjCost'].sum()


def phjCalcAdjEditCost(row):
    # Edit types 'e' (equivalence), 't' (transposition) and 'd' (deletion)
    # require no adjustment (i.e. adjCost is the same as cost)
    if (row['edit'] == 'e') or (row['edit'] == 't') or (row['edit'] == 'd'):
        phjAdjCost = row['cost']
    
    # If edit type is 's' (substitution) then adjust cost based on
    # distance between keys
    elif (row['edit'] == 's'):
        phjAdjCost = phjKeyDistance(phjKey1 = row['key1'],
                                    phjKey2 = row['key2'],
                                    phjKeyboardType = 'qwerty')
    
    # If edit type is 'i' (insertion) then need to adjust cost based on the difference
    # in phystical distance between the key before and the key after; the adjusted
    # cost is the minimum of these two values. If the inserted key stroke is identical
    # to either the character before or the character after, the adjusted cost is 1 (even though
    # the physical difference is zero).
    # Most insertions will be of the form iABC (i.e. 'A' inserted between 'B' and 'C')
    # Insertions at the start of the string will be of the form iA>B, where '>' represents the start of the sting.
    # Insertions at the end of the string will be of the form iAB<, where '<' represents the end of the string.
    elif (row['edit'] == 'i'):
        # If insertion at start of string then only compare key1 and key3
        if (row['key2'] == '>'):
            phjAdjCost = phjKeyDistance(phjKey1 = row['key1'],
                                        phjKey2 = row['key3'],
                                        phjKeyboardType = 'qwerty')
        
        # If insertion at end of string then only compare key1 and key2
        elif (row['key3'] == '<'):
            phjAdjCost = phjKeyDistance(phjKey1 = row['key1'],
                                        phjKey2 = row['key2'],
                                        phjKeyboardType = 'qwerty')
        
        # Most insertions will be mid string and therefore need to adjust cost
        # based on the minimum between key1 and key2 and key1 and key3
        else:
            if (row['key1'] == row['key2']):
                phjAdjCostA = 1
                
            else:
                phjAdjCostA = phjKeyDistance(phjKey1 = row['key1'],
                                             phjKey2 = row['key2'],
                                             phjKeyboardType = 'qwerty')
            
            
            if (row['key1'] == row['key3']):
                phjAdjCostB = 1
                
            else:
                phjAdjCostB = phjKeyDistance(phjKey1 = row['key1'],
                                             phjKey2 = row['key3'],
                                             phjKeyboardType = 'qwerty')

            phjAdjCost = min(phjAdjCostA,phjAdjCostB)
            
    
    return phjAdjCost


# Distance between keys calculated using co-ordinate geometry
# and Pythagoras' theorem
def phjKeyDistance(phjKey1,
                   phjKey2,
                   phjKeyboardType = 'qwerty'):
    
    phjKeyboardCoords = phjDefineKeyboardCoords(phjKeyboardType = phjKeyboardType)
    
    if phjKeyboardCoords is not None:
        phjKey1Coords = phjKeyboardCoords[phjKey1]
        phjKey2Coords = phjKeyboardCoords[phjKey2]
        
        phjDist = math.sqrt(math.pow((phjKey1Coords[0] - phjKey2Coords[0]),2) + math.pow((phjKey1Coords[1] - phjKey2Coords[1]),2))
    
    else:
        phjDist = None
        
    return phjDist


def phjDefineKeyboardCoords(phjKeyboardType = 'qwerty'):
    
    if phjKeyboardType == 'qwerty':
        # QWERTY keyboard co-ordinates
        # Keyboard set out with following assumptions:
        # i.   There are 4 rows, equally spaced and numbered 0, 1, 2 and 3
        # ii.  Centre point for '1' key is [0,0]
        # iii. Centre point for 'Q' is off-set to the right by 0.5 units (therefore [1,0.5])
        # iv.  Centre point for 'A' is off-set to the right by a further 0.25 units (therefore [2,0.75])
        # v.   Centre point for 'Z' is off-set to the right by a further 0.5 units, therefore [3,1.25]

        phjKeyboardCoords = {'1':[0,0],
                             '2':[0,1],
                             '3':[0,2],
                             '4':[0,3],
                             '5':[0,4],
                             '6':[0,5],
                             '7':[0,6],
                             '8':[0,7],
                             '9':[0,8],
                             '0':[0,9],
                             'Q':[1,0.5],
                             'W':[1,1.5],
                             'E':[1,2.5],
                             'R':[1,3.5],
                             'T':[1,4.5],
                             'Y':[1,5.5],
                             'U':[1,6.5],
                             'I':[1,7.5],
                             'O':[1,8.5],
                             'P':[1,9.5],
                             'A':[2,0.75],
                             'S':[2,1.75],
                             'D':[2,2.75],
                             'F':[2,3.75],
                             'G':[2,4.75],
                             'H':[2,5.75],
                             'J':[2,6.75],
                             'K':[2,7.75],
                             'L':[2,8.75],
                             'Z':[3,1.25],
                             'X':[3,2.25],
                             'C':[3,3.25],
                             'V':[3,4.25],
                             'B':[3,5.25],
                             'N':[3,6.25],
                             'M':[3,7.25]}
    
    else:
        print("Keyboard '{0}' is not a recognised.".format(phjKeyboardType))
        
        phjKeyboardCoords = None
        
    return phjKeyboardCoords


if __name__ == '__main__':
    main()
