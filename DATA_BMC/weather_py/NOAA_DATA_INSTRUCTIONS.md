# Instructions pour obtenir les données météo NOAA (1933-1939)

## Problème
Les données ERA5 (via Open-Meteo) ne remontent qu'à 1940. Pour les années 1933-1939 de Black Mountain College, il faut utiliser les données de stations météo NOAA.

## Sources de données

### 1. Climate Data Online (CDO) - Interface Web
**URL**: https://www.ncei.noaa.gov/cdo-web/search

1. Sélectionner "Daily Summaries"
2. Date Range: 1933-09-01 to 1939-12-31
3. Search For: Stations
4. Enter: "Asheville, NC" ou "Buncombe County, NC"
5. Add to Cart → Select Data Types (TMAX, TMIN, PRCP, SNOW, etc.)
6. Submit Order → télécharger le CSV

### 2. API CDO v2 (programmatique)
**Documentation**: https://www.ncdc.noaa.gov/cdo-web/webservices/v2

```bash
# Obtenir un token (gratuit)
# https://www.ncdc.noaa.gov/cdo-web/token

# Chercher les stations près de Black Mountain
curl -H "token: YOUR_TOKEN" \
  "https://www.ncei.noaa.gov/cdo-web/api/v2/stations?datasetid=GHCND&locationid=FIPS:37021&startdate=1933-01-01&enddate=1940-01-01"

# Télécharger les données
curl -H "token: YOUR_TOKEN" \
  "https://www.ncei.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&stationid=GHCND:USC00310300&startdate=1933-09-01&enddate=1939-12-31&datatypeid=TMAX,TMIN,PRCP&limit=1000"
```

### 3. GHCN-Daily Direct Download
**URL**: https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/

Fichiers CSV par station:
- `USC00310300.csv` - Asheville (données historiques longues)
- Format: ID, DATE, ELEMENT, VALUE, M-FLAG, Q-FLAG, S-FLAG, OBS-TIME

### 4. Python avec cdo-api-py
```python
pip install cdo-api-py pandas

from cdo_api_py import Client
import pandas as pd

token = "YOUR_TOKEN_HERE"
client = Client(token, default_units='metric')

# Trouver les stations
stations = client.find_stations(
    datasetid='GHCND',
    locationid='FIPS:37021',  # Buncombe County, NC
    startdate='1933-01-01',
    enddate='1940-01-01',
    return_dataframe=True
)

# Télécharger les données
for idx, station in stations.iterrows():
    data = client.get_data_by_station(
        datasetid='GHCND',
        stationid=station['id'],
        startdate='1933-09-01',
        enddate='1939-12-31',
        return_dataframe=True
    )
    data.to_csv(f"noaa_{station['id']}.csv")
```

## Stations proches de Black Mountain

| Station ID | Nom | Distance | Période |
|------------|-----|----------|---------|
| USC00310300 | ASHEVILLE NC US | ~24km | 1867-présent |
| USW00003812 | ASHEVILLE REGIONAL AIRPORT | ~32km | 1946-présent |
| USC00319028 | WAYNESVILLE NC US | ~45km | variable |

## Variables disponibles (GHCN-Daily)

| Code | Description |
|------|-------------|
| TMAX | Température max (tenths of °C) |
| TMIN | Température min (tenths of °C) |
| PRCP | Précipitation (tenths of mm) |
| SNOW | Chutes de neige (mm) |
| SNWD | Épaisseur de neige (mm) |
| AWND | Vitesse moyenne du vent |
| WSFG | Rafales de vent |

**Note**: Diviser TMAX, TMIN par 10 pour obtenir °C
         Diviser PRCP par 10 pour obtenir mm

## Qualité des données

Les données des stations peuvent avoir des lacunes. Vérifier les flags:
- M-FLAG: Measurement flag
- Q-FLAG: Quality flag (blank = passed all checks)
- S-FLAG: Source flag

