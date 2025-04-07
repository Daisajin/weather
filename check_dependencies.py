import sys
import subprocess
import os

def check_python_version():
    print(f"Версия Python: {sys.version}")
    if sys.version_info < (3, 6):
        print("ОШИБКА: Требуется Python 3.6 или выше")
        return False
    return True

def check_package(package_name):
    try:
        __import__(package_name)
        print(f"✓ {package_name} установлен")
        return True
    except ImportError:
        print(f"✗ {package_name} не установлен")
        return False

def install_package(package_name):
    print(f"Установка {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ {package_name} успешно установлен")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Ошибка при установке {package_name}")
        return False

def check_env_file():
    if os.path.exists(".env"):
        print("✓ Файл .env найден")
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
            if "WEATHERAPI_KEY=" in content:
                api_key = content.split("WEATHERAPI_KEY=", 1)[1].strip()
                if api_key and api_key != "your_api_key_here":
                    print("✓ API ключ установлен")
                    return True
                else:
                    print("✗ API ключ не установлен или установлен placeholder")
                    return False
            else:
                print("✗ В файле .env отсутствует WEATHERAPI_KEY")
                return False
    else:
        print("✗ Файл .env не найден")
        return False

def main():
    print("=== Проверка зависимостей ===")
    
    # Проверка версии Python
    if not check_python_version():
        return
    
    # Проверка необходимых пакетов
    required_packages = ["requests"]
    missing_packages = []
    
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    # Установка отсутствующих пакетов
    if missing_packages:
        print("\nУстановка отсутствующих пакетов...")
        for package in missing_packages:
            install_package(package)
    
    # Проверка файла .env
    print("\n=== Проверка файла .env ===")
    check_env_file()
    
    print("\n=== Инструкции ===")
    print("1. Зарегистрируйтесь на сайте https://www.weatherapi.com/ для получения бесплатного API ключа")
    print("2. Убедитесь, что в файле .env указан правильный API ключ от WeatherAPI.com")
    print("3. Запустите приложение командой: python minimal_weather_app.py")

if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...") 