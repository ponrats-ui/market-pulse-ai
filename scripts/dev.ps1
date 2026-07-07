Set-Location "$PSScriptRoot\.."
Write-Host "Backend: cd backend; .venv\Scripts\activate; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Write-Host "Frontend: cd frontend; npm run dev"
