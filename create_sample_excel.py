import pandas as pd
import os

# Create sample Excel file for testing
data = {
    'Roll Number': ['101', '102', '103', '104', '105'],
    'Name': ['আব্দুল করিম', 'ফাতেমা খাতুন', 'রহিম উদ্দিন', 'সালমা আক্তার', 'কামাল হোসেন'],
    'Bengali': [85, 78, 92, 88, 76],
    'English': [78, 82, 85, 79, 81],
    'Math': [92, 88, 95, 90, 85],
    'Physics': [88, 85, 90, 87, 82],
    'Chemistry': [90, 87, 92, 89, 84],
    'Biology': [87, 90, 88, 92, 86],
    'Total': [520, 510, 542, 525, 494],
    'Percentage': [86.67, 85.00, 90.33, 87.50, 82.33],
    'Grade': ['A+', 'A+', 'A+', 'A+', 'A']
}

df = pd.DataFrame(data)

# Create uploads directory if it doesn't exist
os.makedirs('static/uploads/results', exist_ok=True)

# Save to Excel
df.to_excel('sample_result.xlsx', index=False)
print("Sample Excel file created: sample_result.xlsx")
print("\nColumns:", list(df.columns))
print("\nFirst few rows:")
print(df.head())
