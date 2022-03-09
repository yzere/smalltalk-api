from api.models import *
import datetime
import pytz



def add_user(x):
    i=0

    while True:
        CustomUser(password="argon2$argon2id$v=19$m=102400,t=2,p=8$NWttczVqZmt3R3VzalJhVGRZdGFZNw$zdIqskqHa1EddoAXBBdlebTWhxwRxEUI3+HJ+nK14C0", username="user"+str(i), email=str(i)+"@a.pl").save()
        i+=1
        if i == x:
            break

def circle(y):
    i=0
    date = datetime.datetime(2022, 12, 10, 10, 1, 1)
    date = pytz.utc.localize(date)

    while True:
        Circle(expire_date=date, name=str(i), max_users=40).save()
        i+=1
        if i == y:
            break
