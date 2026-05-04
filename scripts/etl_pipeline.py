import os, sys, time, math, warnings, requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
from colorama import Fore, Style, init

warnings.filterwarnings("ignore")
init(autoreset=True)

# ── Configuration ──────────────────────────────────────────────────────────
CONFIG = {
    "api_base"     : "https://archive-api.open-meteo.com/v1/archive",
    "target_rows"  : 1_000_000,
    "output_dir"   : "./weather_powerbi_output",
    "start_year"   : 2015,
    "end_year"     : 2024,
    "request_delay": 0.3,          # seconds between API calls (be polite)
    "random_seed"  : 42,
}
 
OUTPUT_DIR = CONFIG["output_dir"]
os.makedirs(OUTPUT_DIR, exist_ok=True)
np.random.seed(CONFIG["random_seed"])# ── Configuration ──────────────────────────────────────────────────────────
CONFIG = {
    "api_base"     : "https://archive-api.open-meteo.com/v1/archive",
    "target_rows"  : 1_000_000,
    "output_dir"   : "./weather_powerbi_output",
    "start_year"   : 2015,
    "end_year"     : 2024,
    "request_delay": 0.3,          # seconds between API calls (be polite)
    "random_seed"  : 42,
}
 
OUTPUT_DIR = CONFIG["output_dir"]
os.makedirs(OUTPUT_DIR, exist_ok=True)
np.random.seed(CONFIG["random_seed"])

