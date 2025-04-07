import tkinter as tk
from tkinter import ttk, messagebox
import requests
import os
from dotenv import load_dotenv
import json
import urllib.parse
import threading
import time
import traceback

# Загрузка переменных окружения
load_dotenv()

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Погода")
        self.root.geometry("300x400")
        
        # API конфигурация
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key or self.api_key == "your_api_key_here":
            messagebox.showerror("Ошибка", "Пожалуйста, установите правильный OPENWEATHER_API_KEY в файле .env")
            root.destroy()
            return
            
        # Загрузка последнего использованного города
        self.last_city = self.load_last_city()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Запуск автообновления
        self.update_thread = threading.Thread(target=self.auto_update, daemon=True)
        self.update_thread.start()
        
    def create_widgets(self):
        # Основной фрейм
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поле ввода города
        ttk.Label(self.main_frame, text="Введите город:").pack(anchor=tk.W, pady=5)
        
        self.city_frame = ttk.Frame(self.main_frame)
        self.city_frame.pack(fill=tk.X, pady=5)
        
        self.city_entry = ttk.Entry(self.city_frame, width=30)
        self.city_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_button = ttk.Button(
            self.city_frame,
            text="Поиск",
            command=self.get_weather
        )
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        # Фрейм с информацией о погоде
        self.weather_frame = ttk.LabelFrame(self.main_frame, text="Информация о погоде", padding="10")
        self.weather_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Метки с информацией о погоде
        self.temp_label = ttk.Label(
            self.weather_frame,
            text="Температура: --°C",
            font=("Arial", 12)
        )
        self.temp_label.pack(anchor=tk.W, pady=5)
        
        self.humidity_label = ttk.Label(
            self.weather_frame,
            text="Влажность: --%",
            font=("Arial", 12)
        )
        self.humidity_label.pack(anchor=tk.W, pady=5)
        
        self.desc_label = ttk.Label(
            self.weather_frame,
            text="Описание: --",
            font=("Arial", 12)
        )
        self.desc_label.pack(anchor=tk.W, pady=5)
        
        # Если есть сохраненный город, загружаем его погоду
        if self.last_city:
            self.city_entry.insert(0, self.last_city)
            self.get_weather()
            
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
            self.temp_label.config(text=f"Температура: {data['main']['temp']:.1f}°C")
            self.humidity_label.config(text=f"Влажность: {data['main']['humidity']}%")
            self.desc_label.config(text=f"Описание: {data['weather'][0]['description'].capitalize()}")
            
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

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = WeatherApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        print(traceback.format_exc())
        input("Нажмите Enter для выхода...") 