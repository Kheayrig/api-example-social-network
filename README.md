<h2>Социальная сеть</h2>

Реализация REST-API социальной сети на фреймворке fastapi

<h2>Установка</h2>
Требуется наличие базы данных PostgreSQL или наличие доступа к ней

<b>Ubuntu</b>:

Установка python3:
sudo apt update
sudo apt install python3 python3-pip
Установка зависимостей:
pip3 install -r requirements.txt

<h2>Запуск</h2>

python3 -m uvicorn main:app

<h2>Настройка</h2>

configs - Конфиги подключения -> #server, #database, #data_path


<h2>Пример работы</h2>

Посмотреть, как будет функционировать сервис, можно тут:

https://api-example-social-network.herokuapp.com/docs

