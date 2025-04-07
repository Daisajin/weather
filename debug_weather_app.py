import tkinter as tk
from tkinter import messagebox
import requests
import os
import sys
import traceback

print("Запуск отладочной версии приложения...")
print(f"Python версия: {sys.version}")
print(f"Текущая директория: {os.getcwd()}")

try:
    from dotenv import load_dotenv
    print("Библиотека dotenv загружена успешно")
except ImportError as e:
    print(f"Ошибка загрузки dotenv: {e}")
    input("Нажмите Enter для выхода...")
    sys.exit(1)

# Загрузка переменных окружения
load_dotenv()
print("Переменные окружения загружены")

class WeatherApp:
    def __init__(self, root):
        print("Инициализация приложения...")
        self.root = root
        self.root.title("Погода (Отладка)")
        self.root.geometry("300x400")
        
        # API конфигурация
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        print(f"API ключ: {'Установлен' if self.api_key and self.api_key != 'your_api_key_here' else 'Не установлен или неверный'}")
        
        if not self.api_key or self.api_key == "your_api_key_here":
            messagebox.showerror("Ошибка", "Пожалуйста, установите правильный OPENWEATHER_API_KEY в файле .env")
            root.destroy()
            return
            
        # Создание интерфейса
        self.create_widgets()
        print("Интерфейс создан успешно")
        
    def create_widgets(self):
        print("Создание элементов интерфейса...")
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
        
        print("Элементы интерфейса созданы успешно")
            
    def get_weather(self):
        city = self.city_entry.get()
        if not city:
            messagebox.showwarning("Предупреждение", "Пожалуйста, введите название города")
            return
            
        print(f"Запрос погоды для города: {city}")
        
        try:
            # Отключаем кнопку поиска на время запроса
            self.search_button.configure(state="disabled")
            
            # Запрос к API
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric&lang=ru"
            print(f"URL запроса: {url}")
            
            response = requests.get(url)
            print(f"Код ответа: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            print(f"Получены данные: {data}")
            
            # Обновляем метки с информацией
            self.temp_label.config(text=f"Температура: {data['main']['temp']:.1f}°C")
            self.humidity_label.config(text=f"Влажность: {data['main']['humidity']}%")
            self.desc_label.config(text=f"Описание: {data['weather'][0]['description'].capitalize()}")
            
            print("Данные успешно обновлены")
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            messagebox.showerror("Ошибка", f"Не удалось получить данные о погоде: {str(e)}")
        except KeyError as e:
            print(f"Ошибка ключа: {e}")
            messagebox.showerror("Ошибка", "Город не найден")
        except Exception as e:
            print(f"Неизвестная ошибка: {e}")
            print(traceback.format_exc())
            messagebox.showerror("Ошибка", f"Произошла неизвестная ошибка: {str(e)}")
        finally:
            # Включаем кнопку поиска обратно
            self.search_button.configure(state="normal")

if __name__ == "__main__":
    try:
        print("Создание главного окна...")
        root = tk.Tk()
        app = WeatherApp(root)
        print("Запуск главного цикла...")
        root.mainloop()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        print(traceback.format_exc())
        input("Нажмите Enter для выхода...") 