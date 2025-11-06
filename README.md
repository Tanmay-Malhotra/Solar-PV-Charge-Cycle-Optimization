# Solar-PV-Charge-Cycle-Optimization

## How to Use

### Step 1: Configure the Environment
1. Ensure Python 3.8 or later is installed on your system.  
2. Install the required dependencies using:
   ```bash
   pip install -r requirements.txt
   ```
   If `requirements.txt` is not available, manually install:
   ```bash
   pip install pyserial requests python-telegram-bot datetime
   ```

### Step 2: Add API Keys
1. Open `main.py` and set your OpenWeather API key:
   ```python
   api_key = "YOUR_OPENWEATHER_API_KEY"
   ```
2. Open `notify.py` and add your Telegram credentials:
   ```python
   TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
   CHAT_ID = "YOUR_CHAT_ID"
   ```

### Step 3: Connect Hardware
1. Connect **Arduino UNO** (or **NodeMCU**) to your computer using a USB cable.  
2. Attach the **relay module** and **capacitor circuit** as per your hardware setup.  
3. Update the correct serial port in `main.py` (for example, `'COM6'`):
   ```python
   inverter = serial.Serial('COM6', 9600, timeout=1)
   ```

### Step 4: Run the Program
Execute the main script:
```bash
python main.py
```

### Step 5: Follow On-Screen Prompts
During execution, the program will:
1. Ask whether to enable inverter hardware communication (`y/n`).  
2. Request the current battery percentage.  
3. Ask for Time-of-Day (ToD) tariff mode:
   - Auto detection mode (`0`)  
   - Manual entry mode (`1`)  
4. Ask for weather input:
   - API-based (`0`)  
   - Manual entry (`1`)

### Step 6: System Actions
Based on the inputs and forecasts, the system will:
1. Determine whether to charge, partially charge, or discharge the battery.  
2. Send control commands to the connected Arduino or NodeMCU.  
3. Display the decision summary in the terminal.  
4. Send status notifications to the user via Telegram.

### Step 7: Stop the Program
Press `Ctrl + C` in the terminal to safely terminate execution.  
If using Arduino, wait for the “PMU connection closed” message before disconnecting the device.

---

### Additional Notes
- Ensure a stable internet connection for weather data retrieval and Telegram communication.  
- If using NodeMCU instead of Arduino, the system can operate independently without a laptop by fetching weather data and sending alerts directly over Wi-Fi.  
- For future versions, the dashboard can be hosted on the cloud for remote monitoring and control.  
