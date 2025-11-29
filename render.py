import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import matplotlib.dates as mdates

# --- FEATURE FLAG ---
# Set to True to sum all data points within the same day into a single daily total.
# Set to False to plot all data points at their original interval resolution.
MERGE_DATA_DAILY = True

# --- 1. DATA SETUP ---

df = pd.read_csv('/Users/powfamily/Dropbox/Oom & Wat/10-19 Life admin/12 Where I live & how I get around/12.21 Electricity, gas, & water/bchydro.com-consumption-XXXXXXXX2202-2025-11-26-020019.csv', skipinitialspace=True)

# --- 2. DATA CLEANING AND PREPARATION ---

# Convert the "Interval Start Date/Time" column to proper datetime objects
df['Interval Start Date/Time'] = pd.to_datetime(df['Interval Start Date/Time'], format='%Y-%m-%d %H:%M')

# Set the datetime column as the index for time-series plotting
df = df.set_index('Interval Start Date/Time')

# Ensure 'Inflow (kWh)' is numeric
df['Inflow (kWh)'] = pd.to_numeric(df['Inflow (kWh)'], errors='coerce')

# *** NEW LOGIC FOR CONDITIONAL DAILY AGGREGATION ***
if MERGE_DATA_DAILY:
    # 2a. Resample the data to daily frequency and sum the Inflow (kWh)
    # This aggregates all records within a 24hr period into one sum.
    df_aggregated = df['Inflow (kWh)'].resample('D').sum().to_frame()

    # Remove days where the sum is 0 (i.e., days without data) which might occur due to resampling
    df_aggregated = df_aggregated[df_aggregated['Inflow (kWh)'] > 0]

    # Use the aggregated data frame for further processing
    df = df_aggregated

# 2b. Extract the actual year for grouping (now from the aggregated index or original index)
df['Year'] = df.index.year

# 2c. Create a common "Day Index" (Month/Day/Time) by setting a fixed year (e.g., 2000)
# This aligns all data points on a single annual timeline for comparison.
def get_day_index(dt):
    """Sets a fixed year (2000) while preserving Month, Day, Hour, and Minute/00:00."""
    return dt.replace(year=2000, hour=0, minute=0, second=0, microsecond=0)

df['DayIndex'] = df.index.map(get_day_index)

# Group the DataFrame by the actual year
yearly_groups = df.groupby('Year')


# --- 3. PLOTTING ---

# Create the figure and axes
fig, ax = plt.subplots(figsize=(14, 7))

# 3.1. Plot each year as a separate line
for year, data in yearly_groups:
    # Determine the marker size and line style based on aggregation status
    marker_style = '.' if not MERGE_DATA_DAILY else 'o'
    line_width = 1.5 if not MERGE_DATA_DAILY else 2.5

    # Plot against the common 'DayIndex' for the X-axis
    ax.plot(data['DayIndex'], data['Inflow (kWh)'],
            label=f'Inflow {year} (kWh)',
            linewidth=line_width,
            marker=marker_style,
            markersize=5,
            alpha=0.8,
            zorder=3)

# --- 4. CUSTOMIZATION AND LABELS ---

# Update title based on aggregation status
title_suffix = " (Daily Total)" if MERGE_DATA_DAILY else " (Interval Data)"
ax.set_title(f'Annual Energy Inflow (kWh) Comparison{title_suffix}', fontsize=16, pad=20)
ax.set_xlabel('Day of Year (Jan 1 to Dec 31)', fontsize=12)
ax.set_ylabel('Inflow (kWh) Total' if MERGE_DATA_DAILY else 'Inflow (kWh) Interval', fontsize=12)

# Format X-axis to show dates nicely, based on the common DayIndex
# Use MonthLocator to render ticks only once a month
ax.xaxis.set_major_locator(mdates.MonthLocator())
# Display Month and Day (since the year is fixed to 2000, we don't display it)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

# Add grid lines for better readability
ax.grid(True, which='major', axis='x', linestyle=':', linewidth=1.0, alpha=0.6)
ax.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5, alpha=0.7)

# Rotate x-axis labels for better fit
plt.xticks(rotation=45, ha='right')

# Add legend and tight layout
ax.legend(loc='upper right', title="Year")
plt.tight_layout()

# Show the plot
plt.show()

print(f"Graph generated successfully. Data aggregation set to: {'Daily Sum' if MERGE_DATA_DAILY else 'Interval Data'}.")
