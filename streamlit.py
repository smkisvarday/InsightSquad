import altair as alt
import pandas as pd
import streamlit as st

### Import data ###

#mount google drive ("allow access" when prompted)

# mount to google drive
#from google.colab import drive
#drive.mount('/content/gdrive')

#read in data

#IF DIRECTORY DOESN'T WORK FOR YOU try right clicking on the folder -> add shortcut to Drive
 # and put the shortcut in your top-level My Drive folder
directory = '/content/gdrive/My Drive/GroupProject_bmi706/Disease-VaccineWHODatasets/'


#  (these are saved as csv, with the readme/reference worksheets tabs removed)
#vaccine coverage data:
# vax = pd.read_csv(directory+'wuenic_input_to_pdf__july_2022.csv')
vax = pd.read_csv(directory +"coverage--2021.csv")


#disease incidence data:
dis = pd.read_csv(directory+'incidence-rate--2021.csv')

###  Creating the Needed Dataframe ###

vax.head()
vax.shape
vax[vax.GROUP == "COUNTRIES"].NAME.unique().size

vax[vax.GROUP == "WB_LONG"].NAME.unique()

print(vax.ANTIGEN.unique().shape)
print(vax.ANTIGEN_DESCRIPTION.unique().shape)
vax.ANTIGEN.unique()

vax.YEAR.agg(['min', 'max'])

pd.DataFrame(vax.groupby(['YEAR'])['COVERAGE'].apply(lambda x: x.notnull().mean())).max()

vax_countries = vax[vax.GROUP == "COUNTRIES"].NAME.unique()
dis_countries = dis[dis.GROUP == "COUNTRIES"].NAME.unique()
countries_not_in_vax = np.setdiff1d(dis_countries, vax_countries)
countries_not_in_vax

countries_not_in_dis = np.setdiff1d(vax_countries, dis_countries)
countries_not_in_dis

#define vaccine codes
# Most definitions found at: https://www.who.int/data/gho/data/indicators/indicators-index

vax_dict = {'bcg':'tuberculosis',  # BCG immunization coverage among 1-year-olds (%)
            'dtp1':'diptheria_tetanus_pertussis_dose1',  
            'dtp3':'diptheria_tetanus_pertussis_dose3', # #Diphtheria tetanus toxoid and pertussis (DTP3) immunization coverage among 1-year-olds (%)
            'hepb3':'hepatitisB_dose3', # Hepatitis B (HepB3) immunization coverage among 1-year-olds (%) 
            'hepbb':'hepatitisB_birth-dose',
            'hib3':'Haemophilus_influenzaeB',  #percentage of 1 year olds receiving HIB vaccine in a given year
            'ipv1':'polio_inactivated',  #https://www.who.int/teams/health-product-policy-and-standards/standards-and-specifications/vaccines-quality/poliomyelitis
            'mcv1':'measles_dose1', # Measles-containing-vaccine first-dose (MCV1) immunization coverage among 1-year-olds (%) 
            'mcv2':'measles_dose2', # Measles-containing-vaccine second-dose (MCV2) immunization coverage by the nationally recommended age (%)
            'pcv3':'pneumococcal', # Pneumococcal Conjugate vaccines (PCV3) immunization coverage among 1-year-olds (%)
            'pol3':'polio_live-oral',  # Polio (Pol3) immunization coverage among 1-year-olds (%), https://apps.who.int/iris/bitstream/handle/10665/332774/WER9526-283-290-eng-fre.pdf
            'rotac':'rotavirus',  # Rotavirus vaccines completed dose (RotaC) immunization coverage among 1-year-olds (%)
            'rcv1':'rubella_dose1',  #https://www.cdc.gov/mmwr/volumes/70/wr/mm7023a1.htm
            'yfv':'yellow_fever'}


vax.ANTIGEN.unique()

dis.head()

dis.DISEASE_DESCRIPTION.unique()

#how many unique countries in dis?
print('There are ', dis_countries.size, ' unique countries in the disease dataset.')

#how many uniue regions in dis?
dis_regions = dis[dis.GROUP == "WHO_REGIONS"].NAME.unique()
vax_regions = vax[vax.GROUP == "WHO_REGIONS"].NAME.unique()
print('There are ', dis_regions.size, ' WHO regions in the disease dataset:')
print(dis_regions)

print('The same 6 regions are in the vax dataset:')
print(vax_regions)

dis.shape

dis.isna().sum()

dis.dropna(thresh=7, inplace=True, axis=0)

dis.groupby('NAME')['YEAR'].apply(lambda x: x.count())

dis.isna().sum()

cong_dz = ['CRS', 'NTETANUS']

