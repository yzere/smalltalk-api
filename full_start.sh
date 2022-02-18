# Jeżeli chcemy zrobić alias pozwalający na odpalanie tego z dowolnego miejsca w systemi za pomocą jednego polecenia, należy
# dopisać poniższą linię do pliku "~/.bashrc" na końcu a następnie wpisać "source ~/.bashrc". 

#   alias full_api_start="source $HOME/Projects/smalltalk-api/full_start.sh"

#!/usr/bin/bash
source ~/Projects/smalltalk-api/venv/bin/activate
python ~/Projects/smalltalk-api/manage.py makemigrations
python ~/Projects/smalltalk-api/manage.py migrate
python ~/Projects/smalltalk-api/manage.py runserver
