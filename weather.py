import tkinter as tk
from tkinter import ttk, messagebox
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import numpy as np
import random
import webbrowser  


# OpenWeatherMap API Key
API_KEY = "your_openweathermap_api_key_here"

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather, Health & Mood Station")
        self.root.geometry("1180x980")
        self.root.minsize(900, 760)
        self.root.configure(bg="#08111f")
        self.colors = {
            "bg": "#08111f",
            "panel": "#101d30",
            "panel_soft": "#14263d",
            "text": "#f4f8ff",
            "muted": "#91a4bc",
            "cyan": "#54d6ff",
            "blue": "#3578ff",
            "green": "#62e6b5",
        }
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Weather.TCombobox", fieldbackground="#14263d", background="#14263d",
                        foreground="#f4f8ff", bordercolor="#29425f", arrowcolor="#54d6ff")
        
        # Data storage
        self.current_city_data = None 
        self.current_temp_val = 0
        self.graph_temps = []
        self.graph_times = []
        self.current_playlist_url = "https://open.spotify.com/"

        self.scroll_canvas = tk.Canvas(root, bg=self.colors["bg"], highlightthickness=0)
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.content_frame = tk.Frame(self.scroll_canvas, bg=self.colors["bg"])
        self.content_window = self.scroll_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", self._update_scroll_region)
        self.scroll_canvas.bind("<Configure>", self._resize_scroll_content)
        self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # --- 1. TOP BAR ---
        self.top_frame = tk.Frame(self.content_frame, pady=15, bg=self.colors["bg"])
        self.top_frame.pack(fill="x", padx=34)

        self.hero_canvas = tk.Canvas(self.top_frame, height=150, highlightthickness=0,
                                     bg=self.colors["bg"])
        self.hero_canvas.pack(fill="x", pady=(0, 12))
        self.hero_canvas.create_text(24, 38, anchor="w", text="ATMOSPHERE",
                                     font=("Segoe UI", 11, "bold"), fill=self.colors["cyan"])
        self.hero_canvas.create_text(24, 78, anchor="w", text="Weather, health & mood",
                                     font=("Segoe UI", 30, "bold"), fill=self.colors["text"])
        self.hero_canvas.create_text(26, 113, anchor="w", text="A calmer way to read the sky.",
                                     font=("Segoe UI", 12), fill=self.colors["muted"])
        self.hero_particles = []
        for _ in range(18):
            x = random.randint(500, 1100)
            y = random.randint(18, 138)
            size = random.randint(2, 5)
            self.hero_particles.append([self.hero_canvas.create_oval(x, y, x + size, y + size,
                                                                       fill=self.colors["cyan"], outline=""),
                                        random.choice((-1, 1))])
        self._animate_hero()

        self.search_hint = tk.Label(self.top_frame, text="SEARCH A CITY", font=("Segoe UI", 9, "bold"),
                                    bg=self.colors["bg"], fg=self.colors["muted"])
        self.search_hint.pack(anchor="w", padx=4)
        
        self.city_entry = tk.Entry(self.top_frame, font=("Segoe UI", 14), width=24, bd=0,
                       relief="flat", bg="#14263d", fg=self.colors["text"],
                       insertbackground=self.colors["cyan"])
        self.city_entry.pack(side=tk.LEFT, padx=(4, 10), ipady=9)
        self.city_entry.bind('<Return>', lambda event: self.fetch_weather_by_city()) 
        
        self.search_btn = tk.Button(self.top_frame, text="🔍 Search", command=self.fetch_weather_by_city, 
                                    font=("Segoe UI", 11, "bold"), bg=self.colors["blue"], fg="white",
                                    padx=14, pady=8, relief="flat", cursor="hand2")
        self.search_btn.pack(side=tk.LEFT, padx=5)
        self._add_hover(self.search_btn, self.colors["blue"], "#5b93ff")

        self.loc_btn = tk.Button(self.top_frame, text="📍 My Location", command=self.fetch_weather_by_location, 
                                 font=("Segoe UI", 11, "bold"), bg="#1eaa82", fg="white",
                                 padx=14, pady=8, relief="flat", cursor="hand2")
        self.loc_btn.pack(side=tk.LEFT, padx=5)
        self._add_hover(self.loc_btn, "#1eaa82", "#39c99e")
        self.status_label = tk.Label(self.top_frame, text="● READY", font=("Segoe UI", 9, "bold"),
                                     bg=self.colors["bg"], fg=self.colors["green"])
        self.status_label.pack(side=tk.RIGHT, padx=8)

        # --- 2. MAIN DISPLAY ---
        self.info_frame = tk.Frame(self.content_frame, pady=5, bg=self.colors["bg"])
        self.info_frame.pack(fill="x")
        
        self.temp_label = tk.Label(self.info_frame, text="--°C", font=("Segoe UI", 60, "bold"), bg=self.colors["bg"], fg=self.colors["text"])
        self.temp_label.pack()
        
        self.feels_like_label = tk.Label(self.info_frame, text="Feels like --°C", font=("Segoe UI", 14), bg=self.colors["bg"], fg=self.colors["muted"])
        self.feels_like_label.pack(pady=(0, 10))
        
        self.desc_label = tk.Label(self.info_frame, text="Ready to scan", font=("Segoe UI", 16), bg=self.colors["bg"], fg=self.colors["cyan"])
        self.desc_label.pack()

        # --- 3. SMART ADVICE BOX (Outfit & Health) ---
        self.suggestion_frame = tk.Frame(self.content_frame, bg="#E3F2FD", pady=15, padx=20, highlightbackground="#2196F3", highlightthickness=1)
        self.suggestion_frame.pack(fill="x", padx=40, pady=10)
        
        self.outfit_label = tk.Label(self.suggestion_frame, text="👕 OUTFIT: Waiting for data...", 
                                     font=("Segoe UI", 11, "bold"), bg="#E3F2FD", fg="#1565C0", justify=tk.LEFT, wraplength=900)
        self.outfit_label.pack(anchor="w")
        
        self.health_label = tk.Label(self.suggestion_frame, text="🏥 HEALTH: Waiting for data...", 
                                     font=("Segoe UI", 11, "bold"), bg="#E3F2FD", fg="#D32F2F", justify=tk.LEFT, wraplength=900)
        self.health_label.pack(anchor="w", pady=(5,0))

        # --- 3.5 MUSIC MATCHING STATION (NEW ADDITION) ---
        self.music_frame = tk.Frame(self.content_frame, bg="#1DB954", pady=10, padx=20) # Spotify Green background
        self.music_frame.pack(fill="x", padx=40, pady=(0, 10))

        # Left side: Text info
        self.music_info_frame = tk.Frame(self.music_frame, bg="#1DB954")
        self.music_info_frame.pack(side=tk.LEFT, fill="both", expand=True)

        self.music_vibe_label = tk.Label(self.music_info_frame, text="🎧 MOOD MATCHER", font=("Segoe UI", 10, "bold"), bg="#1DB954", fg="white")
        self.music_vibe_label.pack(anchor="w")

        self.music_track_label = tk.Label(self.music_info_frame, text="Waiting for weather...", font=("Segoe UI", 14, "bold"), bg="#1DB954", fg="white")
        self.music_track_label.pack(anchor="w")

        # Right side: Play Button
        self.play_btn = tk.Button(self.music_frame, text="▶ PLAY ON SPOTIFY", command=self.open_spotify,
                                  font=("Segoe UI", 10, "bold"), bg="white", fg="#1DB954", padx=15, relief="flat", cursor="hand2")
        self.play_btn.pack(side=tk.RIGHT)


        # --- 4. DETAILS GRID (3 Rows) ---
        self.details_frame = tk.Frame(self.content_frame, bg="#F9F9F9", pady=15)
        self.details_frame.pack(fill="x", padx=40, pady=5)

        def create_detail_box(parent, label, default_val, row, col):
            f = tk.Frame(parent, bg="#F9F9F9", pady=5)
            f.grid(row=row, column=col, sticky="ew", padx=10)
            tk.Label(f, text=label, font=("Segoe UI", 9, "bold"), bg="#F9F9F9", fg="#888").pack()
            l_val = tk.Label(f, text=default_val, font=("Segoe UI", 14, "bold"), bg="#F9F9F9", fg="#333") 
            l_val.pack()
            parent.grid_columnconfigure(col, weight=1)
            return l_val

        # Row 1
        self.lbl_humidity = create_detail_box(self.details_frame, "HUMIDITY", "--%", 0, 0)
        self.lbl_wind = create_detail_box(self.details_frame, "WIND SPEED", "-- km/h", 0, 1)
        self.lbl_pressure = create_detail_box(self.details_frame, "PRESSURE", "-- hPa", 0, 2)
        self.lbl_visibility = create_detail_box(self.details_frame, "VISIBILITY", "-- km", 0, 3)

        # Row 2
        self.lbl_sunrise = create_detail_box(self.details_frame, "🌅 SUNRISE", "--:--", 1, 0)
        self.lbl_sunset = create_detail_box(self.details_frame, "🌇 SUNSET", "--:--", 1, 1)
        self.lbl_uv = create_detail_box(self.details_frame, "☀️ UV INDEX", "--", 1, 2)
        self.lbl_cloud = create_detail_box(self.details_frame, "☁️ CLOUDS", "--%", 1, 3)

        # Row 3
        self.lbl_rain = create_detail_box(self.details_frame, "☔ RAIN PROB", "--%", 2, 0)
        self.lbl_aqi_num = create_detail_box(self.details_frame, "🍃 AQI SCORE", "--", 2, 1)
        self.lbl_pm25 = create_detail_box(self.details_frame, "🌫️ PM2.5", "--", 2, 2)
        self.lbl_pm10 = create_detail_box(self.details_frame, "🌫️ PM10", "--", 2, 3)

        # --- 5. GRAPH AREA ---
        self.options_frame = tk.Frame(self.content_frame, bg=self.colors["bg"], pady=5)
        self.options_frame.pack(fill="x", padx=40)
        
        self.view_mode = tk.StringVar()
        self.view_combo = ttk.Combobox(self.options_frame, textvariable=self.view_mode, font=("Segoe UI", 11), state="readonly", width=22, style="Weather.TCombobox")
        self.view_combo['values'] = ("Next 24 Hours", "Next 5 Days", "Previous 24 Hours (Sim)", "Last Month Avg (Sim)")
        self.view_combo.current(0)
        self.view_combo.pack(side=tk.RIGHT, padx=10)
        tk.Label(self.options_frame, text="GRAPH VIEW", font=("Segoe UI", 10, "bold"), bg=self.colors["bg"], fg=self.colors["muted"]).pack(side=tk.RIGHT)

        self.graph_frame = tk.Frame(self.content_frame, bg=self.colors["bg"])
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        self.fig, self.ax = plt.subplots(figsize=(8, 3.0), dpi=100)
        self.fig.patch.set_facecolor('white') 
        self.annot = self.ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points", bbox=dict(boxstyle="round", fc="#333", ec="none"), color="white")
        self.annot.set_visible(False)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.view_combo.bind("<<ComboboxSelected>>", self.update_graph_view)

    def _update_scroll_region(self, event=None):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _resize_scroll_content(self, event):
        self.scroll_canvas.itemconfigure(self.content_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.delta:
            self.scroll_canvas.yview_scroll(int(-event.delta / 120), "units")
        elif event.num == 4:
            self.scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.scroll_canvas.yview_scroll(1, "units")

    def _add_hover(self, button, normal_color, active_color):
        button.bind("<Enter>", lambda event: button.config(bg=active_color))
        button.bind("<Leave>", lambda event: button.config(bg=normal_color))

    def _animate_hero(self):
        for particle_data in self.hero_particles:
            particle, direction = particle_data
            coords = self.hero_canvas.coords(particle)
            if not coords:
                continue
            next_x = coords[0] + direction * 0.35
            if next_x > 1160 or next_x < 460:
                direction *= -1
                particle_data[1] = direction
            self.hero_canvas.move(particle, direction * 0.35, 0)
        self.root.after(45, self._animate_hero)

    # --- LOGIC ---

    def calculate_music_mood(self, weather_id, temp, cloud_cover, is_day):
        """
        Determines the mood based on weather parameters.
        Returns: (Mood Text, Spotify Search Query)
        """
        # 1. Rain / Drizzle / Thunderstorm (IDs 200-531)
        if 200 <= weather_id <= 531:
            if not is_day:
                return "🌧️ Rainy Night Vibe", "lofi beats rain"
            return "☔ Rainy Day Blues", "acoustic pop"

        # 2. Snow (IDs 600-622)
        if 600 <= weather_id <= 622:
            return "❄️ Snowy & Cozy", "classical study"

        # 3. Atmosphere (Fog/Mist) (IDs 701-781)
        if 701 <= weather_id <= 781:
            return "🌫️ Foggy Mystery", "ambient electronic"

        # 4. Clear Sky (800)
        if weather_id == 800:
            if is_day:
                if temp > 28: return "☀️ Hot Summer Hype", "summer hits 2024"
                return "☀️ Sunny & Happy", "upbeat pop"
            else:
                return "🌙 Clear Night", "deep house chill"

        # 5. Clouds (801-804)
        if 801 <= weather_id <= 804:
            if cloud_cover > 80:
                return "☁️ Overcast & Chill", "indie folk"
            return "🌥️ Partly Cloudy", "soft rock"

        # Fallback
        return "🎵 Weather Mix", "top hits"

    def open_spotify(self):
        webbrowser.open(self.current_playlist_url)

    def generate_advice(self, temp, weather_id, rain_prob, aqi_val, uv_val, cloud_cover, is_day):
        # 1. OUTFIT LOGIC
        outfit = ""
        if temp < 10: outfit = "🥶 Freeze Alert! Heavy coat, scarf, and gloves required."
        elif 10 <= temp < 18: outfit = "🧥 Chilly. Hoodie or light jacket recommended."
        elif 18 <= temp < 25: outfit = "👕 Pleasant. T-shirt and jeans are perfect."
        elif 25 <= temp < 30: outfit = "😎 Warm. Short sleeves, light fabrics."
        else: outfit = "🔥 Hot! Shorts, tank top, stay cool."

        if (200 <= weather_id <= 599) or rain_prob > 40: outfit += " | ☔ Take an Umbrella!"
        if uv_val > 6: outfit += " | 🧢 Wear a hat & sunglasses."

        self.outfit_label.config(text=f"👕 OUTFIT: {outfit}")

        # 2. HEALTH & COLOR LOGIC
        health = ""
        col_good, col_mod, col_sens, col_bad, col_haz = "#00C853", "#FFD600", "#FF6D00", "#D50000", "#4A148C"
        selected_color = "#333333"

        if aqi_val <= 50:
            health = "✅ Air is clean. Enjoy outdoors!"
            self.suggestion_frame.config(bg="#E8F5E9", highlightbackground=col_good)
            self.health_label.config(fg="#1B5E20", bg="#E8F5E9")
            self.outfit_label.config(bg="#E8F5E9")
            selected_color = col_good
        elif 51 <= aqi_val <= 100:
            health = "⚠️ Moderate. Sensitive people limit exertion."
            self.suggestion_frame.config(bg="#FFFDE7", highlightbackground=col_mod)
            self.health_label.config(fg="#F57F17", bg="#FFFDE7")
            self.outfit_label.config(bg="#FFFDE7")
            selected_color = col_mod
        elif 101 <= aqi_val <= 150:
            health = "😷 Unhealthy for Sensitive Groups."
            self.suggestion_frame.config(bg="#FFF3E0", highlightbackground=col_sens)
            self.health_label.config(fg="#E65100", bg="#FFF3E0")
            self.outfit_label.config(bg="#FFF3E0")
            selected_color = col_sens
        elif 151 <= aqi_val <= 200:
            health = "⛔ Unhealthy! Wear a mask outside."
            self.suggestion_frame.config(bg="#FFEBEE", highlightbackground=col_bad)
            self.health_label.config(fg="#B71C1C", bg="#FFEBEE")
            self.outfit_label.config(bg="#FFEBEE")
            selected_color = col_bad
        else:
            health = "☠️ HAZARDOUS! STAY INDOORS."
            self.suggestion_frame.config(bg="#F3E5F5", highlightbackground=col_haz)
            self.health_label.config(fg="#4A148C", bg="#F3E5F5")
            self.outfit_label.config(bg="#F3E5F5")
            selected_color = col_haz

        self.health_label.config(text=f"🏥 HEALTH: {health}")
        self.lbl_aqi_num.config(fg=selected_color)

        # 3. UPDATE MUSIC STATION
        mood_text, search_query = self.calculate_music_mood(weather_id, temp, cloud_cover, is_day)
        self.music_track_label.config(text=f"{mood_text}: {search_query.title()}")
        # Create a direct Spotify search link (opens web player)
        self.current_playlist_url = f"https://open.spotify.com/search/{search_query.replace(' ', '%20')}/playlists"


    def estimate_uv(self, cloud_cover, hour):
        if hour < 7 or hour > 17: return 0 
        base_uv = 0
        if 10 <= hour <= 14: base_uv = 8
        elif 9 <= hour < 10 or 14 < hour <= 16: base_uv = 5
        else: base_uv = 2
        
        if cloud_cover < 20: factor = 1.0
        elif cloud_cover < 50: factor = 0.8
        elif cloud_cover < 80: factor = 0.5
        else: factor = 0.3
        return round(base_uv * factor, 1)

    def fetch_weather_by_city(self):
        city = self.city_entry.get()
        if city: self.get_weather_data(city=city)

    def fetch_weather_by_location(self):
        try:
            ip_data = requests.get("https://ipinfo.io/json").json()
            lat, lon = ip_data["loc"].split(",")
            self.get_weather_data(lat=lat, lon=lon)
        except:
            messagebox.showerror("Error", "Location not found.")

    def get_weather_data(self, city=None, lat=None, lon=None):
        try:
            base = "https://api.openweathermap.org/data/2.5/"
            if city:
                url_curr = f"{base}weather?q={city}&appid={API_KEY}&units=metric"
                url_fore = f"{base}forecast?q={city}&appid={API_KEY}&units=metric"
            else:
                url_curr = f"{base}weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
                url_fore = f"{base}forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

            curr = requests.get(url_curr).json()
            if curr.get("cod") != 200: raise Exception("Not Found")
            self.current_city_data = requests.get(url_fore).json()
            
            lat, lon = curr["coord"]["lat"], curr["coord"]["lon"]
            url_aqi = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
            aqi_data = requests.get(url_aqi).json()
            pm25 = aqi_data["list"][0]["components"]["pm2_5"]
            pm10 = aqi_data["list"][0]["components"]["pm10"]
            aqi_val = self.calculate_aqi(pm25)

            temp = curr['main']['temp']
            weather_id = curr['weather'][0]['id']
            rain_prob = int(self.current_city_data['list'][0]['pop'] * 100)
            cloud_cover = curr['clouds']['all']
            
            # Determine Day/Night based on current time vs sunrise/sunset
            now_ts = datetime.now().timestamp()
            sunrise_ts = curr['sys']['sunrise']
            sunset_ts = curr['sys']['sunset']
            is_day = sunrise_ts <= now_ts <= sunset_ts

            uv_val = self.estimate_uv(cloud_cover, datetime.now().hour)

            self.temp_label.config(text=f"{temp:.1f}°C")
            self.feels_like_label.config(text=f"Feels like {curr['main']['feels_like']:.1f}°C")
            self.desc_label.config(text=f"{curr['weather'][0]['description'].title()} in {curr['name']}")

            self.lbl_humidity.config(text=f"{curr['main']['humidity']}%")
            self.lbl_wind.config(text=f"{curr['wind']['speed']} km/h")
            self.lbl_pressure.config(text=f"{curr['main']['pressure']} hPa")
            self.lbl_visibility.config(text=f"{curr.get('visibility', 0)/1000:.1f} km")
            self.lbl_sunrise.config(text=datetime.fromtimestamp(sunrise_ts).strftime("%I:%M %p"))
            self.lbl_sunset.config(text=datetime.fromtimestamp(sunset_ts).strftime("%I:%M %p"))
            self.lbl_uv.config(text=f"{uv_val}")
            self.lbl_cloud.config(text=f"{cloud_cover}%")
            self.lbl_rain.config(text=f"{rain_prob}%")
            self.lbl_aqi_num.config(text=f"{aqi_val}")
            self.lbl_pm25.config(text=f"{pm25}")
            self.lbl_pm10.config(text=f"{pm10}")

            # Run Logic (Added is_day and cloud_cover to args)
            self.generate_advice(temp, weather_id, rain_prob, aqi_val, uv_val, cloud_cover, is_day)
            self.update_graph_view()

        except Exception as e:
            # print(e) # Debugging
            messagebox.showerror("Error", str(e))

    def calculate_aqi(self, pm25):
        if pm25 <= 12: return int((50/12)*pm25)
        elif pm25 <= 35.4: return int(51 + (49/23.3)*(pm25-12.1))
        return int(101 + (pm25-35.5))

    # --- GRAPH LOGIC ---
    def update_graph_view(self, event=None):
        if not self.current_city_data: return
        mode = self.view_mode.get()
        if "Next 24 Hours" in mode: self.generate_next_24h()
        elif "Next 5 Days" in mode: self.generate_next_5_days()
        elif "Previous 24 Hours" in mode: self.generate_past_24h_sim()
        elif "Last Month" in mode: self.generate_monthly_avg_sim()
        self.plot_graph(mode)

    def generate_next_24h(self):
        raw_temps, raw_times = [], []
        for item in self.current_city_data["list"][:6]:
            raw_temps.append(item["main"]["temp"])
            raw_times.append(item["dt"])
        new_times = np.arange(raw_times[0], raw_times[-1], 3600)
        self.graph_temps = np.interp(new_times, raw_times, raw_temps)
        self.graph_times = [datetime.fromtimestamp(t).strftime("%I %p") for t in new_times]

    def generate_next_5_days(self):
        temp_map = {}
        for item in self.current_city_data["list"]:
            date = item["dt_txt"].split(" ")[0]
            if date not in temp_map: temp_map[date] = []
            temp_map[date].append(item["main"]["temp"])
        self.graph_temps = [sum(v)/len(v) for v in temp_map.values()][:5]
        self.graph_times = [datetime.strptime(k, "%Y-%m-%d").strftime("%a %d") for k in temp_map.keys()][:5]

    def generate_past_24h_sim(self):
        base = float(self.temp_label.cget("text").replace("°C",""))
        self.graph_times, self.graph_temps = [], []
        curr_h = datetime.now().hour
        for i in range(24, 0, -1):
            h = (curr_h - i) % 24
            var = random.uniform(0,3) if 6<=h<=18 else random.uniform(-4,-1)
            self.graph_temps.append(base+var)
            self.graph_times.append(f"{h}:00")

    def generate_monthly_avg_sim(self):
        base = float(self.temp_label.cget("text").replace("°C",""))
        self.graph_temps = [base+random.uniform(-3,3) for _ in range(4)]
        self.graph_times = ["Week 1", "Week 2", "Week 3", "Last Week"]

    def plot_graph(self, title):
        self.ax.clear()
        x = np.arange(len(self.graph_temps))
        self.ax.set_facecolor('#101d30')
        self.fig.patch.set_facecolor('#08111f')
        self.ax.plot(x, self.graph_temps, color='#54d6ff', linewidth=2.5, marker='o', markersize=5, markerfacecolor='#101d30')
        self.ax.fill_between(x, self.graph_temps, min(self.graph_temps)-5, color='#54d6ff', alpha=0.12)
        self.ax.set_title(title, fontsize=10, fontweight='bold', color="#f4f8ff")
        step = 3 if len(x) > 12 else 1
        self.ax.set_xticks(x[::step])
        self.ax.set_xticklabels(self.graph_times[::step], color='#91a4bc')
        self.ax.tick_params(axis='y', colors='#91a4bc')
        self.ax.grid(True, linestyle=':', alpha=0.25, color='#91a4bc')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#29425f')
        self.ax.spines['bottom'].set_color('#29425f')
        self.canvas.draw()

    def on_hover(self, event):
        if event.inaxes == self.ax and len(self.graph_temps) > 0:
            x_idx = int(round(event.xdata))
            if 0 <= x_idx < len(self.graph_temps):
                self.annot.xy = (x_idx, self.graph_temps[x_idx])
                self.annot.set_text(f"{self.graph_times[x_idx]}\n{self.graph_temps[x_idx]:.1f}°C")
                self.annot.set_visible(True)
                self.canvas.draw_idle()
                return
        if self.annot.get_visible():
            self.annot.set_visible(False)
            self.canvas.draw_idle()

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()