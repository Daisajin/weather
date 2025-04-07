import tkinter as tk
from tkinter import messagebox
import requests
import os
import json
import urllib.parse

# Загрузка API ключа из файла .env
def load_api_key():
    try:
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("WEATHERAPI_KEY="):
                    return line.strip().split("=", 1)[1]
    except Exception as e:
        print(f"Ошибка загрузки API ключа: {e}")
    return None

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Погода")
        self.root.geometry("300x400")
        
        # API конфигурация
        self.api_key = load_api_key()
        if not self.api_key or self.api_key == "your_api_key_here":
            messagebox.showerror("Ошибка", "Пожалуйста, установите правильный WEATHERAPI_KEY в файле .env")
            root.destroy()
            return
            
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Основной фрейм
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Поле ввода города
        tk.Label(self.main_frame, text="Введите город:").pack(anchor=tk.W, pady=5)
        
        self.city_entry = tk.Entry(self.main_frame, width=30)
        self.city_entry.pack(fill=tk.X, pady=5)
        
        self.search_button = tk.Button(
            self.main_frame,
            text="Поиск",
            command=self.get_weather
        )
        self.search_button.pack(pady=5)
        
        # Фрейм с информацией о погоде
        self.weather_frame = tk.LabelFrame(self.main_frame, text="Информация о погоде")
        self.weather_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Метки с информацией о погоде
        self.temp_label = tk.Label(
            self.weather_frame,
            text="Температура: --°C"
        )
        self.temp_label.pack(anchor=tk.W, pady=5)
        
        self.humidity_label = tk.Label(
            self.weather_frame,
            text="Влажность: --%"
        )
        self.humidity_label.pack(anchor=tk.W, pady=5)
        
        self.desc_label = tk.Label(
            self.weather_frame,
            text="Описание: --"
        )
        self.desc_label.pack(anchor=tk.W, pady=5)
            
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
            
            # Запрос к API WeatherAPI.com
            url = f"http://api.weatherapi.com/v1/current.json?key={self.api_key}&q={encoded_city}&lang=ru"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Обновляем метки с информацией
            self.temp_label.config(text=f"Температура: {data['current']['temp_c']:.1f}°C")
            self.humidity_label.config(text=f"Влажность: {data['current']['humidity']}%")
            self.desc_label.config(text=f"Описание: {data['current']['condition']['text'].capitalize()}")
            
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Не удалось получить данные о погоде: {str(e)}")
        except KeyError:
            messagebox.showerror("Ошибка", "Город не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла неизвестная ошибка: {str(e)}")
        finally:
            # Включаем кнопку поиска обратно
            self.search_button.configure(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop() 