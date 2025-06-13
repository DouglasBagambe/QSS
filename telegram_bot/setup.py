from setuptools import setup, find_packages

setup(
    name="telegram_bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiogram>=3.0.0",
        "python-dotenv>=0.19.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "requests>=2.26.0",
        "aiohttp>=3.8.0",
        "python-telegram-bot>=20.0",
        "pytz>=2021.1",
        "python-dateutil>=2.8.2",
        "fastapi==0.115.12",
        "uvicorn==0.34.3",
        "pydantic==2.11.5",
        "python-multipart==0.0.20",
        "httpx",
        "gunicorn==23.0.0",
        "pytz==2025.2"
    ],
    python_requires=">=3.8",
) 