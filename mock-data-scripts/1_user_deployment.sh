#!/bin/bash

curl -X POST http://127.0.0.1:8000/api/auth/register/ -H "Accept: */*" -H "Content-Type: application/json" --data-binary @- <<DATA
{"email":"test@test.com","password1":"kalichowszczyzna","password2":"kalichowszczyzna","social_contact":"wp.pl","username":"testowy"}
DATA

curl -X POST http://127.0.0.1:8000/api/auth/register/ -H "Accept: */*" -H "Content-Type: application/json" --data-binary @- <<DATA
{"email":"sposob.1104@gmail.com","password1":"kalichowszczyzna","password2":"kalichowszczyzna","social_contact":"wp.pl","username":"sposob.1104@gmail.com"}
DATA

curl -X POST http://127.0.0.1:8000/api/auth/register/ -H "Accept: */*" -H "Content-Type: application/json" --data-binary @- <<DATA
{"email":"wayson.1104@gmail.com","password1":"kalichowszczyzna","password2":"kalichowszczyzna","social_contact":"wp.pl","username":"wayson.1104@gmail.com"}
DATA
