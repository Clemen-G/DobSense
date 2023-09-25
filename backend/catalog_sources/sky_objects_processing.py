
# %%

#  comment

import requests
import gzip
import pandas as pd
import itertools
import json
from astropy.coordinates import SkyCoord
from astropy import units as u
import numpy as np
import csv

# %%

url = "https://raw.githubusercontent.com/Stellarium/stellarium-skycultures/master/western/index.json"

r = requests.get(url).json()


# %%

# creates a list of [constellation, set of stars]

def to_record(const_obj):
    return {
        "iau": const_obj["iau"],
        "stars": set(itertools.chain(*const_obj['lines'])),
        "id": const_obj['id'],
        'common_name': const_obj['common_name']['native']}

const_stars = list(map(to_record, r["constellations"]))

# %%

# save hip-boyer map to disk, just in case

catalog_url = 'http://cdsarc.u-strasbg.fr/viz-bin/nph-Cat/txt?IV%2F27A/catalog.dat'

catalog_dat = requests.get(catalog_url)

with open('./catalog.dat', 'w') as f:
    f.write(catalog_dat.text)
# %%

# downloads data set
'''
From http://cdsarc.u-strasbg.fr/ftp/IV/27A/ReadMe
--------------------------------------------------------------------------------
   Bytes Format Units   Label   Explanations
--------------------------------------------------------------------------------
   1-  6  I6    ---     HD      [1/257937] Henry Draper Catalog Number <III/135>
   8- 19  A12   ---     DM      Durchmusterung Identification from HD Catalog
                                  <III/135> (1)
  21- 25  I5    ---     GC      [1/33342]? Boss General Catalog (GC, <I/113>)
                                   number if one exists, otherwise blank
  27- 30  I4    ---     HR      [1/9110]? Harvard Revised Number=Bright Star
                                   Number <V/50> if one exists, otherwise blank
  32- 37  I6    ---     HIP     [1/120416]? Hipparcos Catalog <I/196> number
                                   if one exists, otherwise blank
  39- 40  I2    h       RAh     Right Ascension J2000 (hours) (2)
  41- 42  I2    min     RAm     Right Ascension J2000 (minutes) (2)
  43- 47  F5.2  s       RAs     Right Ascension J2000 (seconds) (2)
      49  A1    ---     DE-     Declination J2000 (sign)
  50- 51  I2    deg     DEd     Declination J2000 (degrees) (2)
  52- 53  I2    arcmin  DEm     Declination J2000 (minutes) (2)
  54- 57  F4.1  arcsec  DEs     Declination J2000 (seconds) (2)
  59- 63  F5.2  mag     Vmag    [-1.44/13.4]? Visual magnitude (2)
  65- 67  I3    ---     Fl      ? Flamsteed number (G1)
  69- 73  A5    ---     Bayer   Bayer designation (G1)
  75- 77  A3    ---     Cst     Constellation abbreviation (G1)
'''

df = pd.read_csv(
    catalog_url,
    skiprows=[0, 1, 2, 4],
    header=0,
    delimiter='|',
    dtype=str,
    skipinitialspace=True)

# removes last non-data line
df = df.head(-1)
# %%

# renames a couple of columns
df.rename(columns={'Ah Am   RAs  Ed Em  DEs': "RA/DEC", "Cst": "Const"},
          inplace=True)
# removes unneeded columns
df.drop(labels=['HD', 'GC', 'HR', 'Fl'], axis=1, inplace=True)
# removes 'DF     ' column
df.drop(labels=df.columns[0], axis=1, inplace=True)
# strips whitespaces from Bayer name
df['Bayer'] = df['Bayer'].str.strip()

# only keeps elements with HIP id
df = df[~df['HIP'].isna()]
# casts HIP elements to int
df['HIP'] = df['HIP'].astype(int)
# Makes HIP index
df = df.set_index(df['HIP'])
df = df.drop('HIP', axis=1)

# %%

# stats

df.isna().sum(axis=0)
# Note: some HIP are na


# %%

# data checks

# set of distinct star that belong to some constellation. HIP id.
stars_in_const = {s for const in const_stars for s in const["stars"]}

# 11 constellation stars are not in the catalog
const_stars_not_in_catalog = stars_in_const - set(df.index)


# restrict to stars in some constellation
const_stars_in_catalog = df[df.index.isin(stars_in_const)]

