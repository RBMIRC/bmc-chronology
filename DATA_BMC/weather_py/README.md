# Black Mountain College Weather Archive
## Retcon Black Mountain Project

This archive contains historical weather data for Black Mountain College, NC (1933-1957).

## Contents

| File | Description |
|------|-------------|
| `bmc_weather_archive_template.json` | JSON template with full structure (years/months/days) |
| `bmc_weather_local.py` | Python script to fetch Open-Meteo data (1940-1957) |
| `bmc_weather_collector.py` | Alternative collector script |
| `NOAA_DATA_INSTRUCTIONS.md` | Instructions for obtaining 1933-1939 data from NOAA |

## Data Availability

| Period | Source | Status |
|--------|--------|--------|
| 1933-1939 | NOAA GHCN-Daily | Requires API token or manual download |
| 1940-1957 | Open-Meteo (ERA5) | Available (run `bmc_weather_local.py`) |

## Quick Start

### For 1940-1957 data (Open-Meteo):

```bash
# Install dependencies
pip install requests pandas

# Optional: for better caching
pip install openmeteo-requests requests-cache retry-requests

# Run the collector
python bmc_weather_local.py
```

### For 1933-1939 data (NOAA):

1. Get a free API token: https://www.ncdc.noaa.gov/cdo-web/token
2. Follow instructions in `NOAA_DATA_INSTRUCTIONS.md`

## Location

- **Name**: Black Mountain, North Carolina
- **Coordinates**: 35.6179°N, 82.3968°W
- **Elevation**: ~640m
- **Nearby station**: Asheville, NC (USC00310300)

## JSON Structure

```json
{
  "black_mountain_college_weather_archive": {
    "metadata": { ... },
    "statistics": { ... },
    "years": {
      "1933": {
        "status": "PENDING_NOAA_GHCN",
        "months": {
          "09": {
            "days": {
              "01": { "temperature_2m_max": 25.3, ... }
            }
          }
        }
      }
    }
  }
}
```

## Variables

| Variable | Unit | Description |
|----------|------|-------------|
| temperature_2m_max | °C | Maximum temperature |
| temperature_2m_min | °C | Minimum temperature |
| precipitation_sum | mm | Total precipitation |
| snowfall_sum | mm | Total snowfall |
| wind_speed_10m_max | km/h | Maximum wind speed |
| weather_code | WMO code | Weather condition |

---

*Part of the Retcon Black Mountain project*  
*Eden Summer Institute*
