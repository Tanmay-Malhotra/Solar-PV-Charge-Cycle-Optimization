# Array to store 7 days of temperature
weekly_temps = []
MAX_DAYS = 7

def update_weekly_avg(current_temp):
    global weekly_temps

    if len(weekly_temps) < MAX_DAYS:
        weekly_temps.append(current_temp)
    else:
        weekly_temps.pop(0)
        weekly_temps.append(current_temp)

    # Calculate average temperature for environmental adaptation
    weekly_avg = sum(weekly_temps) / len(weekly_temps)
    return weekly_avg

def autonomic_plane(current_temp, weekly_avg):
    # If deviation > ±10, impute with weekly average
    if abs(current_temp - weekly_avg) > 10:
        print(f"Temperature deviation detected. Imputing {current_temp} with weekly average {weekly_avg}.")
        current_temp = weekly_avg
    return current_temp


if __name__ == "__main__":
    # Predefined temperature array for 7 days (example)
    predefined_temps = [28, 30, 31, 29, 32, 33, 30]

    print("Initial weekly temperature data:")
    for temp in predefined_temps:
        weekly_avg = update_weekly_avg(temp)
    print(f"Weekly average after initialization: {weekly_avg:.2f}°C\n")

    # New temperature readings for testing autonomic adaptation
    test_readings = [34, 20, 45, 31]

    print("Testing new temperature readings:")
    for current_temp in test_readings:
        weekly_avg = update_weekly_avg(current_temp)
        adapted_temp = autonomic_plane(current_temp, weekly_avg)
        print(f"Current: {current_temp}°C → Adapted: {adapted_temp:.2f}°C | New Weekly Avg: {weekly_avg:.2f}°C\n")