import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from datetime import timedelta
import matplotlib.ticker as ticker

# --- 1. DATA SETUP ---
df_list = [pd.read_csv(file) for file in glob('/Users/powfamily/Dropbox/Oom & Wat/10-19 Life admin/12 Where I live & how I get around/12.21 Electricity, gas, & water/bchydro.com-consumption-XXXXXXXX2202-*.csv')]
df = pd.concat(df_list, ignore_index=True).drop_duplicates()

# --- 2. DATA CLEANING AND PREPARATION ---
df['Interval Start Date/Time'] = pd.to_datetime(df['Interval Start Date/Time'], format='%Y-%m-%d %H:%M')
df = df.set_index('Interval Start Date/Time').sort_index()
df['Inflow (kWh)'] = pd.to_numeric(df['Inflow (kWh)'], errors='coerce')

df = df['Inflow (kWh)'].resample('D').sum().to_frame()
df = df[df['Inflow (kWh)'] > 0]

df['Year'] = df.index.year

# --- 3. PLOTTING ---
fig, ax = plt.subplots(figsize=(16, 8))
years = sorted(df['Year'].unique())
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

for i, year in enumerate(years):
    year_data = df[df['Year'] == year].copy()
    if year_data.empty:
        continue

    # Sunday Alignment
    first_day = pd.Timestamp(year=year, month=1, day=1)
    days_to_subtract = (first_day.weekday() + 1) % 7
    start_date = first_day - timedelta(days=days_to_subtract)

    padded_data = df[(df.index >= start_date) & (df.index < first_day)].copy()

    year_data['RelDay'] = (year_data.index - start_date).days
    padded_data['RelDay'] = (padded_data.index - start_date).days

    color = colors[i % len(colors)]

    if not padded_data.empty:
        ax.plot(padded_data['RelDay'], padded_data['Inflow (kWh)'],
                color=color, linestyle=':', alpha=0.4, linewidth=2)

    ax.plot(year_data['RelDay'], year_data['Inflow (kWh)'],
            label=f'Year {year}', color=color, linestyle='-',
            marker='o', markersize=4, zorder=3)

# --- 4. WEEKEND BANDS AND CUSTOMIZATION ---

# Highlight Weekends (Day 0=Sun, Day 6=Sat)
for day in range(0, 378):
    if day % 7 == 0 or day % 7 == 6:
        ax.axvspan(day - 0.5, day + 0.5, color='gray', alpha=0.08, zorder=1)

# --- FIXED X-AXIS LOGIC ---
# Define exactly 14 positions (every 28 days up to day 336, plus a final one at 364)
tick_positions = [i * 28 for i in range(14)]
tick_labels = ["W1", "W5", "W9", "W13", "W17", "W21", "W25", "W29", "W33", "W37", "W41", "W45", "W49", "W53"]

ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels)

# Minor ticks for every week to show the weekly grid
ax.xaxis.set_minor_locator(ticker.MultipleLocator(7))

ax.set_title('Electricity Usage: Weekday Aligned (Sunday Start)', fontsize=16)
ax.set_xlabel('4-Week Periods', fontsize=12)
ax.set_ylabel('Inflow (kWh)', fontsize=12)

ax.grid(True, which='minor', axis='x', linestyle=':', alpha=0.3)
ax.grid(True, which='major', axis='y', linestyle='--', alpha=0.5)
ax.legend(title="Year", loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
plt.show()
