import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
import matplotlib.dates as mdates
from datetime import timedelta

# --- 1. DATA SETUP ---
df_list = [pd.read_csv(file) for file in glob('/Users/powfamily/Dropbox/Oom & Wat/10-19 Life admin/12 Where I live & how I get around/12.21 Electricity, gas, & water/bchydro.com-consumption-XXXXXXXX2202-*.csv')]
df = pd.concat(df_list, ignore_index=True).drop_duplicates()

# --- 2. DATA CLEANING AND PREPARATION ---
df['Interval Start Date/Time'] = pd.to_datetime(df['Interval Start Date/Time'], format='%Y-%m-%d %H:%M')
df = df.set_index('Interval Start Date/Time').sort_index()
df['Inflow (kWh)'] = pd.to_numeric(df['Inflow (kWh)'], errors='coerce')

df = df['Inflow (kWh)'].resample('D').sum().to_frame()
df = df[df['Inflow (kWh)'] > 0]

# Extract Year for grouping
df['Year'] = df.index.year

# --- 3. PLOTTING ---
fig, ax = plt.subplots(figsize=(16, 8))

years = sorted(df['Year'].unique())

# Get the color list from the public API
prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

for i, year in enumerate(years):
    # 1. Get data for the current year
    year_data = df[df['Year'] == year].copy()
    if year_data.empty:
        continue

    # 2. Find the first Sunday on or before Jan 1st of this year
    first_day = pd.Timestamp(year=year, month=1, day=1)
    # weekday() returns 0 for Monday, 6 for Sunday.
    # To get to the previous Sunday: (day.weekday() + 1) % 7
    days_to_subtract = (first_day.weekday() + 1) % 7
    start_date = first_day - timedelta(days=days_to_subtract)

    # 3. Get the "Padded" data (from the previous year's end)
    padded_data = df[(df.index >= start_date) & (df.index < first_day)].copy()

    # 4. Create a "Relative Day" index (0 = first Sunday, 1 = Monday...)
    # This aligns every year so they all start on 'Day 0' (Sunday)
    year_data['RelDay'] = (year_data.index - start_date).days
    padded_data['RelDay'] = (padded_data.index - start_date).days

    # Select color using the loop index
    color = colors[i % len(colors)]

    # Plot Padded Data (Dotted)
    if not padded_data.empty:
        ax.plot(padded_data['RelDay'], padded_data['Inflow (kWh)'],
                color=color, linestyle=':', alpha=0.5, linewidth=2)

    # Plot Actual Year Data (Solid)
    ax.plot(year_data['RelDay'], year_data['Inflow (kWh)'],
            label=f'Year {year}', color=color, linestyle='-',
            marker='o', markersize=4)

# --- 4. CUSTOMIZATION ---

# Custom x-axis: Instead of dates, we show "Week Numbers" or "Days"
# Since 365 days / 7 = ~52 weeks, we can mark every 7 days (Sundays)
ax.set_xticks([i for i in range(0, 372, 7)])
ax.set_xticklabels([f"Wk {i//7 + 1}" for i in range(0, 372, 7)])

ax.set_title(f'Energy Inflow: Week-Aligned Comparison (Starting Sunday)', fontsize=16)
ax.set_xlabel('Week of Year (Aligned to Sunday)', fontsize=12)
ax.set_ylabel('Inflow (kWh)', fontsize=12)
ax.grid(True, which='both', linestyle='--', alpha=0.5)
ax.legend(title="Year", bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()
