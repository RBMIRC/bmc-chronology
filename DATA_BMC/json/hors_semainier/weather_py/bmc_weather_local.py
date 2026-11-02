#!/usr/bin/env python3
"""
Black Mountain College Weather Archive Collector - Local Version
================================================================
Script to run on your local machine to collect historical weather data.

This script collects weather data from multiple sources:
1. Open-Meteo Historical API (ERA5 reanalysis) - 1940-1957 (free, no key)
2. NOAA GHCN-Daily via web_fetch - 1933-1957 (free, needs manual download)
3. Meteostat for station data (optional)

Black Mountain College: 35.6179° N, 82.3968° W
Period: September 1933 - December 1957

Usage:
    python bmc_weather_local.py

Requirements:
    pip install requests pandas openmeteo-requests requests-cache retry-requests

Author: Retcon Black Mountain Project
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time

# Try to import optional dependencies
try:
    import openmeteo_requests
    import requests_cache
    from retry_requests import retry
    OPENMETEO_SDK = True
except ImportError:
    OPENMETEO_SDK = False
    import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

BMC_LATITUDE = 35.6179
BMC_LONGITUDE = -82.3968
LOCATION_NAME = "Black Mountain, North Carolina"

# Date range for BMC
START_YEAR = 1933
END_YEAR = 1957
START_MONTH = 9  # September 1933 opening

OUTPUT_DIR = Path("./bmc_weather_archive")
OUTPUT_DIR.mkdir(exist_ok=True)

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
# DATA FETCHING FUNCTIONS
# ============================================================================

def fetch_openmeteo_data(start_date: str, end_date: str, hourly: bool = False) -> dict:
    """
    Fetch data from Open-Meteo Historical Weather API.
    Data available from 1940 onwards.
    """
    
    if OPENMETEO_SDK:
        # Use the official SDK with caching
        cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)
        
        params = {
            "latitude": BMC_LATITUDE,
            "longitude": BMC_LONGITUDE,
            "start_date": start_date,
            "end_date": end_date,
            "timezone": "America/New_York",
            "daily": [
                "weather_code", "temperature_2m_max", "temperature_2m_min",
                "temperature_2m_mean", "apparent_temperature_max", "apparent_temperature_min",
                "sunrise", "sunset", "daylight_duration", "sunshine_duration",
                "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours",
                "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"
            ]
        }
        
        if hourly:
            params["hourly"] = [
                "temperature_2m", "relative_humidity_2m", "dew_point_2m",
                "apparent_temperature", "precipitation", "rain", "snowfall",
                "weather_code", "pressure_msl", "cloud_cover",
                "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
            ]
        
        try:
            responses = openmeteo.weather_api("https://archive-api.open-meteo.com/v1/archive", params=params)
            return responses[0] if responses else None
        except Exception as e:
            print(f"  SDK Error: {e}")
            return None
    
    else:
        # Use direct requests
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
                "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"
            ])
        }
        
        if hourly:
            params["hourly"] = ",".join([
                "temperature_2m", "relative_humidity_2m", "dew_point_2m",
                "apparent_temperature", "precipitation", "rain", "snowfall",
                "weather_code", "pressure_msl", "cloud_cover",
                "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
            ])
        
        try:
            response = requests.get(base_url, params=params, timeout=120)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"  Request Error: {e}")
            return None


def collect_openmeteo_all_years(include_hourly: bool = False) -> tuple:
    """Collect all available Open-Meteo data for BMC period."""
    
    all_daily = []
    all_hourly = []
    
    print("\n" + "="*60)
    print("COLLECTING OPEN-METEO DATA (1940-1957)")
    print("="*60)
    
    for year in range(1940, 1958):
        print(f"  Fetching {year}...", end=" ", flush=True)
        
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        data = fetch_openmeteo_data(start_date, end_date, hourly=include_hourly)
        
        if data:
            # Process based on SDK or raw response
            if OPENMETEO_SDK:
                # SDK returns Response object
                daily_data = {
                    "time": pd.date_range(
                        start=pd.to_datetime(data.Daily().Time(), unit="s", utc=True),
                        end=pd.to_datetime(data.Daily().TimeEnd(), unit="s", utc=True),
                        freq=pd.Timedelta(seconds=data.Daily().Interval()),
                        inclusive="left"
                    )
                }
                daily_vars = [
                    "weather_code", "temperature_2m_max", "temperature_2m_min",
                    "temperature_2m_mean", "apparent_temperature_max", "apparent_temperature_min",
                    "sunrise", "sunset", "daylight_duration", "sunshine_duration",
                    "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours",
                    "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant"
                ]
                for i, var in enumerate(daily_vars):
                    daily_data[var] = data.Daily().Variables(i).ValuesAsNumpy()
                
                df_daily = pd.DataFrame(daily_data)
                df_daily.set_index("time", inplace=True)
                all_daily.append(df_daily)
            else:
                # Raw JSON response
                if "daily" in data:
                    df_daily = pd.DataFrame(data["daily"])
                    df_daily["time"] = pd.to_datetime(df_daily["time"])
                    df_daily.set_index("time", inplace=True)
                    all_daily.append(df_daily)
                
                if include_hourly and "hourly" in data:
                    df_hourly = pd.DataFrame(data["hourly"])
                    df_hourly["time"] = pd.to_datetime(df_hourly["time"])
                    df_hourly.set_index("time", inplace=True)
                    all_hourly.append(df_hourly)
            
            print("OK")
        else:
            print("FAILED")
        
        time.sleep(0.3)  # Rate limiting
    
    return all_daily, all_hourly


# ============================================================================
# JSON STRUCTURE CREATION
# ============================================================================

def create_archive_json(daily_dataframes: list, hourly_dataframes: list = None) -> dict:
    """Create the hierarchical JSON structure for the weather archive."""
    
    print("\n" + "="*60)
    print("CREATING JSON ARCHIVE STRUCTURE")
    print("="*60)
    
    archive = {
        "black_mountain_college_weather_archive": {
            "metadata": {
                "title": "Retcon Black Mountain - Atmospheric Archive",
                "description": "Historical weather data for Black Mountain College, NC (1933-1957)",
                "project": "Retcon Black Mountain",
                "location": {
                    "name": LOCATION_NAME,
                    "latitude": BMC_LATITUDE,
                    "longitude": BMC_LONGITUDE,
                    "elevation_m": 640,
                    "county": "Buncombe",
                    "state": "North Carolina"
                },
                "period": {
                    "requested": "1933-09 to 1957-12",
                    "bmc_opening": "1933-09-25",
                    "bmc_closing": "1957-10-21"
                },
                "data_sources": {
                    "primary": "Open-Meteo Historical Weather API (ERA5 Reanalysis)",
                    "era5_resolution": "0.25° (~25km)",
                    "temporal_resolution": "daily (hourly available)"
                },
                "data_availability": {
                    "1933-1939": {
                        "status": "NOT_AVAILABLE_IN_ERA5",
                        "reason": "ERA5 reanalysis begins 1940",
                        "alternatives": [
                            "NOAA GHCN-Daily (station data)",
                            "NOAA Climate Data Online",
                            "State Climate Office of North Carolina"
                        ]
                    },
                    "1940-1957": {
                        "status": "AVAILABLE",
                        "source": "ERA5 Reanalysis via Open-Meteo"
                    }
                },
                "units": {
                    "temperature": "°C",
                    "precipitation": "mm",
                    "snowfall": "mm",
                    "wind_speed": "km/h",
                    "wind_direction": "degrees",
                    "pressure": "hPa",
                    "humidity": "%",
                    "cloud_cover": "%",
                    "duration": "seconds"
                },
                "weather_codes": WEATHER_CODES,
                "generated_at": datetime.now().isoformat(),
                "notes": [
                    "ERA5 is reanalysis data combining observations with weather models",
                    "May differ slightly from actual station measurements",
                    "Pre-1940 data requires NOAA GHCN station records"
                ]
            },
            "statistics": {},
            "years": {}
        }
    }
    
    # Process data if available
    if daily_dataframes:
        combined = pd.concat(daily_dataframes).sort_index()
        
        # Overall statistics
        archive["black_mountain_college_weather_archive"]["statistics"] = {
            "total_days_available": len(combined),
            "date_range": {
                "first": str(combined.index.min().date()),
                "last": str(combined.index.max().date())
            },
            "temperature": {
                "overall_max_c": round(float(combined["temperature_2m_max"].max()), 1),
                "overall_min_c": round(float(combined["temperature_2m_min"].min()), 1),
                "mean_c": round(float(combined["temperature_2m_mean"].mean()), 1)
            },
            "precipitation": {
                "total_mm": round(float(combined["precipitation_sum"].sum()), 1),
                "max_daily_mm": round(float(combined["precipitation_sum"].max()), 1)
            }
        }
        
        # Process each year
        for year in range(START_YEAR, END_YEAR + 1):
            year_str = str(year)
            
            if year < 1940:
                archive["black_mountain_college_weather_archive"]["years"][year_str] = {
                    "status": "NO_DATA_PRE_ERA5",
                    "note": "ERA5 reanalysis data not available before 1940",
                    "months": {}
                }
                continue
            
            year_data = combined[combined.index.year == year]
            
            if year_data.empty:
                archive["black_mountain_college_weather_archive"]["years"][year_str] = {
                    "status": "NO_DATA",
                    "months": {}
                }
                continue
            
            year_entry = {
                "status": "AVAILABLE",
                "summary": {
                    "days_recorded": len(year_data),
                    "temp_max_c": round(float(year_data["temperature_2m_max"].max()), 1),
                    "temp_min_c": round(float(year_data["temperature_2m_min"].min()), 1),
                    "temp_mean_c": round(float(year_data["temperature_2m_mean"].mean()), 1),
                    "total_precip_mm": round(float(year_data["precipitation_sum"].sum()), 1),
                    "total_snow_mm": round(float(year_data["snowfall_sum"].sum()), 1)
                },
                "months": {}
            }
            
            # Process each month
            for month in range(1, 13):
                month_str = f"{month:02d}"
                month_data = year_data[year_data.index.month == month]
                
                if month_data.empty:
                    continue
                
                month_entry = {
                    "summary": {
                        "days_recorded": len(month_data),
                        "temp_max_c": round(float(month_data["temperature_2m_max"].max()), 1),
                        "temp_min_c": round(float(month_data["temperature_2m_min"].min()), 1),
                        "temp_mean_c": round(float(month_data["temperature_2m_mean"].mean()), 1),
                        "total_precip_mm": round(float(month_data["precipitation_sum"].sum()), 1)
                    },
                    "days": {}
                }
                
                # Process each day
                for idx, row in month_data.iterrows():
                    day_str = f"{idx.day:02d}"
                    
                    day_entry = {}
                    for col in row.index:
                        val = row[col]
                        if pd.notna(val):
                            if isinstance(val, float):
                                day_entry[col] = round(val, 2)
                            elif isinstance(val, (int, bool)):
                                day_entry[col] = int(val)
                            else:
                                day_entry[col] = str(val)
                    
                    month_entry["days"][day_str] = day_entry
                
                year_entry["months"][month_str] = month_entry
            
            archive["black_mountain_college_weather_archive"]["years"][year_str] = year_entry
            print(f"  Processed {year}: {len(year_data)} days")
    
    else:
        # Create empty structure for manual filling
        print("  Creating empty structure (no data collected)")
        for year in range(START_YEAR, END_YEAR + 1):
            archive["black_mountain_college_weather_archive"]["years"][str(year)] = {
                "status": "PENDING",
                "months": {}
            }
    
    return archive


# ============================================================================
# FILE OUTPUT
# ============================================================================

def save_outputs(archive: dict, daily_dfs: list, hourly_dfs: list = None):
    """Save all output files."""
    
    print("\n" + "="*60)
    print("SAVING OUTPUT FILES")
    print("="*60)
    
    # Main JSON archive (pretty)
    json_file = OUTPUT_DIR / "bmc_weather_archive_1933-1957.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(archive, f, indent=2, ensure_ascii=False)
    print(f"  ✓ {json_file.name}")
    
    # Compact JSON
    compact_file = OUTPUT_DIR / "bmc_weather_archive_compact.json"
    with open(compact_file, "w", encoding="utf-8") as f:
        json.dump(archive, f, separators=(',', ':'), ensure_ascii=False)
    print(f"  ✓ {compact_file.name}")
    
    # CSV exports
    if daily_dfs:
        combined_daily = pd.concat(daily_dfs).sort_index()
        csv_file = OUTPUT_DIR / "bmc_weather_daily_1940-1957.csv"
        combined_daily.to_csv(csv_file)
        print(f"  ✓ {csv_file.name} ({len(combined_daily)} records)")
    
    if hourly_dfs:
        combined_hourly = pd.concat(hourly_dfs).sort_index()
        hourly_file = OUTPUT_DIR / "bmc_weather_hourly_1940-1957.csv"
        combined_hourly.to_csv(hourly_file)
        print(f"  ✓ {hourly_file.name} ({len(combined_hourly)} records)")
    
    # Summary report
    create_summary_report(archive, daily_dfs)


def create_summary_report(archive: dict, daily_dfs: list):
    """Generate summary report."""
    
    report = []
    report.append("=" * 70)
    report.append("BLACK MOUNTAIN COLLEGE WEATHER ARCHIVE")
    report.append("Retcon Black Mountain Project")
    report.append("=" * 70)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\nLocation: {LOCATION_NAME}")
    report.append(f"Coordinates: {BMC_LATITUDE}°N, {BMC_LONGITUDE}°W")
    
    if daily_dfs:
        combined = pd.concat(daily_dfs).sort_index()
        report.append(f"\nData available: {combined.index.min().date()} to {combined.index.max().date()}")
        report.append(f"Total days: {len(combined)}")
        
        report.append("\n" + "-" * 70)
        report.append("ANNUAL SUMMARY")
        report.append("-" * 70)
        
        for year in range(1940, 1958):
            year_data = combined[combined.index.year == year]
            if not year_data.empty:
                report.append(f"\n{year}:")
                report.append(f"  Temperature: {year_data['temperature_2m_min'].min():.1f}°C to {year_data['temperature_2m_max'].max():.1f}°C")
                report.append(f"  Mean temp: {year_data['temperature_2m_mean'].mean():.1f}°C")
                report.append(f"  Precipitation: {year_data['precipitation_sum'].sum():.1f} mm")
                report.append(f"  Snowfall: {year_data['snowfall_sum'].sum():.1f} mm")
    
    report.append("\n" + "-" * 70)
    report.append("DATA GAPS: 1933-1939")
    report.append("-" * 70)
    report.append("""