#drop na
incidence = dis[~dis.DISEASE.isin(cong_dz)]
incidence.dropna(inplace=True)
incidence

vax.head(2)
dis.head()
dis.DISEASE.unique()

#drop the mostly-nan row from both datasets
dis.dropna(thresh=7, inplace=True, axis=0)
vax.dropna(thresh=9, inplace=True, axis=0)

#add an a DISEASE column to the vax dataset, to match the ANTIGEN_DESCRIPTION column in dis dataset

#create empty column
vax['DISEASE'] = np.NaN

diphtheria_words = '|'.join(['Diphtheria']) 
measles_words = '|'.join(['Measles'])
tetanus_words = '|'.join(['Tetanus'])
mumps_words = []
pertussis_words = '|'.join(['Pertussis'])
polio_words = '|'.join(['Polio', 'polio', 'IPV'])
rubella_words = '|'.join(['Rubella'])
yellowfever_words = '|'.join(['Yellow fever'])
jenceph_words = '|'.join(['Japanese encephalitis'])

#populate with diseases matching antigen description, for diseases in the dis dataset 
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(diphtheria_words), 'DISEASE'] = 'DIPHTHERIA'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(measles_words), 'DISEASE'] = 'MEASLES'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(tetanus_words), 'DISEASE'] = 'TTETANUS'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(pertussis_words), 'DISEASE'] = 'PERTUSSIS'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(polio_words), 'DISEASE'] = 'POLIO'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(rubella_words), 'DISEASE'] = 'RUBELLA'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(yellowfever_words), 'DISEASE'] = 'YFEVER'
vax.loc[vax.ANTIGEN_DESCRIPTION.str.contains(jenceph_words), 'DISEASE'] = 'JAPENC'


vax.head()

dis.DISEASE_DESCRIPTION.unique()
common_diseases = vax.loc[vax.DISEASE.notna(), 'DISEASE'].unique()
common_diseases

###Merge diseae and vaccine data on matching conditions ###

#limit both datasets to just illnesses common to both, then merge on DISEASE

vax_lim = vax[vax.DISEASE.isin(common_diseases)]
dis_lim = dis[dis.DISEASE.isin(common_diseases)]

df = pd.merge(vax_lim, dis_lim, on=['GROUP', 'CODE', 'NAME', 'YEAR', 'DISEASE'], how='left')
df.head(3)

### Test case to eval accuracy of merge ###

dis[(dis.NAME=='Aruba') & (dis.YEAR==2019) & (dis.DISEASE=='MEASLES')]
vax[(vax.NAME=='Aruba') & (vax.YEAR==2019) & (vax.DISEASE=='MEASLES')]
df[(df.NAME=='Aruba') & (df.YEAR==2019) & (df.DISEASE=='MEASLES')]

# What groups does df contain?
df.GROUP.unique()

# What Development statuses does df contain?
df[df.GROUP=='DEVELOPMENT_STATUS']

### Let's look at it ###
df.head()
df.YEAR.unique()
df.DISEASE.unique()
df.ANTIGEN.unique()

###Now creating a dataframe specifically for the geospatial chart ###

# defining completed vaccine series
# for me the definition will be has had the WHO recommended number of vaccines in childhood

#WHO says at least:
#       DIPHTHERIA = 5 == DIPHCV5
#       POLIO = 3 == POL3
#       MEASLES = 2 == MCV2
#       PERTUSSIS = 3 == DTPCV3
#       RUBELLA = 1 == RCV1
#       TETANUS = TTETANUS = 3 (best we can do here is 2 plus) == TT2PLUS
#       YELLOW FEVER = YFEVER = (1 where endemic) == YFV
#       JAPANESE ENCEPHALITIS = JAPENC = JAPENC
#Note: There are 3 codes related to Japanese Encephalitis JAPENC is just "Japanese Encephalitis"; JAPENC_C is "Japanese Encephalitis, last dose". However, when you look at the data for these two, JAPENC_C is rarely used and when it is used, there is also a listing for JAPENC, so JAPENC is clearly the code we want for this one.


#Selecting just the rows for the final dose vaccines:

#df1 = df1[df1['Country'].isin(countries)]

WHO_completed_series = ['DIPHCV5', 'POL3', 'MCV2', 'DTPCV3',  'RCV1', 'TT2PLUS', 'YFV', 'JAPENC']
df_last_dose = df[df['ANTIGEN'].isin(WHO_completed_series)]
                                      
print(df_last_dose.ANTIGEN.unique())
print(df_last_dose.shape)

print(df_last_dose.YEAR.unique())

print(df_last_dose.columns.tolist())

df_last_dose = df_last_dose[df_last_dose['COVERAGE_CATEGORY_DESCRIPTION'] == 'Official coverage']
df_last_dose.head()

