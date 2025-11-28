import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import numpy as np

# --- 1. MOCK DATA SETUP ---
# Replace this section with pd.read_csv('your_file_name.csv') once you have the file.
# This mock data is just to make the script runnable.
# It simulates data spanning 8 days (Jan 1st to Jan 8th) including a weekend.

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


# --- 3. IDENTIFY WEEKENDS FOR HIGHLIGHTING ---

# Identify weekend days (Saturday=5, Sunday=6)
# dt.dayofweek returns 0 for Monday and 6 for Sunday
weekend_dates = df[df.index.dayofweek.isin([5, 6])].index.normalize().unique()

# --- 4. PLOTTING ---

# Create the figure and axes
fig, ax = plt.subplots(figsize=(14, 7))

# 4.1. Highlight Weekends (Shaded Columns)
for date in weekend_dates:
    # Calculate the start and end of the day for the shading
    start_of_day = date
    # We add 1 day to the date to get the end boundary of the shading
    end_of_day = date + pd.Timedelta(days=1)

    # Use axvspan to draw a vertical span (column) over the weekend period
    ax.axvspan(start_of_day, end_of_day,
               facecolor='#F0F8FF',  # Light Blue/Alice Blue color
               alpha=0.5,            # Transparency
               zorder=0,             # Ensure it stays behind the line plot
               label='Weekend' if date == weekend_dates.min() else "") # Label only the first one

# 4.2. Plot the Line Graph
ax.plot(df.index, df['Inflow (kWh)'],
        label='Inflow (kWh)',
        color='#1f77b4', # Muted blue
        linewidth=1.5,
        marker='.',
        markersize=3,
        zorder=3)

# --- 5. CUSTOMIZATION AND LABELS ---

# Set title and labels
ax.set_title('Energy Inflow (kWh) Over Time with Weekend Highlights', fontsize=16, pad=20)
ax.set_xlabel('Interval Start Date/Time', fontsize=12)
ax.set_ylabel('Inflow (kWh)', fontsize=12)

# Format X-axis to show dates nicely
# Use date formatters and locators for cleaner display
import matplotlib.dates as mdates
ax.xaxis.set_major_locator(mdates.DayLocator(interval=1)) # Show tick every day
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%a')) # Display Date and Day of Week

# Add grid lines for better readability
ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

# Rotate x-axis labels for better fit
plt.xticks(rotation=45, ha='right')

# Add legend and tight layout
ax.legend(loc='upper right')
plt.tight_layout()

# Show the plot
plt.show()

print("Graph generated successfully. Check the pop-up window for the visualization.")
