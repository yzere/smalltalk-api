#!/bin/bash

curl -X POST http://127.0.0.1:8000/api/models/circles/ -H "Accept: */*" -H "Content-Type: application/json" --data-binary @- <<DATA
{
    "circle_ID": 1,
    "name": "Wiśniowa",
    "localization": "Wiśniowa 56, Warszawa",
    "description": "Krąg stworzony dla uczniów szkoły.",
    "expire_date": "2025-11-05T22:24",
    "max_users": 55,
    "stats": null,
    "admin_users_IDs": [
        1
    ],
    "reports_IDs": [],
    "users_IDs": [
        1,
        2
    ]
}
DATA
