# These are the functions that can be accessed from epydemiology.
# Other functions that are used internally cannot be accessed
# directly by end-users.
from .phjGetData import phjReadDataFromExcelNamedCellRange

from .phjGetDBData import phjConnectToDatabase
from .phjGetDBData import phjGetDataFromDatabase

from .phjMiscFuncs import phjGetStrFromArgOrFile
from .phjMiscFuncs import phjReadTextFromFile
from .phjMiscFuncs import phjCreateNamedGroupRegex
from .phjMiscFuncs import phjFindRegexNamedGroups
from .phjMiscFuncs import phjMaxLevelOfTaxonomicDetail
from .phjMiscFuncs import phjReverseMap
from .phjMiscFuncs import phjRetrieveUniqueFromMultiDataFrames
from .phjMiscFuncs import phjUpdateLUT
from .phjMiscFuncs import phjUpdateLUTToLatestValues

from .phjMatrices import phjBinaryVarsToSquareMatrix
from .phjMatrices import phjLongToWideBinary

from .phjCalculateProportions import phjCalculateBinomialProportions
from .phjCalculateProportions import phjCalculateBinomialConfInts
from .phjCalculateProportions import phjCalculateMultinomialProportions
from .phjCalculateProportions import phjSummaryTableToBinaryOutcomes
from .phjCalculateProportions import phjAnnualDiseaseTrend

from .phjCleanUKPostcodes import phjCleanUKPostcodeVariable
from .phjCleanUKPostcodes import phjPostcodeFormat7

from .phjCleanData import phjParseDateVar

from .phjExploreData import phjViewLogOdds
from .phjExploreData import phjCategoriseContinuousVariable

from .phjExtFuncs import getJenksBreaks

from .phjRROR import phjOddsRatio
from .phjRROR import phjRelativeRisk

from .phjSelectData import phjSelectCaseControlDataset
from .phjSelectData import phjGenerateCaseControlDataset
from .phjSelectData import phjCollapseOnPatientID
