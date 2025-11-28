import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import matplotlib.dates as mdates

# --- 1. MOCK DATA SETUP ---
# NOTE: The mock data has been expanded to span multiple months and years (2024 and 2025)
# to better demonstrate the annual comparison feature.
# Remember to replace this section with pd.read_csv('your_file_name.csv') once you have your actual file.

with open('/Users/powfamily/Dropbox/Oom & Wat/10-19 Life admin/12 Where I live & how I get around/12.21 Electricity, gas, & water/bchydro.com-consumption-XXXXXXXX2202-2025-11-26-020019.csv', 'r') as f:
    csv_data = f.read()

# Simulate reading the CSV data
df = pd.read_csv(StringIO(csv_data), skipinitialspace=True)

# --- 2. DATA CLEANING AND PREPARATION ---

# Convert the "Interval Start Date/Time" column to proper datetime objects
df['Interval Start Date/Time'] = pd.to_datetime(df['Interval Start Date/Time'], format='%Y-%m-%d %H:%M')

# Set the datetime column as the index for time-series plotting
df = df.set_index('Interval Start Date/Time')

# Ensure 'Inflow (kWh)' is numeric
df['Inflow (kWh)'] = pd.to_numeric(df['Inflow (kWh)'], errors='coerce')

# *** NEW LOGIC FOR MULTI-YEAR COMPARISON ***

# 2a. Extract the actual year for grouping
df['Year'] = df.index.year

# 2b. Create a common "Day Index" (Month/Day/Time) by setting a fixed year (e.g., 2000)
# This aligns all data points on a single annual timeline for comparison.
def get_day_index(dt):
    """Sets a fixed year (2000) while preserving Month, Day, Hour, and Minute."""
    return dt.replace(year=2000)

df['DayIndex'] = df.index.map(get_day_index)

# Group the DataFrame by the actual year
yearly_groups = df.groupby('Year')


# --- 3. PLOTTING ---

# Create the figure and axes
fig, ax = plt.subplots(figsize=(14, 7))

# 3.1. Plot each year as a separate line
for year, data in yearly_groups:
    # Plot against the common 'DayIndex' for the X-axis
    ax.plot(data['DayIndex'], data['Inflow (kWh)'],
            label=f'Inflow {year} (kWh)',
            linewidth=1.5,
            marker='o',
            markersize=3,
            alpha=0.8,
            zorder=3)

# --- 4. CUSTOMIZATION AND LABELS ---

# Set title and labels
ax.set_title('Annual Energy Inflow (kWh) Comparison', fontsize=16, pad=20)
ax.set_xlabel('Day of Year (Jan 1 to Dec 31)', fontsize=12)
ax.set_ylabel('Inflow (kWh)', fontsize=12)

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

print("Multi-year comparison graph generated successfully. Check the pop-up window for the visualization.")
