# VyaparVoice

VyaparVoice is a voice-first inventory app for small businesses. It now uses MongoDB with store-owner authentication and JWT-protected, owner-isolated inventory data.

## Requirements

- Python 3.11+
- Node.js 18+
- MongoDB locally or a MongoDB Atlas connection string

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

Set `MONGODB_URI`, `MONGODB_DATABASE`, and a strong `JWT_SECRET_KEY` in `backend/.env`. The API creates MongoDB indexes on startup. Health is available at `http://localhost:8000/api/health` and API docs at `http://localhost:8000/docs`.

## Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open the Vite URL, usually `http://localhost:5173`. Set `VITE_API_URL` in `frontend/.env` if the backend uses another URL.

## Authentication

- `/signup` creates an owner with store information and preferences.
- `/signin` returns a JWT and stores it in `localStorage`.
- Protected API requests receive `Authorization: Bearer <token>` automatically.
- `/api/auth/me` restores the owner on refresh.
- Products, transactions, dashboard calculations, NLP matching, and assistant logs are always filtered by the JWT-derived owner ID.
- Logout removes local credentials. The server does not store plaintext passwords.

## MongoDB collections

`store_owners`, `products`, `transactions`, and `assistant_logs` are stored in the configured `vyaparvoice` database. Product and transaction seed data is created for a new owner only, after signup/login integration can be extended to call the seed service.

## Demo commands

- `20 kilo rice add karo`
- `5 kilo rice bech diya`
- `How much rice do I have?`
- `Which items are low?`
- `What should I reorder?`

## Important

The current workspace does not include a MongoDB server binary, so the application requires MongoDB or Atlas to be running before startup. Do not commit `.env` or real credentials.