# ── 50 Major World Cities ──────────────────────────────────────────────────
CITIES = [
    # (name, country, latitude, longitude, climate_zone, continent)
    ("New York",       "USA",           40.71, -74.01, "Humid Continental",  "North America"),
    ("Los Angeles",    "USA",           34.05,-118.24, "Mediterranean",       "North America"),
    ("Chicago",        "USA",           41.88, -87.63, "Humid Continental",  "North America"),
    ("Houston",        "USA",           29.76, -95.37, "Humid Subtropical",  "North America"),
    ("Phoenix",        "USA",           33.45,-112.07, "Desert",             "North America"),
    ("Toronto",        "Canada",        43.65, -79.38, "Humid Continental",  "North America"),
    ("Mexico City",    "Mexico",        19.43, -99.13, "Subtropical Highland","North America"),
    ("London",         "UK",            51.51,  -0.13, "Oceanic",            "Europe"),
    ("Paris",          "France",        48.85,   2.35, "Oceanic",            "Europe"),
    ("Berlin",         "Germany",       52.52,  13.40, "Oceanic",            "Europe"),
    ("Madrid",         "Spain",         40.42,  -3.70, "Mediterranean",      "Europe"),
    ("Rome",           "Italy",         41.90,  12.50, "Mediterranean",      "Europe"),
    ("Amsterdam",      "Netherlands",   52.37,   4.90, "Oceanic",            "Europe"),
    ("Vienna",         "Austria",       48.21,  16.37, "Humid Continental",  "Europe"),
    ("Warsaw",         "Poland",        52.23,  21.01, "Humid Continental",  "Europe"),
    ("Stockholm",      "Sweden",        59.33,  18.07, "Subarctic",          "Europe"),
    ("Oslo",           "Norway",        59.91,  10.75, "Subarctic",          "Europe"),
    ("Zurich",         "Switzerland",   47.38,   8.54, "Oceanic",            "Europe"),
    ("Istanbul",       "Turkey",        41.01,  28.95, "Mediterranean",      "Europe"),
    ("Athens",         "Greece",        37.98,  23.73, "Mediterranean",      "Europe"),
    ("Moscow",         "Russia",        55.75,  37.62, "Subarctic",          "Asia"),
    ("Dubai",          "UAE",           25.20,  55.27, "Desert",             "Asia"),
    ("Mumbai",         "India",         19.08,  72.88, "Tropical Monsoon",   "Asia"),
    ("Delhi",          "India",         28.61,  77.21, "Semi-Arid",          "Asia"),
    ("Bangalore",      "India",         12.97,  77.59, "Tropical Savanna",   "Asia"),
    ("Tokyo",          "Japan",         35.68, 139.69, "Humid Subtropical",  "Asia"),
    ("Beijing",        "China",         39.90, 116.41, "Humid Continental",  "Asia"),
    ("Shanghai",       "China",         31.23, 121.47, "Humid Subtropical",  "Asia"),
    ("Singapore",      "Singapore",      1.35, 103.82, "Tropical Rainforest","Asia"),
    ("Bangkok",        "Thailand",      13.75, 100.52, "Tropical Savanna",   "Asia"),
    ("Seoul",          "South Korea",   37.57, 126.98, "Humid Continental",  "Asia"),
    ("Hong Kong",      "China",         22.32, 114.17, "Humid Subtropical",  "Asia"),
    ("Kuala Lumpur",   "Malaysia",       3.14, 101.69, "Tropical Rainforest","Asia"),
    ("Jakarta",        "Indonesia",     -6.21, 106.85, "Tropical Rainforest","Asia"),
    ("Riyadh",         "Saudi Arabia",  24.69,  46.72, "Desert",             "Asia"),
    ("Cairo",          "Egypt",         30.06,  31.25, "Desert",             "Africa"),
    ("Lagos",          "Nigeria",        6.52,   3.38, "Tropical Savanna",   "Africa"),
    ("Nairobi",        "Kenya",         -1.29,  36.82, "Tropical Savanna",   "Africa"),
    ("Johannesburg",   "South Africa", -26.20,  28.04, "Semi-Arid",          "Africa"),
    ("Casablanca",     "Morocco",       33.59,  -7.62, "Mediterranean",      "Africa"),
    ("São Paulo",      "Brazil",       -23.55, -46.63, "Humid Subtropical",  "South America"),
    ("Buenos Aires",   "Argentina",    -34.61, -58.38, "Humid Subtropical",  "South America"),
    ("Lima",           "Peru",         -12.05, -77.04, "Desert",             "South America"),
    ("Bogotá",         "Colombia",       4.71, -74.07, "Subtropical Highland","South America"),
    ("Santiago",       "Chile",        -33.46, -70.65, "Mediterranean",      "South America"),
    ("Sydney",         "Australia",    -33.87, 151.21, "Humid Subtropical",  "Oceania"),
    ("Melbourne",      "Australia",    -37.81, 144.96, "Oceanic",            "Oceania"),
    ("Auckland",       "New Zealand",  -36.86, 174.77, "Oceanic",            "Oceania"),
    ("Honolulu",       "USA",           21.31,-157.86, "Tropical Savanna",   "Oceania"),
    ("Anchorage",      "USA",           61.22,-149.90, "Subarctic",          "North America"),
]
 
 
# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def log(msg, color=Fore.CYAN):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{ts}] {msg}{Style.RESET_ALL}")
 
def separator(title=""):
    w = 70
    if title:
        pad = (w - len(title) - 2) // 2
        print(Fore.YELLOW + "─"*pad + f" {title} " + "─"*pad)
    else:
        print(Fore.YELLOW + "─"*w)
 
def progress_bar(iterable, desc, total=None):
    return tqdm(iterable, desc=desc, total=total, colour="cyan",
                unit="city", ncols=90)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 1. EXTRACT
# ─────────────────────────────────────────────────────────────────────────────
 
HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "dew_point_2m",
    "apparent_temperature",
    "precipitation",
    "rain",
    "snowfall",
    "snow_depth",
    "pressure_msl",
    "surface_pressure",
    "cloud_cover",
    "wind_speed_10m",
    "wind_direction_10m",
    "wind_gusts_10m",
    "shortwave_radiation",
    "et0_fao_evapotranspiration",
    "weather_code",
]
 
