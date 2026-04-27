import numpy as np
import plotly.express as px
from astroquery.gaia import Gaia

# 1. Fetch data
query = """
SELECT TOP 100 
    source_id, ra, dec, parallax, teff_gspphot, phot_g_mean_mag
FROM gaiadr3.gaia_source
WHERE parallax > 100 
ORDER BY parallax DESC
"""
job = Gaia.launch_job(query)
df = job.get_results().to_pandas()

# 2. Conversions
df['dist_ly'] = 3261.56 / df['parallax']
ra_rad = np.radians(df['ra'])
dec_rad = np.radians(df['dec'])

df['x'] = df['dist_ly'] * np.cos(dec_rad) * np.cos(ra_rad)
df['y'] = df['dist_ly'] * np.cos(dec_rad) * np.sin(ra_rad)
df['z'] = df['dist_ly'] * np.sin(dec_rad)

# 3. FIX: Handle negative sizes and missing temperatures
# We use a base size of 25 and subtract magnitude. 
# clip(min=1) ensures no star has a size smaller than 1 or negative.
df['display_size'] = (25 - df['phot_g_mean_mag']).clip(lower=1)

# Fill missing temperatures with a neutral solar-like value (5778K)
df['teff_gspphot'] = df['teff_gspphot'].fillna(5778)

# 4. Plot
fig = px.scatter_3d(
    df, x='x', y='y', z='z',
    color='teff_gspphot',
    size='display_size', 
    size_max=15,         
    hover_name='source_id',
    hover_data={'x':False, 'y':False, 'z':False, 'dist_ly':':.2f', 'phot_g_mean_mag':':.2f'},
    color_continuous_scale='RdYlBu_r', 
    template='plotly_dark'            
)

fig.update_layout(
    title="3D Map of the Solar Neighborhood (Fixed)",
    scene=dict(xaxis_title='X (ly)', yaxis_title='Y (ly)', zaxis_title='Z (ly)')
)
fig.show()