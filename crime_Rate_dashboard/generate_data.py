import pandas as pd
import numpy as np
import random
import os

base_dir = r"C:\Users\Expart\Desktop\Crime_rate_dashboard\crime_ai_dashboard"
os.makedirs(base_dir, exist_ok=True)
csv_path = os.path.join(base_dir, 'crime_dataset_india.csv')

np.random.seed(42)
random.seed(42)

years = list(range(2010, 2024))
cities = {
    'Mumbai': (19.0760, 72.8777),
    'Delhi': (28.7041, 77.1025),
    'Bangalore': (12.9716, 77.5946),
    'Chennai': (13.0827, 80.2707),
    'Kolkata': (22.5726, 88.3639)
}
crime_types = ['Theft', 'Robbery', 'Assault', 'Cybercrime', 'Murder']

data = []
for year in years:
    for city, (lat, lon) in cities.items():
        for crime in crime_types:
            base = random.randint(50, 500)
            if city == 'Delhi' and crime in ['Theft', 'Robbery']:
                base += 200
            elif city == 'Mumbai' and crime == 'Cybercrime':
                base += 150
            elif crime == 'Murder':
                base = random.randint(10, 50)
                
            if crime == 'Cybercrime':
                base += int((year - 2010) * 20)
                
            lat_noise = lat + random.uniform(-0.05, 0.05)
            lon_noise = lon + random.uniform(-0.05, 0.05)
            
            data.append([year, city, crime, base, lat_noise, lon_noise])

df = pd.DataFrame(data, columns=['Year', 'City', 'Crime_Type', 'Crime_Count', 'Latitude', 'Longitude'])
df.to_csv(csv_path, index=False)
print("Data generated successfully.")