print(df_last_dose.shape)

#Getting just the columns I want for the geospatial maps

df_ld = df_last_dose[['NAME', 'YEAR', 'DISEASE', 'COVERAGE', 'INCIDENCE_RATE']]

print(df_ld.columns)
print(df_ld.shape)

#Getting just the columns I want for the geospatial maps

df_ld = df_last_dose[['NAME', 'YEAR', 'DISEASE', 'COVERAGE', 'INCIDENCE_RATE']]

print(df_ld.columns)
print(df_ld.shape)

df_ld.YEAR.unique()

#Change the name of the 'NAME' column to 'Country', so that it will line up with the name of the 'Country' column in the Country code dataframe to use in the geospatial map.

df_ld = df_ld.rename(columns={'NAME': 'Country'})

df_ld.head()

# Getting country codes for making geospatial charts
country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'conuntry-code': str})

country_df.head()

#Just the Country and country code columns:

country_df_nw = country_df.copy()
country_df_2 = country_df_nw[['Country', 'country-code']]
country_df_2

print(country_df_2[country_df_2['Country'] == 'Aruba'])

# merge the dataframes

for_geo = df_ld.merge(country_df_2, how='inner'
)
for_geo.head()

for_geo.YEAR.unique()
for_geo['Country']
print(for_geo[for_geo['Country'] == 'Aruba'])

### Delete this later!!!  I'm just trying to narrow down to one vaccine to see if I can make the linked geocharts without the disease radio button.

for_geo = for_geo[for_geo['DISEASE'] == 'DIPHTHERIA']
for_geo.DISEASE.unique()

### Don't forget to delete above!!!  ###

#Just checking to make sure I still have all the years.  Can also delete this later.  
for_geo.YEAR.unique()

###  OKAY HERE GOES THE CHART ###

country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'conuntry-code': str})

from vega_datasets import data
source = alt.topo_feature(data.world_110m.url, 'countries')

#I will need to update the year for this visualization once I figure out how to do a slider for this chart
year = 2018.0 # only visualize for 2018
for_geo = for_geo[for_geo['YEAR']==year]

st.header("Global Vaccine-Preventable Disease Dashboard")

width = 600
height  = 300
project = 'equirectangular'

# a gray map using as the visualization background
background = alt.Chart(source
).mark_geoshape(
    fill='#aaa',
    stroke='white'
).properties(
    width=width,
    height=height
).project(project)

######################
# P3.4 create a selector to link two map visualizations
selector = alt.selection_single(on='click'
    # add your code here
    # ...
    )


chart_base = alt.Chart(source
    ).properties( 
        width=width,
        height=height
    ).project(project
    ).add_selection(selector
    ).transform_lookup(
        lookup="id",
# Rate = COVERAGE,  Population = Incidence Rate, 
        from_=alt.LookupData(for_geo, "country-code", ['COVERAGE', 'COUNTRY', 'INCIDENCE_RATE', 'YEAR']),
    )

# fix the color schema so that it will not change upon user selection
coverage_scale = alt.Scale(domain=[for_geo['COVERAGE'].min(), for_geo['COVERAGE'].max()], scheme='oranges')
coverage_color = alt.Color(field="COVERAGE:Q", type="quantitative", scale=coverage_scale)

chart_coverage = chart_base.mark_geoshape().encode(
    color=alt.Color('COVERAGE:Q', type="quantitative", scale=coverage_scale), 
    tooltip=['COVERAGE:Q', 'Country:N']  
    ######################
    # P3.1 map visualization showing the mortality rate
    # add your code here
    # ...
    ######################
    # P3.3 tooltip
    # add your code here
    # ...
    ).transform_filter(
    selector
    ).properties(
###Need to fix the year in title?
    title=f'Vaccine Coverage Worldwide {year}'
)


# fix the color schema so that it will not change upon user selection
incidence_scale = alt.Scale(domain=[for_geo['INCIDENCE_RATE'].min(), for_geo['INCIDENCE_RATE'].max()], scheme='yellowgreenblue')
chart_incidence = chart_base.mark_geoshape().encode(
    color=alt.Color('INCIDENCE_RATE:Q', type="quantitative", scale=incidence_scale),
    tooltip=['INCIDENCE_RATE:Q', 'COUNTRY:N'] 
    ######################
    # P3.2 map visualization showing the mortality rate
    # add your code here
    # ...
     ######################
    # P3.3 tooltip
    # add your code here  
    # ...
    ).transform_filter(
    selector
).properties(
###Again the year?
    title=f'World Disease Incidence Rate {year}'
)

chart2 = alt.vconcat(background + chart_coverage, background + chart_incidence
).resolve_scale(
    color='independent'
)



chart2


