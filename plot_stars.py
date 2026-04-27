import numpy as np
import plotly.express as px
import pandas as pd
from astroquery.gaia import Gaia

# 1. Simplified Query - Using only the main stable table
query = """
SELECT TOP 100 
    source_id, ra, dec, parallax, teff_gspphot, phot_g_mean_mag, designation
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

# 3. Clean up the Name
# The 'designation' column looks like 'Gaia DR3 123456...', let's make it shorter
df['display_name'] = df['designation'].str.replace('Gaia DR3 ', 'ID: ')

# Famous Star Cross-match (The "Manual" way for the closest ones)
# Gaia IDs for the big ones often vary, but we can tag the Sun easily
df['display_size'] = (25 - df['phot_g_mean_mag']).clip(lower=2)
df['teff_gspphot'] = df['teff_gspphot'].fillna(5778)

# 4. ADD THE SUN
sun = pd.DataFrame([{
    'display_name': '☀️ THE SUN (Home)',
    'x': 0, 'y': 0, 'z': 0,
    'dist_ly': 0,
    'teff_gspphot': 5778,
    'display_size': 40, 
    'phot_g_mean_mag': -26.7
}])
df = pd.concat([df, sun], ignore_index=True)

# 5. Plot
fig = px.scatter_3d(
    df, x='x', y='y', z='z',
    color='teff_gspphot',
    size='display_size',
    size_max=18,
    hover_name='display_name',
    hover_data={
        'x': False, 'y': False, 'z': False, 
        'display_size': False,
        'dist_ly': ':.2f', 
        'phot_g_mean_mag': ':.2f',
        'teff_gspphot': ':.0f'
    },
    color_continuous_scale='RdYlBu_r', 
    template='plotly_dark'
)

fig.update_layout(
    title="Nearest Stars to the Sun (Gaia DR3)",
    scene=dict(
        xaxis=dict(backgroundcolor="black", gridcolor="gray", title="X (ly)"),
        yaxis=dict(backgroundcolor="black", gridcolor="gray", title="Y (ly)"),
        zaxis=dict(backgroundcolor="black", gridcolor="gray", title="Z (ly)")
    )
)

fig.show()