# smallTalk: stare społeczności - nowe znajomości
Nasza aplikacja łączy ludzi, którzy podczas codziennego życia nigdy nie mieli by okazji się spotkać, mimo, że mogą mieć ze sobą wiele wspólnego. Dobierani są ludzie ze wspólnych środowisk (np. szkoła), a następnie dodaje ich do anonimowego chatu, dając możliwość ujawnienia się po udanej rozmowie.

Z czego składa się nasz projekt?
 strona internetowa informacyjna
 profile na mediach społecznościowych
 strona internetowa aplikacji (funkcjonalna)
 aplikacja mobilna (funkcjonalna)
 baza danych znajdująca się na naszym serwerze
 komponent funkcjonalny odpowiadający za uwierzytelnianie użytkowników czy łączenie osób ze sobą znajdujący się również na naszym serwerze


Jak korzystać z bazy PostgreSQL?
Instalacja PosgreSQL:
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get -y install postgresql
sudo service postgresql start                                                       #polecenie dla WSL
sudo systemctl start postgresql                                                     #polecenie dla normalnego Ubuntu

Tworzenie bazy danych:
sudo su - postgres
psql
CREATE DATABASE db;                                                                 #db to nazwa bazy danych, jeżeli wpiszemy inną to trzeba zmienić w settings.py
CREATE USER admin WITH PASSWORD 'admin';                                            #analogicznie ^
ALTER ROLE admin SET client_encoding TO 'utf8';                                     #analogicznie ^
ALTER ROLE admin SET default_transaction_isolation TO 'read committed';             #analogicznie ^
ALTER ROLE admin SET timezone TO 'UTC';                                             #analogicznie ^
GRANT ALL PRIVILEGES ON DATABASE db TO admin;                                       #analogicznie ^
\q
exit

Instalacja pakietów dla pythona:
pip3 install -r req.txt

Migracje:
Tak samo jak dla sqlite3