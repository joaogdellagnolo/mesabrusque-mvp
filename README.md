# 🍽️ MesaBrusque — MVP de Descoberta, Reservas e Cupons (Brusque/SC)

Aplicativo Mobile-First estilo "iFood de Reservas / TheFork" focado em **Brusque/SC**, onde os usuários exploram o mapa da cidade, visualizam mesas disponíveis em tempo real, fazem reservas instantâneas e ganham cupons de desconto para preencher horários ociosos dos restaurantes parceiros.

---

## 🚀 Stack Tecnológica

- **Frontend:** React 18 (Vite) + Tailwind CSS + Lucide Icons
- **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0
- **Banco de Dados:** PostgreSQL (com fallback automático para SQLite local em desenvolvimento)

---

## 🛠️ Como Rodar o Projeto (No Trabalho ou em Casa)

### Opção Rápida (Sem precisar instalar nada)
Basta abrir o arquivo `abrir-app.html` diretamente no navegador (ou pressionar `F5` no VS Code / Antigravity).

### Rodando Backend (FastAPI) + Frontend (Vite)

1. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```
   - API: `http://localhost:8000`
   - Swagger Docs: `http://localhost:8000/docs`

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - App: `http://localhost:5173`

