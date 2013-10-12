""" Match the CPS data with BLS data based on MSA
to output poverty rate and community worker presence by region"""

import pandas as pd
import numpy as np

def read_cps():
    """ Read CPS data
     Must convert .sav file to .csv first """
    
    cps = pd.read_csv('cdc.csv', sep=' ',
                      error_bad_lines = False, warn_bad_lines = False,
                      usecols = ['gtcbsa', 'income', 'hrnumhou' ])
    # Only need certain columns
    # hrnumhou is # of people in household
    # hrhhid is household ID, not using
    
    cps['gtcbsa'] = cps['gtcbsa'].apply(str.strip)
    
    return cps

def read_occ():
    """ Read the Occupation data from BLS, just one part for now"""
    # Need new pandas .12 to do this
    occ = pd.read_excel('oesm12ma/aMSA_M2012_dl.xls', 'AMSA_dl') # Magic!
    occ = occ[['OCC_CODE','OCC_TITLE','TOT_EMP','AREA_NAME','AREA','A_MEDIAN']]
    return occ

def read_census():
    """ Read the census data, with headers manually merged into one header row"""
    census = pd.read_csv('CBSA-EST2012-01.csv',
                         usecols = ['CBSA\nCode','Metro Division Code',
                                     'Geographic area','2012'])
    print census.columns
    census = census[census["Metro Division Code"].isnull()]
    return census

if __name__ == '__main__':
    cps = read_cps()
    occ = read_occ()
    census = read_census()
    
    # Messy CPS Area names - manually clean
    # Could potentially match on first name before the hyphen, and state
    cps['gtcbsa'] = cps['gtcbsa'].replace('Chicago-Naperville-Joliet, IL-IN-WI', 'Chicago-Joliet-Naperville, IL-IN-WI')
    cps['gtcbsa'] = cps['gtcbsa'].replace('Philadelphia-Camden-Wilmington, PA-NJ-DE', \
                                          'Philadelphia-Camden-Wilmington, PA-NJ-DE-MD')
    cps['gtcbsa'] = cps['gtcbsa'].replace('Miami-Fort Lauderdale-Miami Beach, FL', 'Miami-Fort Lauderdale-Pompano Beach, FL')
    
    # Narrow the data
    tot_pop = occ[occ['OCC_TITLE'] == "All Occupations"]
    
    filter_occ = "Community and Social Service Occupations"
    
    # Filters to Community Occupations
    occ = occ[occ['OCC_TITLE']==filter_occ]
    occ = occ.rename(columns={'TOT_EMP':'SS Employed', 'A_MEDIAN':'SS Med Salary'})
    
    print "BLS Columns:", occ.columns
    
    #cps = cps.dropna()
    print "CPS Columns:", cps.columns
    
    cps_income = pd.DataFrame(pd.pivot_table(cps, values ='income', rows = 'gtcbsa', aggfunc = 'median'))
    
    # Get percent in poverty per msa (cbsa)
    cps_count = pd.DataFrame(pd.pivot_table(cps, values ='income', rows = 'gtcbsa', aggfunc = len))
    cps_poverty = cps[  (cps['income'] < 11170) & (cps['hrnumhou'] == 1) |
                        (cps['income'] < 15130) & (cps['hrnumhou'] == 2) |
                        (cps['income'] < 19090) & (cps['hrnumhou'] == 3) |
                        (cps['income'] < 23050) & (cps['hrnumhou'] == 4) |
                        (cps['income'] < 27010) & (cps['hrnumhou'] == 5) |
                        (cps['income'] < 30970) & (cps['hrnumhou'] == 6) |
                        (cps['income'] < 34930) & (cps['hrnumhou'] == 7) |
                        (cps['income'] < 38890) & (cps['hrnumhou'] == 8) |
                        ((cps['hrnumhou'] > 8)
                            & ((cps['income']-38890).astype(float)/(cps['hrnumhou']-8).astype(float) < 3960))
                        ]
    cps_poverty = pd.DataFrame(pd.pivot_table(cps_poverty, values ='income', rows = 'gtcbsa', aggfunc = len))
    cps_poverty['poverty'] = cps_poverty.astype(float)/cps_count.astype(float)
    #cps_poverty.to_csv('cps_poverty.csv')
    
    cps_income = pd.merge(cps_income, cps_poverty, left_index = True, right_index = True)
    
    m = pd.merge(occ, census, how = 'left', left_on = 'AREA', right_on = 'CBSA\nCode')
    m = pd.merge(occ, cps_income, how='left', left_on = 'AREA_NAME', right_index = True )
    m = pd.merge(m, tot_pop, how = 'left', on='AREA_NAME')
    
    
    m.to_csv('merged_cps_keepna.csv',
             cols=['AREA_NAME','SS Employed', 'poverty', 'TOT_EMP']) #,'2012'])
    print m
