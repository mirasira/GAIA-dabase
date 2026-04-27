from astroquery.gaia import Gaia
import pandas as pd
import plotly.express as px

# 1. Write the ADQL Query
# We select the top 50 stars with the highest parallax (meaning they are closest)
query = """
SELECT TOP 50 
    source_id, ra, dec, parallax, teff_gspphot, phot_g_mean_mag
FROM gaiadr3.gaia_source
WHERE parallax > 0
ORDER BY parallax DESC
"""

# 2. Launch the Job
job = Gaia.launch_job(query)
results = job.get_results().to_pandas()

# 3. Data Cleaning & Conversion
# Distance (ly) approx = 3.26 / (parallax / 1000)
results['distance_ly'] = 3261.56 / results['parallax']

# 4. Create Interactive 3D Map
fig = px.scatter_3d(
    results, 
    x='ra', y='dec', z='distance_ly',
    color='teff_gspphot', 
    size='phot_g_mean_mag',
    hover_name='source_id',
    labels={'teff_gspphot': 'Temp (K)', 'distance_ly': 'Distance (ly)'},
    title="Interactive Map of the 50 Nearest Stars (Gaia DR3)"
)

# Reverse size so smaller magnitude (brighter stars) appear larger
fig.update_traces(marker=dict(sizeref=2, sizemode='area'))
fig.show()