# only keep stars with a Bayer name
const_stars_in_catalog = const_stars_in_catalog[~const_stars_in_catalog["Bayer"].isna()]
'''
hip_const = pd.DataFrame(
    [[c['iau'], s] for c in const_stars for s in c['stars']],
    columns=['Const', 'HIP'])
hip_const = hip_const.set_index(hip_const['HIP'])
hip_const = hip_const.drop('HIP', axis=1)

master_db = const_stars_in_catalog.join(hip_const)
'''
master_db = const_stars_in_catalog

# converts RA/DEC string to decimal degrees

stars_skycoords = SkyCoord(master_db["RA/DEC"].to_numpy(),
                           unit=(u.hourangle, u.deg))

stars_ra_degs = stars_skycoords.ra.value
stars_dec_degs = stars_skycoords.dec.value

stars_ra_dec_degs = pd.DataFrame(
                                dict(ra=stars_ra_degs,
                                    dec=stars_dec_degs),
                                index=master_db.index)

master_db = master_db.join(stars_ra_dec_degs)

# drops RA/DEC column
# df = df.drop('RA/DEC', axis=1)

# prepares a groupby dataset grouped by constellation
grps = master_db.reset_index().sort_values(['Const', 'Vmag']).groupby('Const')

const_stars_final = []

for [const, grp] in grps:
    # grp = grp.set_index('HIP')
    entry = grp.to_dict('records')
    # entry = [s for s in grp]
    const_stars_final.append({
        "const": const,
        "stars": entry}
    )

# %%

# save to file

with open('../data/constellations_stars.json', "w") as f:
    json.dump(const_stars_final, f, indent=4)
# %%

# =============================================================
# Saguaro astro catalog preparation procedure
# =============================================================

database_path = "./raw/SAC_DeepSky_Ver81_QCQ.TXT"
df = pd.read_csv(
    database_path,
    quotechar='"',
    quoting=csv.QUOTE_ALL,
    header=0,
    delimiter=',',
    dtype=str,
    skipinitialspace=True)

# removes spaces around column names
df.columns = [c.strip() for c in df.columns]

df = df[['OBJECT', 'OTHER', 'TYPE', 'CON', 'RA', 'DEC', 'MAG', 'SUBR',
       'CLASS', 'NGC DESCR']]

# removes all leading/trailing spaces and dedups spaces
df = df.replace(r"^ +| +$", r"", regex=True)
df = df.replace(r" +", r" ", regex=True)

# removes NONEX objects
df = df[df["TYPE"] != "NONEX"]

# there is a duplicate object, NGC 2905, with slightly
# different coordinates
df["OBJECT"].value_counts().iloc[0:2]

df[df["OBJECT"] == "NGC 2905"]

duplicate_item_idx = df.index[df["OBJECT"] == "NGC 2905"][1]
df = df.drop(duplicate_item_idx)

# replaces RA/DEC values with decimal degrees
objects_coords = SkyCoord(df[["RA", "DEC"]].to_numpy(),
                           unit=(u.hourangle, u.deg))

objects_ra_degs = objects_coords.ra.value
objects_dec_degs = objects_coords.dec.value

objects_ra_dec_degs = pd.DataFrame(
                                dict(ra=objects_ra_degs,
                                    dec=objects_dec_degs),
                                index=df.index)
df = df.join(objects_ra_dec_degs)

df.drop(labels=["RA", "DEC"], axis=1, inplace=True)

column_rename_map = dict(
    OBJECT='object_id',
    OTHER='other_names',
    TYPE='type',
    CON='con',
    MAG='vmag',
    SUBR='sr_br',
    CLASS='class'
)
column_rename_map['NGC DESCR'] = 'ngc_desc'
df.rename(column_rename_map, axis=1, inplace=True)

# adds alternative spellings of Messier objects (M 45 -> "Messier 45", "M45")

messier_ids = df["other_names"].str.extract(r"( |^)M (\d+)")[1]

messier_long = ("Messier " + messier_ids)
messier_long.name = "m_long"
messier_short = ("M" + messier_ids)
messier_short.name = "m_short"
# alt_messiers = messier_long.str.cat(messier_short, sep=" ")
# df2 = df.copy()
# df2["other_names"] = df2["other_names"].str.cat(alt_messiers, sep=" ")
df2 = pd.concat([df, messier_long, messier_short], axis=1)

# save to file

with gzip.open('../data/saguaro_objects.json.gz', "wb") as f:
    df2.to_json(f, orient='records')
# %%