For weather data from 1933-1939, you will need to use NOAA GHCN-Daily:

1. Get an API token: https://www.ncdc.noaa.gov/cdo-web/token

2. Search for nearby stations:
   - ASHEVILLE NC US (USC00310300) - has data from 1867
   - WAYNESVILLE NC US - nearby cooperative station
   - BLACK MOUNTAIN NC US (if exists)

3. Use the Climate Data Online search:
   https://www.ncei.noaa.gov/cdo-web/search

4. Or download GHCN-Daily files directly:
   https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/

Station ID format: USC00XXXXXX or USW00XXXXXX
""")
    
    report_text = "\n".join(report)
    report_file = OUTPUT_DIR / "README_bmc_weather.txt"
    with open(report_file, "w") as f:
        f.write(report_text)
    print(f"  ✓ {report_file.name}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution."""
    
    print("\n" + "=" * 70)
    print("BLACK MOUNTAIN COLLEGE WEATHER ARCHIVE COLLECTOR")
    print("=" * 70)
    print(f"\nLocation: {LOCATION_NAME}")
    print(f"Coordinates: {BMC_LATITUDE}°N, {BMC_LONGITUDE}°W")
    print(f"Period: September {START_YEAR} - December {END_YEAR}")
    print(f"Output: {OUTPUT_DIR.absolute()}")
    
    if OPENMETEO_SDK:
        print("\n[✓] Using Open-Meteo SDK with caching")
    else:
        print("\n[!] Open-Meteo SDK not available, using direct requests")
        print("    Install: pip install openmeteo-requests requests-cache retry-requests")
    
    # Collect data
    # Set include_hourly=True if you want hourly data (much larger files)
    daily_dfs, hourly_dfs = collect_openmeteo_all_years(include_hourly=False)
    
    # Create JSON structure
    archive = create_archive_json(daily_dfs, hourly_dfs)
    
    # Save outputs
    save_outputs(archive, daily_dfs, hourly_dfs)
    
    print("\n" + "=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)
    
    # List output files
    print(f"\nOutput files in {OUTPUT_DIR}:")
    for f in sorted(OUTPUT_DIR.glob("*")):
        size = f.stat().st_size
        if size > 1024*1024:
            size_str = f"{size/1024/1024:.1f} MB"
        elif size > 1024:
            size_str = f"{size/1024:.1f} KB"
        else:
            size_str = f"{size} bytes"
        print(f"  - {f.name} ({size_str})")


if __name__ == "__main__":
    main()
