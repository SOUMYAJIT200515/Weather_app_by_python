# 🌦️ Weather, Health & Mood Station

A comprehensive, interactive Desktop GUI application built with Python that goes beyond basic weather reporting. It integrates real-time meteorological data with **Health Safety (AQI)**, **Smart Outfit Suggestions**, and a **Weather-Based Music Matcher** connected directly to Spotify.

![Weather App Interface](app_preview.png)

---

## 🌟 Key Features

* **📡 Real-Time Weather Data:** Fetches current temperature, humidity, wind speed, pressure, and visibility using the [OpenWeatherMap API](https://openweathermap.org/).
* **👕 Smart Outfit Planner:** Suggests ideal clothing layers based on current temperature, rain probability, and UV index.
* **🏥 Health & AQI Monitor:** Analyzes Air Quality Index (AQI) and PM2.5 levels to provide actionable health warnings (e.g., *"Wear a mask"*).
* **🎧 Weather-Based Music Matcher:** Dynamically detects the "vibe" of the current weather (e.g., *Rainy Night*, *Sunny Pop*) and generates a clickable link to a relevant Spotify search.
* **📈 Interactive Analytics:** Embedded Matplotlib graphs to visualize temperature trends, including 24-hour forecasts (interpolated) and 5-day outlooks.
* **📍 Flexible Geolocation:** Search manually by city name or use auto-location tracking.

---

## 🛠️ Tech Stack & Architecture

* **GUI Framework:** `tkinter` & `ttk` for a native, responsive desktop experience.
* **Data Visualization:** `matplotlib` (`backend_tkagg`) for live embedded charts.
* **Data Processing & Networking:** 
  * `requests`: Handles asynchronous API calls.
  * `numpy`: Used for data interpolation to create smooth hourly curves.
* **Core Utilities:** `datetime`, `random`, `webbrowser`.

---

## ⚙️ Prerequisites & Installation

Make sure you have **Python 3.x** installed on your system.

### 1. Clone the Repository
```bash
git clone [https://github.com/Spandan2106/Weather_app_by_python.git](https://github.com/Spandan2106/Weather_app_by_python.git)
cd Weather_app_by_python
```
### 2. Install Dependencies
Open your terminal or command prompt and install the required external libraries:

```Bash
pip install requests matplotlib numpy
```
(Note: ```tkinter, datetime, random,``` and ```webbrowser``` are built-in and included with standard Python installations.)

3. Configure Your OpenWeatherMap API Key
* Sign up for a free account on [OpenWeatherMap](https://openweathermap.org/).

* Navigate to your account dashboard and copy your API Key.

* Open ```weather_app.py``` and replace the placeholder on line 11 with your key:

```Python
API_KEY = "your_openweathermap_api_key_here"
```
# 🚀 How to Run
Launch the application by running the script from your terminal:

```Bash
python weather_app.py
```
Enter your target city name (e.g., London, Kolkata, Mumbai) into the GUI search bar and hit Enter or click Search.

# ⚠️ Troubleshooting
* Graph not showing? Ensure numpy and matplotlib are correctly installed.

* "Location not found" error? Verify your internet connection and check the spelling of the city name.

* 401 Unauthorized Error? Your API key may still be activating (OpenWeatherMap keys can take 10–20 minutes to become active after creation).

# 🔮 Future Roadmap
* [ ] Add scrollable 7-day weather forecast cards.

* [ ] Implement local configuration storage to remember default user cities.

* [ ] Integrate Spotify Web API for in-app playback control.

* [ ] Clean Light/Dark mode toggle interface.

# 🤝 Contributing
Contributions, issues, and feature requests are always welcome! Feel free to fork the repository and submit a pull request.

# 📜 License
This project is open-source and available under the MIT License.