def fetch_city(city_row: tuple, start: str, end: str) -> pd.DataFrame | None:
    """Fetch hourly weather for one city from Open-Meteo Historical API."""
    name, country, lat, lon, climate, continent = city_row
    params = {
        "latitude"       : lat,
        "longitude"      : lon,
        "start_date"     : start,
        "end_date"       : end,
        "hourly"         : ",".join(HOURLY_VARS),
        "timezone"       : "auto",
        "wind_speed_unit": "mph",
        "temperature_unit": "celsius",
        "precipitation_unit": "mm",
    }
    try:
        r = requests.get(CONFIG["api_base"], params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        hourly = data.get("hourly", {})
        if not hourly or "time" not in hourly:
            return None
        df = pd.DataFrame(hourly)
        df["city"]        = name
        df["country"]     = country
        df["latitude"]    = lat
        df["longitude"]   = lon
        df["climate_zone"]= climate
        df["continent"]   = continent
        return df
    except Exception as e:
        log(f"  ⚠  {name}: {e}", Fore.RED)
        return None
 
 
def extract() -> pd.DataFrame:
    separator("EXTRACT – Open-Meteo Historical Weather API")
    target   = CONFIG["target_rows"]
    start_yr = CONFIG["start_year"]
    end_yr   = CONFIG["end_year"]
 
    log(f"Target rows : {target:,}")
    log(f"Period      : {start_yr}–{end_yr}")
    log(f"Cities      : {len(CITIES)} global cities")
    log(f"Variables   : {len(HOURLY_VARS)} hourly metrics per city")
    log("Starting API calls …\n")
 
    all_frames = []
    total_rows = 0
    city_count = 0
 
    start_date = f"{start_yr}-01-01"
    end_date   = f"{end_yr}-12-31"
 
    for city in progress_bar(CITIES, "Fetching cities"):
        if total_rows >= target:
            break
 
        df = fetch_city(city, start_date, end_date)
        if df is not None and len(df) > 0:
            all_frames.append(df)
            total_rows += len(df)
            city_count += 1
            log(f"  ✔  {city[0]:<18} {len(df):>7,} rows  (total so far: {total_rows:,})",
                Fore.GREEN)
 
        time.sleep(CONFIG["request_delay"])
 
    if not all_frames:
        log("API returned no data. Generating fully synthetic dataset.", Fore.YELLOW)
        return generate_synthetic_weather(target)
 
    raw = pd.concat(all_frames, ignore_index=True)
    log(f"\nExtracted {len(raw):,} rows from {city_count} cities.", Fore.GREEN)
 
    if len(raw) < target:
        shortfall = target - len(raw)
        log(f"Generating {shortfall:,} synthetic rows to reach target.", Fore.MAGENTA)
        synth = generate_synthetic_weather(shortfall)
        raw   = pd.concat([raw, synth], ignore_index=True)
 
    return raw.head(target)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 1b. SYNTHETIC FALLBACK
# ─────────────────────────────────────────────────────────────────────────────
def generate_synthetic_weather(n: int) -> pd.DataFrame:
    """Realistic synthetic hourly weather data as API fallback / top-up."""
    log(f"Generating {n:,} synthetic weather rows …", Fore.MAGENTA)
    city_sample = [c for c in CITIES]
    rng_cities  = [city_sample[i % len(city_sample)] for i in range(n)]
 
    hours = pd.date_range("2015-01-01", periods=n, freq="h")
    hour_of_day = hours.hour
    month       = hours.month
 
    # Seasonal temperature envelope
    base_temp = 15 + 12 * np.sin((month - 3) * np.pi / 6)
    temp      = base_temp + np.random.normal(0, 5, n)
    humidity  = np.clip(50 + np.random.normal(0, 20, n), 10, 100)
    dew_point = temp - ((100 - humidity) / 5)
    rain      = np.random.exponential(0.3, n) * (np.random.rand(n) < 0.15)
    snow      = np.random.exponential(0.1, n) * (temp < 2) * (np.random.rand(n) < 0.10)
    wind      = np.abs(np.random.normal(10, 6, n))
    pressure  = np.random.normal(1013, 8, n)
    cloud     = np.clip(np.random.normal(50, 30, n), 0, 100)
    radiation = np.clip(800 * np.sin(np.pi * hour_of_day / 24) + np.random.normal(0, 50, n), 0, 1000)
    w_codes   = np.random.choice([0,1,2,3,51,61,71,80,95], n, p=[.3,.15,.1,.1,.1,.1,.05,.07,.03])
    gusts     = wind * np.random.uniform(1.2, 2.0, n)
    app_temp  = temp - 2 * (wind > 15)
 
    df = pd.DataFrame({
        "time"                       : hours.strftime("%Y-%m-%dT%H:%M"),
        "temperature_2m"             : temp.round(1),
        "relative_humidity_2m"       : humidity.round(0).astype(int),
        "dew_point_2m"               : dew_point.round(1),
        "apparent_temperature"       : app_temp.round(1),
        "precipitation"              : (rain + snow).round(2),
        "rain"                       : rain.round(2),
        "snowfall"                   : snow.round(2),
        "snow_depth"                 : (snow * 10).round(1),
        "pressure_msl"               : pressure.round(1),
        "surface_pressure"           : (pressure - 2).round(1),
        "cloud_cover"                : cloud.round(0).astype(int),
        "wind_speed_10m"             : wind.round(1),
        "wind_direction_10m"         : np.random.randint(0, 360, n),
        "wind_gusts_10m"             : gusts.round(1),
        "shortwave_radiation"        : radiation.round(1),
        "et0_fao_evapotranspiration" : np.clip(radiation / 500, 0, 5).round(2),
        "weather_code"               : w_codes,
        "city"        : [c[0] for c in rng_cities],
        "country"     : [c[1] for c in rng_cities],
        "latitude"    : [c[2] for c in rng_cities],
        "longitude"   : [c[3] for c in rng_cities],
        "climate_zone": [c[4] for c in rng_cities],
        "continent"   : [c[5] for c in rng_cities],
    })
    return df

# ─────────────────────────────────────────────────────────────────────────────
# 2. TRANSFORM
# ─────────────────────────────────────────────────────────────────────────────
 
WMO_CODES = {
    0:"Clear Sky", 1:"Mainly Clear", 2:"Partly Cloudy", 3:"Overcast",
    45:"Fog", 48:"Icy Fog",
    51:"Light Drizzle", 53:"Moderate Drizzle", 55:"Heavy Drizzle",
    61:"Slight Rain", 63:"Moderate Rain", 65:"Heavy Rain",
    71:"Slight Snow", 73:"Moderate Snow", 75:"Heavy Snow",
    77:"Snow Grains",
    80:"Slight Showers", 81:"Moderate Showers", 82:"Violent Showers",
    85:"Slight Snow Showers", 86:"Heavy Snow Showers",
    95:"Thunderstorm", 96:"Thunderstorm+Hail", 99:"Thunderstorm+Heavy Hail",
}
 
def wind_direction_label(deg):
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
            "S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[int((deg % 360) / 22.5 + 0.5) % 16]
 
def heat_index(T, RH):
    """Steadman Heat Index (°C). Valid for T > 27°C, RH > 40%."""
    HI = (-8.78469475556
          + 1.61139411 * T
          + 2.33854883889 * RH
          - 0.14611605 * T * RH
          - 0.012308094 * T**2
          - 0.0164248277778 * RH**2
          + 0.002211732 * T**2 * RH
          + 0.00072546 * T * RH**2
          - 0.000003582 * T**2 * RH**2)
    return np.where(T > 27, HI, T)
 
def wind_chill(T, V):
    """Wind Chill (°C). Valid for T < 10°C, V > 4.8 km/h."""
    mph_to_kph = 1.60934
    V_kph = V * mph_to_kph
    WC = (13.12 + 0.6215*T - 11.37*(V_kph**0.16) + 0.3965*T*(V_kph**0.16))
    return np.where((T < 10) & (V_kph > 4.8), WC, T)
 
 
def transform(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    separator("TRANSFORM")
    log(f"Raw rows: {len(df):,}")
 
    # ── 2.1 Parse datetime ──────────────────────────────────────────────────
    df["datetime"] = pd.to_datetime(df["time"], errors="coerce")
    df = df[df["datetime"].notna()]
 
    # ── 2.2 Cast numerics ───────────────────────────────────────────────────
    num_cols = [
        "temperature_2m","relative_humidity_2m","dew_point_2m",
        "apparent_temperature","precipitation","rain","snowfall","snow_depth",
        "pressure_msl","surface_pressure","cloud_cover","wind_speed_10m",
        "wind_direction_10m","wind_gusts_10m","shortwave_radiation",
        "et0_fao_evapotranspiration","weather_code",
        "latitude","longitude",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
 
    # ── 2.3 Drop bad rows ───────────────────────────────────────────────────
    before = len(df)
    df = df[df["temperature_2m"].between(-90, 60)]
    df = df[df["relative_humidity_2m"].between(0, 100)]
    df = df[df["wind_speed_10m"] >= 0]
    df = df[df["precipitation"] >= 0]
    log(f"Removed {before-len(df):,} invalid rows → {len(df):,} clean rows.", Fore.GREEN)
 
    # ── 2.4 Time Features ───────────────────────────────────────────────────
    log("Engineering time features …")
    df["hour"]          = df["datetime"].dt.hour
    df["date"]          = df["datetime"].dt.date
    df["day_of_week"]   = df["datetime"].dt.dayofweek
    df["day_name"]      = df["datetime"].dt.day_name()
    df["month"]         = df["datetime"].dt.month
    df["month_name"]    = df["datetime"].dt.month_name()
    df["year"]          = df["datetime"].dt.year
    df["quarter"]       = df["datetime"].dt.quarter
    df["week"]          = df["datetime"].dt.isocalendar().week.astype(int)
    df["is_weekend"]    = df["day_of_week"].isin([5,6]).astype(int)
    df["date_id"]       = df["datetime"].dt.strftime("%Y%m%d").astype(int)
 
    # Season (Northern Hemisphere default; flipped for southern cities)
    south = df["latitude"] < 0
    month = df["month"]
    def season(m, is_south):
        if   m in [12,1,2]: s = "Winter" if not is_south else "Summer"
        elif m in [3,4,5]:  s = "Spring" if not is_south else "Autumn"
        elif m in [6,7,8]:  s = "Summer" if not is_south else "Winter"
        else:                s = "Autumn" if not is_south else "Spring"
        return s
    df["season"] = [season(m, s) for m, s in zip(df["month"], south)]
 
    # Time of day bucket
    def tod(h):
        if   h < 6:  return "Night"
        elif h < 12: return "Morning"
        elif h < 18: return "Afternoon"
        else:        return "Evening"
    df["time_of_day"] = df["hour"].map(tod)
 
    # ── 2.5 Weather Derived Metrics ─────────────────────────────────────────
    log("Computing derived weather metrics …")
    T  = df["temperature_2m"].values
    RH = df["relative_humidity_2m"].values
    V  = df["wind_speed_10m"].values
 
    df["heat_index_c"]   = heat_index(T, RH).round(1)
    df["wind_chill_c"]   = wind_chill(T, V).round(1)
    df["temp_fahrenheit"]= (T * 9/5 + 32).round(1)
    df["feels_like_f"]   = (df["apparent_temperature"] * 9/5 + 32).round(1)
 
    # Comfort Index (0=unbearable, 100=perfect)
    comfort = 100 - np.abs(T - 21) * 3 - (RH - 50).clip(0) * 0.5 - V * 0.5
    df["comfort_index"] = comfort.clip(0, 100).round(1)
 
    # Weather description from WMO code
    df["weather_description"] = df["weather_code"].map(WMO_CODES).fillna("Unknown")
 
    # Weather category (broad)
    def wx_cat(code):
        if   code == 0:           return "Clear"
        elif code in [1,2,3]:     return "Cloudy"
        elif code in [45,48]:     return "Fog"
        elif 50 <= code <= 57:    return "Drizzle"
        elif 60 <= code <= 67:    return "Rain"
        elif 70 <= code <= 77:    return "Snow"
        elif 80 <= code <= 82:    return "Showers"
        elif 85 <= code <= 86:    return "Snow Showers"
        elif code >= 95:          return "Thunderstorm"
        return "Unknown"
    df["weather_category"] = df["weather_code"].map(wx_cat)
 
    # Wind direction label
    df["wind_dir_label"] = df["wind_direction_10m"].apply(
        lambda x: wind_direction_label(x) if pd.notna(x) else "Unknown"
    )
 
    # Wind speed category (Beaufort-like)
    df["wind_category"] = pd.cut(
        df["wind_speed_10m"],
        bins  = [-1, 5, 12, 20, 30, 999],
        labels= ["Calm","Breeze","Moderate","Strong","Storm"]
    ).astype(str)
 
    # Temperature category
    df["temp_category"] = pd.cut(
        T,
        bins  = [-90, 0, 10, 20, 30, 60],
        labels= ["Freezing","Cold","Cool","Warm","Hot"]
    ).astype(str)
 
    # Precipitation intensity
    df["precip_intensity"] = pd.cut(
        df["precipitation"],
        bins  = [-0.01, 0, 2, 10, 30, 9999],
        labels= ["None","Light","Moderate","Heavy","Extreme"]
    ).astype(str)
 
    # Solar radiation bucket
    df["radiation_level"] = pd.cut(
        df["shortwave_radiation"].fillna(0),
        bins  = [-1, 0, 200, 500, 800, 9999],
        labels= ["Night","Low","Moderate","High","Intense"]
    ).astype(str)
 
    # Humidity comfort
    df["humidity_comfort"] = pd.cut(
        RH,
        bins  = [0, 30, 50, 70, 100],
        labels= ["Dry","Comfortable","Humid","Very Humid"]
    ).astype(str)
 
    # ── 2.6 Anomaly Flags ───────────────────────────────────────────────────
    log("Flagging extreme events …")
    # Per-city monthly means for anomaly
    city_monthly = df.groupby(["city","month"])["temperature_2m"].transform("mean")
    city_monthly_std = df.groupby(["city","month"])["temperature_2m"].transform("std")
    df["temp_anomaly_c"]   = (df["temperature_2m"] - city_monthly).round(2)
    df["temp_anomaly_std"] = ((df["temperature_2m"] - city_monthly) / city_monthly_std.clip(0.1)).round(2)
    df["is_extreme_heat"]  = (df["temp_anomaly_std"] > 2.5).astype(int)
    df["is_extreme_cold"]  = (df["temp_anomaly_std"] < -2.5).astype(int)
    df["is_heavy_rain"]    = (df["rain"] > 20).astype(int)
    df["is_heavy_snow"]    = (df["snowfall"] > 10).astype(int)
    df["is_high_wind"]     = (df["wind_speed_10m"] > 40).astype(int)
    df["is_extreme_event"] = (
        df[["is_extreme_heat","is_extreme_cold",
            "is_heavy_rain","is_heavy_snow","is_high_wind"]].max(axis=1)
    )
 
    # ── 2.7 Unique row ID & date surrogate ──────────────────────────────────
    df.reset_index(drop=True, inplace=True)
    df["record_id"] = "W" + (df.index + 1).astype(str).str.zfill(8)
 
    log("Feature engineering complete.", Fore.GREEN)
 
    # ── 2.8 Build Star Schema Tables ────────────────────────────────────────
    separator("BUILD STAR SCHEMA")
 
    # FACT TABLE
    fact_cols = [
        "record_id","date_id","city","country","continent","climate_zone",
        "latitude","longitude","datetime",
        "temperature_2m","temp_fahrenheit","apparent_temperature","feels_like_f",
        "heat_index_c","wind_chill_c","dew_point_2m","relative_humidity_2m",
        "precipitation","rain","snowfall","snow_depth",
        "pressure_msl","cloud_cover",
        "wind_speed_10m","wind_direction_10m","wind_gusts_10m",
        "shortwave_radiation","et0_fao_evapotranspiration",
        "weather_code","weather_description","weather_category",
        "temp_category","wind_category","precip_intensity",
        "humidity_comfort","radiation_level","time_of_day",
        "comfort_index","temp_anomaly_c","temp_anomaly_std",
        "is_extreme_heat","is_extreme_cold","is_heavy_rain",
        "is_heavy_snow","is_high_wind","is_extreme_event",
        "season","is_weekend","hour","year","month","quarter",
    ]
    fact_cols = [c for c in fact_cols if c in df.columns]
    fact_weather = df[fact_cols].copy()
    log(f"fact_weather     : {len(fact_weather):,} rows × {len(fact_weather.columns)} cols")
 
    # DIM: Date
    dim_date = (
        df[["date_id","date","year","month","month_name","quarter",
            "week","day_of_week","day_name","season","is_weekend"]]
        .drop_duplicates("date_id")
        .sort_values("date_id")
    )
    log(f"dim_date         : {len(dim_date):,} rows")
 
    # DIM: City
    dim_city = pd.DataFrame(CITIES, columns=[
        "city","country","latitude","longitude","climate_zone","continent"
    ]).drop_duplicates("city")
    # Enrich with Köppen classification details
    koppen_desc = {
        "Tropical Rainforest" : "Hot & wet year-round, no dry season",
        "Tropical Savanna"    : "Hot year-round, distinct wet & dry seasons",
        "Desert"              : "Very low precipitation, extreme temperatures",
        "Semi-Arid"           : "Low rainfall, hot summers",
        "Mediterranean"       : "Hot dry summers, mild wet winters",
        "Oceanic"             : "Mild temps year-round, high rainfall",
        "Humid Subtropical"   : "Hot humid summers, mild winters",
        "Humid Continental"   : "Large temp swings, 4 distinct seasons",
        "Subarctic"           : "Very cold winters, short cool summers",
        "Subtropical Highland": "Mild year-round due to altitude",
    }
    dim_city["climate_description"] = dim_city["climate_zone"].map(koppen_desc)
    log(f"dim_city         : {len(dim_city):,} rows")
 
    # DIM: Weather Code
    dim_weather_code = pd.DataFrame([
        {"weather_code": k, "weather_description": v,
         "weather_category": wx_cat(k)}
        for k, v in WMO_CODES.items()
    ])
    log(f"dim_weather_code : {len(dim_weather_code):,} rows")
 
    # AGG: Daily City Summary (for trend charts)
    log("Building daily aggregation …")
    agg_daily = (
        fact_weather.groupby(["date_id","city","country","continent","climate_zone","year","month","season"])
        .agg(
            avg_temp        = ("temperature_2m","mean"),
            max_temp        = ("temperature_2m","max"),
            min_temp        = ("temperature_2m","min"),
            avg_humidity    = ("relative_humidity_2m","mean"),
            total_precip    = ("precipitation","sum"),
            total_rain      = ("rain","sum"),
            total_snow      = ("snowfall","sum"),
            avg_wind        = ("wind_speed_10m","mean"),
            max_wind        = ("wind_gusts_10m","max"),
            avg_pressure    = ("pressure_msl","mean"),
            avg_cloud       = ("cloud_cover","mean"),
            avg_comfort     = ("comfort_index","mean"),
            avg_radiation   = ("shortwave_radiation","mean"),
            extreme_events  = ("is_extreme_event","sum"),
            rainy_hours     = ("is_heavy_rain","sum"),
        )
        .reset_index()
        .round(2)
    )
    log(f"agg_daily        : {len(agg_daily):,} rows")
 
    # AGG: Monthly Climate Normals per city
    log("Building monthly climate normals …")
    agg_monthly = (
        fact_weather.groupby(["city","country","continent","climate_zone","month","season"])
        .agg(
            avg_temp        = ("temperature_2m","mean"),
            avg_max_temp    = ("temperature_2m", "max"),
            avg_min_temp    = ("temperature_2m",lambda x: x.min()),
            avg_humidity    = ("relative_humidity_2m","mean"),
            avg_precip      = ("precipitation","mean"),
            total_precip    = ("precipitation","sum"),
            avg_wind        = ("wind_speed_10m","mean"),
            avg_comfort     = ("comfort_index","mean"),
            extreme_events  = ("is_extreme_event","sum"),
        )
        .reset_index()
        .round(2)
    )
    log(f"agg_monthly      : {len(agg_monthly):,} rows")
 
    # AGG: Extreme Events Log
    agg_extremes = fact_weather[fact_weather["is_extreme_event"] == 1][[
        "record_id","date_id","city","country","datetime","temperature_2m",
        "precipitation","wind_speed_10m","snowfall","weather_description",
        "weather_category","temp_anomaly_c","temp_anomaly_std",
        "is_extreme_heat","is_extreme_cold","is_heavy_rain",
        "is_heavy_snow","is_high_wind",
    ]].copy()
    log(f"agg_extremes     : {len(agg_extremes):,} extreme event rows")
 
    return {
        "fact_weather"    : fact_weather,
        "dim_date"        : dim_date,
        "dim_city"        : dim_city,
        "dim_weather_code": dim_weather_code,
        "agg_daily"       : agg_daily,
        "agg_monthly"     : agg_monthly,
        "agg_extremes"    : agg_extremes,
    }
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 3. LOAD
# ─────────────────────────────────────────────────────────────────────────────
 
def load(tables: dict[str, pd.DataFrame]) -> list[dict]:
    separator("LOAD → CSV for Power BI")
    summary = []
    for name, df in tables.items():
        path     = os.path.join(OUTPUT_DIR, f"{name}.csv")
        df.to_csv(path, index=False)
        size_mb  = os.path.getsize(path) / 1_048_576
        log(f"✔  {name:<22} → {len(df):>9,} rows  |  {size_mb:6.1f} MB  →  {path}", Fore.GREEN)
        summary.append({"table": name, "rows": len(df),
                        "size_mb": round(size_mb,1), "path": path})
    return summary
 
 
# ─────────────────────────────────────────────────────────────────────────────
# 5. MAIN
# ─────────────────────────────────────────────────────────────────────────────
 
def main():
    separator("WEATHER & CLIMATE ETL  →  POWER BI")
    t0 = time.time()
 
    raw    = extract()
    tables = transform(raw)
    summ   = load(tables)
    save_guide()
 
    elapsed = time.time() - t0
    separator("PIPELINE COMPLETE")
    print(Fore.GREEN + f"\n  ✅  ETL finished in {elapsed/60:.1f} min ({elapsed:.0f}s)")
    print(Fore.GREEN + f"  📁  Output : {os.path.abspath(OUTPUT_DIR)}")
    print(Fore.GREEN +  "  📊  Files ready for Power BI:\n")
    for s in summ:
        print(f"        {s['table']:<26} {s['rows']:>9,} rows   {s['size_mb']:>6.1f} MB")
    print()
    print(Fore.YELLOW + "  Next step:")
    print(Fore.YELLOW + "  1. Open Power BI Desktop")
    print(Fore.YELLOW + "  2. Get Data → Text/CSV → import all files above")
    print(Fore.YELLOW + "  3. Follow: weather_powerbi_output/POWERBI_SETUP_GUIDE.md\n")
 
 
if __name__ == "__main__":
    main()
