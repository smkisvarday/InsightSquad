import altair as alt
import pandas as pd
import streamlit as st
import numpy as np
from vega_datasets import data




@st.cache_data
def load_data():

    url_vax = "https://raw.githubusercontent.com/smkisvarday/InsightSquad/master/coverage--2021.csv"
    url_dis = "https://raw.githubusercontent.com/smkisvarday/InsightSquad/master/incidence-rate--2021.csv"


    vax = pd.read_csv(url_vax)
    dis = pd.read_csv(url_dis)

    return vax, dis



vax, dis = load_data()

print(vax.head())

###  Creating the Needed Dataframe ###

vax_countries = vax[vax.GROUP == "COUNTRIES"].NAME.unique()
dis_countries = dis[dis.GROUP == "COUNTRIES"].NAME.unique()

countries_not_in_vax = np.setdiff1d(dis_countries, vax_countries)
countries_not_in_dis = np.setdiff1d(vax_countries, dis_countries)

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

cong_dz = ['CRS', 'NTETANUS']
#drop na
incidence = dis[~dis.DISEASE.isin(cong_dz)]
incidence.dropna(inplace=True)

dis.dropna(thresh=7, inplace=True, axis=0)
#drop the mostly-nan row from both datasets
dis.dropna(thresh=7, inplace=True, axis=0)
vax.dropna(thresh=9, inplace=True, axis=0)



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

common_diseases = vax.loc[vax.DISEASE.notna(), 'DISEASE'].unique()

vax_lim = vax[vax.DISEASE.isin(common_diseases)]
dis_lim = dis[dis.DISEASE.isin(common_diseases)]

df = pd.merge(vax_lim, dis_lim, on=['GROUP', 'CODE', 'NAME', 'YEAR', 'DISEASE'], how='left')

WHO_completed_series = ['DIPHCV5', 'POL3', 'MCV2', 'DTPCV3',  'RCV1', 'TT2PLUS', 'YFV', 'JAPENC']
df_last_dose = df[df['ANTIGEN'].isin(WHO_completed_series)]


df_last_dose = df_last_dose[df_last_dose['COVERAGE_CATEGORY_DESCRIPTION'] == 'Official coverage']

#Getting just the columns I want for the geospatial maps

df_ld = df_last_dose[['NAME', 'YEAR', 'DISEASE', 'COVERAGE', 'INCIDENCE_RATE']]

df_ld = df_ld.rename(columns={'NAME': 'Country'})

country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'conuntry-code': str})

country_df_nw = country_df.copy()
country_df_2 = country_df_nw[['Country', 'country-code']]

# geospatial chart

# merge the dataframes
for_geo = df_ld.merge(country_df_2, how='inner'
)

country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'conuntry-code': str})
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