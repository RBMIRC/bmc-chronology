#!/usr/bin/env python3
"""
Black Mountain College Complete Weather Archive
================================================
Collects ALL available weather data from 1933-1957:
- 1940-1957: Open-Meteo ERA5 (hourly + daily)
- 1933-1939: NOAA GHCN-Daily (daily only, from Asheville station)

Output: Comprehensive JSON with day-by-day, hour-by-hour data
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time
import requests
import io

# Try to import optional dependencies
try:
    import openmeteo_requests
    import requests_cache
    from retry_requests import retry
    OPENMETEO_SDK = True
except ImportError:
    OPENMETEO_SDK = False

# ============================================================================
# CONFIGURATION
# ============================================================================

BMC_LATITUDE = 35.6179
BMC_LONGITUDE = -82.3968
LOCATION_NAME = "Black Mountain, North Carolina"

# NOAA stations near Black Mountain College
# Using multiple stations for best coverage
NOAA_STATIONS = [
    ("USC00315796", "MONTREAT NC", 35.6500, -82.3167),  # Closest, 1917-1944
    ("USC00318442", "SWANNANOA 2 E NC", 35.6000, -82.3667),  # Very close, 1931-1944
    ("USC00313976", "HENDERSONVILLE 1 NE NC", 35.3297, -82.4492),  # Backup, 1898-present
]

OUTPUT_DIR = Path("./bmc_weather_archive")
OUTPUT_DIR.mkdir(exist_ok=True)

# Rate limiting - be nice to APIs
OPENMETEO_DELAY = 3  # seconds between requests
RETRY_DELAY = 65  # seconds to wait after rate limit

# WMO Weather codes
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

# ============================================================================
# NOAA GHCN-DAILY DATA (1933-1939)
# ============================================================================

def parse_ghcn_dly(content: str, station_id: str) -> pd.DataFrame:
    """
    Parse GHCN-Daily .dly fixed-width format.
    Format: ID(11) YEAR(4) MONTH(2) ELEMENT(4) [VALUE(5) MFLAG(1) QFLAG(1) SFLAG(1)] x 31
    """
    records = []

    for line in content.strip().split('\n'):
        if len(line) < 269:
            continue

        sid = line[0:11]
        if sid != station_id:
            continue

        year = int(line[11:15])
        month = int(line[15:17])
        element = line[17:21]

        # Parse 31 days
        for day in range(31):
            offset = 21 + (day * 8)
            value_str = line[offset:offset+5]
            mflag = line[offset+5:offset+6]
            qflag = line[offset+6:offset+7]
            sflag = line[offset+7:offset+8]

            try:
                value = int(value_str)
            except:
                value = -9999

            if value != -9999:
                try:
                    date = datetime(year, month, day + 1)
                    records.append({
                        'date': date,
                        'element': element,
                        'value': value,
                        'qflag': qflag
                    })
                except ValueError:
                    # Invalid date (e.g., Feb 30)
                    pass

    return pd.DataFrame(records)


def fetch_noaa_ghcn_daily():
    """
    Fetch NOAA GHCN-Daily data from multiple nearby stations.
    Combines data to maximize coverage for 1933-1939.
    """
    print("\n" + "="*60)
    print("FETCHING NOAA GHCN-DAILY DATA (1933-1939)")
    print("="*60)

    all_data = []

    for station_id, station_name, lat, lon in NOAA_STATIONS:
        print(f"\n  Station: {station_id} ({station_name})")

        # Try .dly format from NOAA
        url = f"https://www.ncei.noaa.gov/pub/data/ghcn/daily/all/{station_id}.dly"
        print(f"    URL: {url}")

        try:
            response = requests.get(url, timeout=120)
            response.raise_for_status()

            print(f"    Downloaded: {len(response.content)/1024:.1f} KB")

            # Parse the .dly format
            df = parse_ghcn_dly(response.text, station_id)

            if len(df) == 0:
                print("    No records found")
                continue

            # Filter to 1933-1939
            df = df[(df['date'] >= '1933-09-01') & (df['date'] <= '1939-12-31')]

            # Filter quality (keep only good data)
            df = df[df['qflag'].isin([' ', ''])]

            if len(df) == 0:
                print("    No data for 1933-1939")
                continue

            print(f"    Records for 1933-1939: {len(df)}")

            # Pivot to get one row per day
            daily = df.pivot_table(
                index='date',
                columns='element',
                values='value',
                aggfunc='first'
            )

            # Convert units (NOAA uses tenths for temp/precip)
            if 'TMAX' in daily.columns:
                daily['temperature_max_c'] = daily['TMAX'] / 10.0
            if 'TMIN' in daily.columns:
                daily['temperature_min_c'] = daily['TMIN'] / 10.0
            if 'PRCP' in daily.columns:
                daily['precipitation_mm'] = daily['PRCP'] / 10.0
            if 'SNOW' in daily.columns:
                daily['snowfall_mm'] = daily['SNOW'].astype(float)
            if 'SNWD' in daily.columns:
                daily['snow_depth_mm'] = daily['SNWD'].astype(float)

            daily['station'] = station_id
            all_data.append(daily)

            print(f"    Days with data: {len(daily)}")
            print(f"    Date range: {daily.index.min().date()} to {daily.index.max().date()}")

        except requests.exceptions.HTTPError as e:
            print(f"    HTTP Error: {e}")
        except Exception as e:
            print(f"    Error: {e}")

    if not all_data:
        print("\n  No NOAA data could be fetched!")
        return None

    # Combine data from all stations, prioritizing first station (closest)
    print("\n  Combining data from all stations...")
    combined = pd.concat(all_data)

    # Group by date and take first non-null value for each column
    # This prioritizes data from earlier stations in the list (closer)
    result = combined.groupby(combined.index).first()

    # Keep only the columns we care about
    keep_cols = ['temperature_max_c', 'temperature_min_c', 'precipitation_mm', 'snowfall_mm', 'snow_depth_mm']
    result = result[[c for c in keep_cols if c in result.columns]]

    print(f"  Combined days: {len(result)}")
    print(f"  Date range: {result.index.min().date()} to {result.index.max().date()}")

    return result


# ============================================================================
# OPEN-METEO DATA (1940-1957)
# ============================================================================

def fetch_openmeteo_year(year: int, include_hourly: bool = True, retry_count: int = 0):
    """Fetch one year of Open-Meteo data with retry logic."""

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    # Use direct requests (more control over errors)
    base_url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": BMC_LATITUDE,
        "longitude": BMC_LONGITUDE,
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "America/New_York",
        "daily": ",".join([
            "weather_code", "temperature_2m_max", "temperature_2m_min",
            "temperature_2m_mean", "apparent_temperature_max", "apparent_temperature_min",
            "sunrise", "sunset", "daylight_duration", "sunshine_duration",
            "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours",
            "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
            "shortwave_radiation_sum", "et0_fao_evapotranspiration"
        ])
    }

    if include_hourly:
        params["hourly"] = ",".join([
            "temperature_2m", "relative_humidity_2m", "dew_point_2m",
            "apparent_temperature", "precipitation", "rain", "snowfall",
            "snow_depth", "weather_code", "pressure_msl", "surface_pressure",
            "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high",
            "visibility", "evapotranspiration", "vapour_pressure_deficit",
            "wind_speed_10m", "wind_speed_100m", "wind_direction_10m", "wind_direction_100m",
            "wind_gusts_10m", "soil_temperature_0cm", "soil_temperature_6cm",
            "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm"
        ])

    try:
        response = requests.get(base_url, params=params, timeout=120)

        if response.status_code == 429 or "rate limit" in response.text.lower():
            if retry_count < 3:
                print(f"RATE LIMITED - waiting {RETRY_DELAY}s...", end=" ", flush=True)
                time.sleep(RETRY_DELAY)
                return fetch_openmeteo_year(year, include_hourly, retry_count + 1)
            else:
                return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        if "429" in str(e) and retry_count < 3:
            print(f"RATE LIMITED - waiting {RETRY_DELAY}s...", end=" ", flush=True)
            time.sleep(RETRY_DELAY)
            return fetch_openmeteo_year(year, include_hourly, retry_count + 1)
        print(f"HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def collect_openmeteo_all_years():
    """Collect all Open-Meteo data for 1940-1957 with proper rate limiting."""

    print("\n" + "="*60)
    print("FETCHING OPEN-METEO ERA5 DATA (1940-1957)")
    print("="*60)
    print(f"Including hourly data - delay {OPENMETEO_DELAY}s between requests")
    print("This will take several minutes...")

    all_daily = []
    all_hourly = []

    for year in range(1940, 1958):
        print(f"  {year}...", end=" ", flush=True)

        data = fetch_openmeteo_year(year, include_hourly=True)

        if data:
            # Process JSON response
            if "daily" in data:
                df_daily = pd.DataFrame(data["daily"])
                df_daily["time"] = pd.to_datetime(df_daily["time"])
                df_daily.set_index("time", inplace=True)
                all_daily.append(df_daily)

            if "hourly" in data:
                df_hourly = pd.DataFrame(data["hourly"])
                df_hourly["time"] = pd.to_datetime(df_hourly["time"])
                df_hourly.set_index("time", inplace=True)
                all_hourly.append(df_hourly)

            days = len(df_daily) if "daily" in data else 0
            hours = len(df_hourly) if "hourly" in data else 0
            print(f"OK ({days} days, {hours} hours)")
        else:
            print("FAILED")

        # Rate limiting - wait between requests
        time.sleep(OPENMETEO_DELAY)

    return all_daily, all_hourly


# ============================================================================
# JSON CREATION
# ============================================================================

def create_complete_json(noaa_daily, openmeteo_daily, openmeteo_hourly):
    """Create the complete hierarchical JSON structure."""

    print("\n" + "="*60)
    print("CREATING COMPLETE JSON ARCHIVE")
    print("="*60)

    archive = {
        "black_mountain_college_weather_archive": {
            "metadata": {
                "title": "Retcon Black Mountain - Complete Atmospheric Archive",
                "description": "Historical weather data for Black Mountain College, NC (1933-1957)",
                "project": "Retcon Black Mountain",
                "institution": "Eden Summer Institute",
                "location": {
                    "name": LOCATION_NAME,
                    "latitude": BMC_LATITUDE,
                    "longitude": BMC_LONGITUDE,
                    "elevation_m": 640,
                    "county": "Buncombe",
                    "state": "North Carolina"
                },
                "bmc_dates": {
                    "opening": "1933-09-25",
                    "closing": "1957-10-21",
                    "note": "Black Mountain College operated from 1933 to 1957"
                },
                "data_sources": {
                    "1933-1939": {
                        "source": "NOAA GHCN-Daily",
                        "stations": [f"{s[0]} ({s[1]})" for s in NOAA_STATIONS],
                        "primary_station": f"{NOAA_STATIONS[0][0]} ({NOAA_STATIONS[0][1]})",
                        "resolution": "daily",
                        "variables": ["temperature_max", "temperature_min", "precipitation", "snowfall", "snow_depth"]
                    },
                    "1940-1957": {
                        "source": "Open-Meteo Historical API (ERA5 Reanalysis)",
                        "resolution": "hourly + daily",
                        "grid_resolution": "0.25 degrees (~25km)",
                        "variables": "comprehensive (temperature, humidity, pressure, wind, clouds, radiation, soil)"
                    }
                },
                "units": {
                    "temperature": "Celsius (°C)",
                    "precipitation": "millimeters (mm)",
                    "snowfall": "millimeters (mm)",
                    "wind_speed": "km/h",
                    "wind_direction": "degrees (0-360)",
                    "pressure": "hPa",
                    "humidity": "percent (%)",
                    "cloud_cover": "percent (%)",
                    "visibility": "meters",
                    "radiation": "MJ/m²",
                    "soil_temperature": "Celsius (°C)",
                    "soil_moisture": "m³/m³"
                },
                "weather_codes": WEATHER_CODES,
                "generated_at": datetime.now().isoformat(),
                "total_days": 0,
                "total_hours": 0
            },
            "statistics": {},
            "years": {}
        }
    }

    root = archive["black_mountain_college_weather_archive"]

    # Combine daily data
    combined_daily = None
    if openmeteo_daily:
        combined_daily = pd.concat(openmeteo_daily).sort_index()

    combined_hourly = None
    if openmeteo_hourly:
        combined_hourly = pd.concat(openmeteo_hourly).sort_index()

    total_days = 0
    total_hours = 0

    # Process each year
    for year in range(1933, 1958):
        year_str = str(year)
        print(f"  Processing {year}...", end=" ", flush=True)

        year_entry = {
            "summary": {},
            "months": {}
        }

        year_days = 0
        year_hours = 0

        # Determine data source
        if year < 1940:
            # Use NOAA data
            year_entry["data_source"] = "NOAA GHCN-Daily"
            year_entry["resolution"] = "daily"

            if noaa_daily is not None and len(noaa_daily) > 0:
                year_data = noaa_daily[noaa_daily.index.year == year]

                if len(year_data) > 0:
                    # Process monthly
                    for month in range(1, 13):
                        month_str = f"{month:02d}"
                        month_data = year_data[year_data.index.month == month]

                        if len(month_data) == 0:
                            continue

                        month_entry = {
                            "days_recorded": len(month_data),
                            "days": {}
                        }

                        for idx, row in month_data.iterrows():
                            day_str = f"{idx.day:02d}"
                            day_entry = {"daily": {}}

                            if 'temperature_max_c' in row.index and pd.notna(row['temperature_max_c']):
                                day_entry["daily"]["temperature_max_c"] = round(float(row['temperature_max_c']), 1)
                            if 'temperature_min_c' in row.index and pd.notna(row['temperature_min_c']):
                                day_entry["daily"]["temperature_min_c"] = round(float(row['temperature_min_c']), 1)
                            if 'precipitation_mm' in row.index and pd.notna(row['precipitation_mm']):
                                day_entry["daily"]["precipitation_mm"] = round(float(row['precipitation_mm']), 1)
                            if 'snowfall_mm' in row.index and pd.notna(row['snowfall_mm']):
                                day_entry["daily"]["snowfall_mm"] = round(float(row['snowfall_mm']), 1)
                            if 'snow_depth_mm' in row.index and pd.notna(row['snow_depth_mm']):
                                day_entry["daily"]["snow_depth_mm"] = round(float(row['snow_depth_mm']), 1)

                            if day_entry["daily"]:
                                month_entry["days"][day_str] = day_entry
                                year_days += 1

                        if month_entry["days"]:
                            year_entry["months"][month_str] = month_entry

                    # Year summary
                    if year_days > 0:
                        summary = {"days_recorded": year_days}
                        if 'temperature_max_c' in year_data.columns:
                            summary["temperature_max_c"] = round(float(year_data['temperature_max_c'].max()), 1)
                        if 'temperature_min_c' in year_data.columns:
                            summary["temperature_min_c"] = round(float(year_data['temperature_min_c'].min()), 1)
                        if 'precipitation_mm' in year_data.columns:
                            summary["total_precipitation_mm"] = round(float(year_data['precipitation_mm'].sum()), 1)
                        year_entry["summary"] = summary
        else:
            # Use Open-Meteo data
            year_entry["data_source"] = "Open-Meteo ERA5"
            year_entry["resolution"] = "hourly"

            if combined_daily is not None:
                year_daily = combined_daily[combined_daily.index.year == year]
                year_hourly_data = combined_hourly[combined_hourly.index.year == year] if combined_hourly is not None else None

                if len(year_daily) > 0:
                    for month in range(1, 13):
                        month_str = f"{month:02d}"
                        month_daily = year_daily[year_daily.index.month == month]
                        month_hourly = year_hourly_data[year_hourly_data.index.month == month] if year_hourly_data is not None else None

                        if len(month_daily) == 0:
                            continue

                        month_entry = {
                            "days_recorded": len(month_daily),
                            "days": {}
                        }

                        for idx, row in month_daily.iterrows():
                            day_str = f"{idx.day:02d}"
                            day_entry = {"daily": {}, "hourly": {}}

                            # Daily data
                            for col in row.index:
                                val = row[col]
                                if pd.notna(val):
                                    if isinstance(val, float):
                                        day_entry["daily"][col] = round(val, 2)
                                    elif isinstance(val, (int, bool)):
                                        day_entry["daily"][col] = int(val)
                                    else:
                                        day_entry["daily"][col] = str(val)

                            # Hourly data for this day
                            if month_hourly is not None:
                                day_hourly = month_hourly[month_hourly.index.day == idx.day]
                                for hour_idx, hour_row in day_hourly.iterrows():
                                    hour_str = f"{hour_idx.hour:02d}:00"
                                    hour_entry = {}
                                    for col in hour_row.index:
                                        val = hour_row[col]
                                        if pd.notna(val):
                                            if isinstance(val, float):
                                                hour_entry[col] = round(val, 2)
                                            elif isinstance(val, (int, bool)):
                                                hour_entry[col] = int(val)
                                            else:
                                                hour_entry[col] = str(val)
                                    if hour_entry:
                                        day_entry["hourly"][hour_str] = hour_entry
                                        year_hours += 1

                            month_entry["days"][day_str] = day_entry
                            year_days += 1

                        year_entry["months"][month_str] = month_entry

                    # Year summary
                    year_entry["summary"] = {
                        "days_recorded": year_days,
                        "hours_recorded": year_hours,
                        "temperature_max_c": round(float(year_daily['temperature_2m_max'].max()), 1) if 'temperature_2m_max' in year_daily.columns else None,
                        "temperature_min_c": round(float(year_daily['temperature_2m_min'].min()), 1) if 'temperature_2m_min' in year_daily.columns else None,
                        "temperature_mean_c": round(float(year_daily['temperature_2m_mean'].mean()), 1) if 'temperature_2m_mean' in year_daily.columns else None,
                        "total_precipitation_mm": round(float(year_daily['precipitation_sum'].sum()), 1) if 'precipitation_sum' in year_daily.columns else None,
                        "total_snowfall_mm": round(float(year_daily['snowfall_sum'].sum()), 1) if 'snowfall_sum' in year_daily.columns else None
                    }

        root["years"][year_str] = year_entry
        total_days += year_days
        total_hours += year_hours
        print(f"{year_days} days, {year_hours} hours")

    # Update metadata
    root["metadata"]["total_days"] = total_days
    root["metadata"]["total_hours"] = total_hours

    # Overall statistics
    root["statistics"] = {
        "period": "1933-09 to 1957-12",
        "total_days": total_days,
        "total_hours": total_hours,
        "data_coverage": {
            "1933-1939": "daily (NOAA station)",
            "1940-1957": "hourly (ERA5 reanalysis)"
        }
    }

    return archive


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*70)
    print("BLACK MOUNTAIN COLLEGE - COMPLETE WEATHER ARCHIVE")
    print("="*70)
    print(f"\nLocation: {LOCATION_NAME}")
    print(f"Coordinates: {BMC_LATITUDE}°N, {BMC_LONGITUDE}°W")
    print(f"Period: September 1933 - December 1957")
    print(f"Output: {OUTPUT_DIR.absolute()}")

    # 1. Fetch NOAA data for 1933-1939
    noaa_daily = fetch_noaa_ghcn_daily()

    # 2. Fetch Open-Meteo data for 1940-1957
    openmeteo_daily, openmeteo_hourly = collect_openmeteo_all_years()

    # 3. Create complete JSON
    archive = create_complete_json(noaa_daily, openmeteo_daily, openmeteo_hourly)

    # 4. Save outputs
    print("\n" + "="*60)
    print("SAVING OUTPUT FILES")
    print("="*60)

    # Main JSON (pretty)
    json_file = OUTPUT_DIR / "bmc_weather_complete_1933-1957.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)
    size_mb = json_file.stat().st_size / (1024*1024)
    print(f"  {json_file.name}: {size_mb:.1f} MB")

    # Compact JSON
    compact_file = OUTPUT_DIR / "bmc_weather_complete_compact.json"
    with open(compact_file, "w", encoding="utf-8") as f:
        json.dump(archive, f, separators=(',', ':'), ensure_ascii=False)
    size_mb = compact_file.stat().st_size / (1024*1024)
    print(f"  {compact_file.name}: {size_mb:.1f} MB")

    # Save CSVs
    if openmeteo_daily:
        daily_df = pd.concat(openmeteo_daily).sort_index()
        csv_file = OUTPUT_DIR / "bmc_daily_1940-1957.csv"
        daily_df.to_csv(csv_file)
        print(f"  {csv_file.name}: {len(daily_df)} records")

    if openmeteo_hourly:
        hourly_df = pd.concat(openmeteo_hourly).sort_index()
        csv_file = OUTPUT_DIR / "bmc_hourly_1940-1957.csv"
        hourly_df.to_csv(csv_file)
        print(f"  {csv_file.name}: {len(hourly_df)} records")

    if noaa_daily is not None and len(noaa_daily) > 0:
        csv_file = OUTPUT_DIR / "bmc_noaa_daily_1933-1939.csv"
        noaa_daily.to_csv(csv_file)
        print(f"  {csv_file.name}: {len(noaa_daily)} records")

    print("\n" + "="*70)
    print("COMPLETE!")
    print("="*70)

    meta = archive["black_mountain_college_weather_archive"]["metadata"]
    print(f"\nTotal days: {meta['total_days']}")
    print(f"Total hours: {meta['total_hours']}")


if __name__ == "__main__":
    main()
