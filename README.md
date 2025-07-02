# Restaurant QR Payment System

This project allows restaurant customers to scan a QR code at their table, view their items, and pay securely via Stripe Checkout — all without waiting for the waiter.

## Tech Stack

- **Frontend:** Angular (standalone components)
- **Backend:** Django
- **Payments:** Stripe Checkout (Test & Live modes supported)

## Features

- QR-based table access (e.g. `/mesa/5`)
- Item selection per customer
- Dynamic total calculation
- One-click Stripe Checkout integration
- Success and cancel pages
- Environment-safe config for both dev and production

## Local Development
1. Backend (Django)
python manage.py runserver

2. Frontend (Angular)
cd qr-pay
npm install
ng serve

Open: http://localhost:4200/mesa/1

Stripe Test Card
Card Number: 4242 4242 4242 4242
Exp: Any future date
CVC: Any 3 digits
ZIP: Any