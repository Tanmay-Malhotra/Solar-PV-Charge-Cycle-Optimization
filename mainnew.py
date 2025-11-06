import time
import wt as main
import math
import serial
from datetime import datetime
from notify import send_telegram_message

from autonomic import update_weekly_avg, autonomic_plane

#openwt API key
api_key = "59fa7bff31936dcd5ba90343da033b98"

def get_weather_prediction(weather):
    weather_mapping = {
        "Clear": 1,  # Sunny
        "Clouds": 0,  # Cloudy
        "Rain": -1,  # Rainy
        "Drizzle": -1,
        "Thunderstorm": -1,
        "Snow": -1,
        "Mist": 0,
        "Fog": 0
    }
    return weather_mapping.get(weather, 0)

def bell_curve_efficiency(temp_c):
    """
    Bell curve model centered at 25°C.
    Efficiency reduces as temperature deviates from 25°C.
    """
    optimal_temp = 25
    sigma = 10   # spread of the curve
    efficiency = math.exp(-((temp_c - optimal_temp) ** 2) / (2 * sigma ** 2))
    return efficiency  # between 0 and 1


def get_tod_tariff(auto=True):
    """Determine or manually input Time-of-Day tariff."""
    if auto:
        current_hour = datetime.now().hour

        if 9 <= current_hour < 15:
            tariff_type = "Solar"
            code = 1
            cost_factor = 0.8  # 20% cheaper
        elif 18 <= current_hour < 22:
            tariff_type = "Peak"
            code = -1
            cost_factor = 1.2  # 20% more expensive
        else:
            tariff_type = "Normal"
            code = 0
            cost_factor = 1.0  # Base rate

        return tariff_type, code, cost_factor

    else:
        print("\nEnter Time-of-Day Tariff Type manually:")
        print("1 for Solar hours (cheaper)")
        print("0 for Normal hours")
        print("-1 for Peak hours (costlier)")
        code = int(input("Enter tariff type: "))

        if code == 1:
            tariff_type, cost_factor = "Solar", 0.8
        elif code == -1:
            tariff_type, cost_factor = "Peak", 1.2
        elif code == 0 :
            tariff_type, cost_factor = "Normal", 1.0
        else:
            print("Invalid code entered. Defaulting to Normal tariff.")
            tariff_type, cost_factor = "Normal", 1.0

        return tariff_type, code, cost_factor
    
def maincode():
    hardware_enabled = input("Enable inverter hardware communication? (y/n): ").lower() == 'y'
    inverter = None

    if hardware_enabled:
        try:
            inverter = serial.Serial('COM6', 9600, timeout=1)
            print("Connected to Inverter Power Management Unit (PMU)")
            time.sleep(2)
        except Exception as e:
            print(f"Error connecting to inverter: {e}")
            hardware_enabled = False

    print("Enter current inverter battery percentage:")
    battery_percentage = int(input("Battery %: "))

    """
    #Take tariff type as input from user
    print("Enter Current Time-of-Day Tariff Type:"
        "\n1 for Solar hours (cheaper)"
        "\n0 for Normal hours"
        "\n-1 for Peak hours (costlier)")

    tariff_code = int(input("Tariff type: "))

    """
    tod_choice = input("\nEnter 0 for Auto ToD detection or 1 for Manual entry: ")
    if tod_choice == '0':
            tariff_type, code, cost_factor = get_tod_tariff(auto=True)
    else:
        tariff_type, code, cost_factor = get_tod_tariff(auto=False)

    print(f"\nCurrent ToD Tariff: {tariff_type} hours (Code: {code}, Cost Factor: {cost_factor})")    


    if battery_percentage < 30:
        print("Battery critically low. Charging to 40% minimum to ensure sufficient backup.")
        #send command to arduino to charge battery to 40%
        battery_percentage = 40
        if hardware_enabled:
            inverter.write(b'1\n')
            print("Sent charging signal to PMU.")
        else:
            print("[Simulated] Charging signal sent to PMU.")

    if code == 1:
        #notify user via telegram to use heavy appliances as cheaper tarrif
        send_telegram_message("Solar Tariff Active: It's a great time to use heavy appliances and charge your devices at a lower cost!")
    elif code == -1:
        #notify user via telegram to avoid using heavy appliances as costlier tarrif
        send_telegram_message("Peak Tariff Active: Consider minimizing the use of heavy appliances to save on energy costs during this period.")
        
        #check battery percentage
        if battery_percentage > 50:
            print("Peak hours & sufficient battery → avoid grid charging, use stored energy.")
            action = "Discharge"
        else:
            print("Battery charge insufficient, using grid power despite peak tariff.")
    
    # At 11 pm in the night, assuming normal tariff, check tomorrow's solar forecast
    

    choice = input("\nEnter 0 to use weather API or 1 to enter conditions manually: ")

    try:
        if choice == '0':
            print("\nFetching next day's weather forecast...")
            weather, forecast_temp, efficiency = main.fetch_weather(api_key)
            print(f"Forecast: {weather}, Temp: {forecast_temp}°C, Efficiency: {efficiency:.2f}")

            weekly_avg = update_weekly_avg(forecast_temp)
            forecast_temp = autonomic_plane(forecast_temp, weekly_avg)

            ndw = get_weather_prediction(weather)
            solar_forecast = efficiency * (1.0 if ndw == 1 else 0.6 if ndw == 0 else 0.3)
            print(f"Combined Solar Forecast Score: {solar_forecast:.2f}")

        elif choice == '1':
            print("\nEnter weather condition: 1=Sunny, 0=Cloudy, -1=Rainy")
            ndw = int(input())
            forecast_temp = float(input("Enter forecast temperature (°C): "))

            weekly_avg = update_weekly_avg(forecast_temp)
            forecast_temp = autonomic_plane(forecast_temp, weekly_avg)
            efficiency = bell_curve_efficiency(forecast_temp)
            solar_forecast = efficiency * (1.0 if ndw == 1 else 0.6 if ndw == 0 else 0.3)
            print(f"Manual Solar Forecast Score: {solar_forecast:.2f}")
        else:
            print("Invalid choice.")
            return
        
        if solar_forecast > 0.75:
            print("High solar potential tomorrow — minimal grid charge needed.")
            #tanu: redundant but okay
            charge = 40
            action = "Minimal Charge"
            if hardware_enabled:
                inverter.write(b'0\n')
                print("Sent command to PMU.")

        elif 0.4 < solar_forecast <= 0.75:
            print("Moderate solar potential — charge partially for reliability.")
            charge = 60
            action = "Partial Charge"
            if hardware_enabled:
                inverter.write(b'1\n')
                print("Sent command to PMU.")
            else:
                print("[Simulated] PMU Command Sent.")
            
        else:
            print("Low solar potential — full charge required.")
            charge = 100
            action = "Full Charge"
            if hardware_enabled:
                inverter.write(b'1\n')
                print("Sent command to PMU.")
            else:
                print("[Simulated] PMU Command Sent.")

        print(f"\nDecision Summary → Action: {action}, Target Charge: {charge}%")
        #send notification to user via telegram about charging decision
        send_telegram_message(f"Charging Decision: {action} to {charge}% based on tomorrow's solar forecast score of {solar_forecast:.2f}.")


        
        

        # -------------------- PMU RESPONSE HANDLING --------------------
        if hardware_enabled:
            time.sleep(1)
            while inverter.in_waiting:
                pmu_response = inverter.readline().decode('utf-8').strip()
                print(f"PMU Response: {pmu_response}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        time.sleep(2)
        if inverter:
            inverter.close()
            print("inverter PMU connection closed.")


if __name__ == "__main__":
    maincode()