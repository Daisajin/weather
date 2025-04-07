import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import requests
import os
import sys
from dotenv import load_dotenv
import json
from PIL import Image
import urllib.parse
import threading
import time
import traceback

# Загрузка переменных окружения
load_dotenv()

class WeatherWidget(ctk.CTk):
    def __init__(self):
        try:
            super().__init__()
            
            # Настройка окна
            self.title("Погода")
            self.geometry("300x400")
            self.attributes('-topmost', True)  # Окно всегда поверх других
            self.overrideredirect(True)  # Убираем стандартную рамку окна
            
            # API конфигурация
            self.api_key = os.getenv("OPENWEATHER_API_KEY")
            if not self.api_key or self.api_key == "your_api_key_here":
                messagebox.showerror("Ошибка", "Пожалуйста, установите правильный OPENWEATHER_API_KEY в файле .env")
                self.destroy()
                return
                
            # Загрузка последнего использованного города
            self.last_city = self.load_last_city()
            
            # Создание интерфейса
            self.create_widgets()
            
            # Запуск автообновления
            self.update_thread = threading.Thread(target=self.auto_update, daemon=True)
            self.update_thread.start()
            
            # Добавление возможности перетаскивания окна
            self.bind('<Button-1>', self.start_move)
            self.bind('<B1-Motion>', self.on_move)
            
        except Exception as e:
            messagebox.showerror("Ошибка инициализации", f"Произошла ошибка: {str(e)}\n\n{traceback.format_exc()}")
            self.destroy()
        
    def create_widgets(self):
        try:
            # Основной фрейм
            self.main_frame = ctk.CTkFrame(self)
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Кнопка закрытия
            self.close_button = ctk.CTkButton(
                self.main_frame, 
                text="×", 
                width=20, 
                command=self.minimize_window
            )
            self.close_button.place(relx=1.0, rely=0.0, anchor="ne")
            
            # Поле ввода города
            self.city_frame = ctk.CTkFrame(self.main_frame)
            self.city_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self.city_entry = ctk.CTkEntry(
                self.city_frame,
                placeholder_text="Введите город",
                width=200
            )
            self.city_entry.pack(side=tk.LEFT, padx=5)
            
            self.search_button = ctk.CTkButton(
                self.city_frame,
                text="Поиск",
                width=70,
                command=self.get_weather
            )
            self.search_button.pack(side=tk.LEFT, padx=5)
            
            # Фрейм с информацией о погоде
            self.weather_frame = ctk.CTkFrame(self.main_frame)
            self.weather_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Метки с информацией о погоде
            self.temp_label = ctk.CTkLabel(
                self.weather_frame,
                text="Температура: --°C",
                font=("Arial", 16)
            )
            self.temp_label.pack(pady=5)
            
            self.humidity_label = ctk.CTkLabel(
                self.weather_frame,
                text="Влажность: --%",
                font=("Arial", 16)
            )
            self.humidity_label.pack(pady=5)
            
            self.desc_label = ctk.CTkLabel(
                self.weather_frame,
                text="Описание: --",
                font=("Arial", 16)
            )
            self.desc_label.pack(pady=5)
            
            # Если есть сохраненный город, загружаем его погоду
            if self.last_city:
                self.city_entry.insert(0, self.last_city)
                self.get_weather()
                
        except Exception as e:
            messagebox.showerror("Ошибка создания интерфейса", f"Произошла ошибка: {str(e)}\n\n{traceback.format_exc()}")
            self.destroy()
            
    def get_weather(self):
        city = self.city_entry.get()
        if not city:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите название города")
            return
            
        # Кодируем название города для URL
        encoded_city = urllib.parse.quote(city)
        
        try:
            # Отключаем кнопку поиска на время запроса
            self.search_button.configure(state="disabled")
            
            # Запрос к API
            url = f"http://api.openweathermap.org/data/2.5/weather?q={encoded_city}&appid={self.api_key}&units=metric&lang=ru"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Обновляем метки с информацией
            self.temp_label.configure(text=f"Температура: {data['main']['temp']:.1f}°C")
            self.humidity_label.configure(text=f"Влажность: {data['main']['humidity']}%")
            self.desc_label.configure(text=f"Описание: {data['weather'][0]['description'].capitalize()}")
            
            # Сохраняем город
            self.save_last_city(city)
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные о погоде: {str(e)}")
        except KeyError:
            messagebox.showerror("Ошибка", "Город не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла неизвестная ошибка: {str(e)}\n\n{traceback.format_exc()}")
        finally:
            # Включаем кнопку поиска обратно
            self.search_button.configure(state="normal")
            
    def save_last_city(self, city):
        try:
            with open("last_city.json", "w", encoding="utf-8") as f:
                json.dump({"city": city}, f)
        except Exception as e:
            print(f"Ошибка сохранения города: {str(e)}")
            
    def load_last_city(self):
        try:
            with open("last_city.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("city", "")
        except (FileNotFoundError, json.JSONDecodeError):
            return ""
        except Exception as e:
            print(f"Ошибка загрузки города: {str(e)}")
            return ""
            
    def auto_update(self):
        while True:
            try:
                if self.city_entry.get():
                    self.get_weather()
                time.sleep(300)  # Обновление каждые 5 минут
            except Exception as e:
                print(f"Ошибка автообновления: {str(e)}")
                time.sleep(60)  # При ошибке ждем минуту перед повторной попыткой
            
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
        
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")
        
    def minimize_window(self):
        self.iconify()  # Сворачиваем окно
        
if __name__ == "__main__":
    try:
        # Устанавливаем тему
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        app = WeatherWidget()
        app.mainloop()
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        print(traceback.format_exc())
        input("Нажмите Enter для выхода...") 