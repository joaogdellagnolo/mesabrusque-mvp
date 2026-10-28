@echo off
chcp 65001 >nul
echo =========================================================
echo   Configurando Git e Enviando para github.com/joaogdellagnolo
echo =========================================================
echo.

:: 1. Verifica se o Git esta instalado; se nao, instala via winget
if not exist "C:\Program Files\Git\cmd\git.exe" (
    echo [1/4] Instalando o Git no Windows...
    winget install -e --id Git.Git --accept-source-agreements --accept-package-agreements
)

:: 2. Verifica se o GitHub CLI (gh) esta instalado; se nao, instala via winget
if not exist "C:\Program Files\GitHub CLI\gh.exe" (
    echo [2/4] Instalando o GitHub CLI...
    winget install -e --id GitHub.cli --accept-source-agreements --accept-package-agreements
)

set "PATH=%PATH%;C:\Program Files\Git\cmd;C:\Program Files\GitHub CLI"

echo.
echo [3/4] Preparando repositorio local e commit...
cd /d "%~dp0"

if not exist ".git" (
    git init -b main
)

git config user.name "joaogdellagnolo"
git config user.email "joaogdellagnolo@users.noreply.github.com"

git add .
git commit -m "feat: MVP completo MesaBrusque (FastAPI + React + Tailwind)"

echo.
echo [4/4] Autenticando na sua conta do GitHub (joaogdellagnolo)...
echo (Aperte ENTER quando solicitado para abrir o navegador e autorizar)
echo.
gh auth status >nul 2>&1
if errorlevel 1 (
    gh auth login --web -h github.com -p https
)

echo.
echo Criando repositorio 'mesabrusque-mvp' e enviando arquivos...
gh repo create joaogdellagnolo/mesabrusque-mvp --public --source=. --remote=origin --push

if errorlevel 1 (
    echo.
    echo Caso o repositorio ja exista, enviando push diretamente...
    git remote add origin https://github.com/joaogdellagnolo/mesabrusque-mvp.git 2>nul
    git branch -M main
    git push -u origin main
)

echo.
echo =========================================================
echo   CONCLUIDO! Acesse seu projeto em:
echo   https://github.com/joaogdellagnolo/mesabrusque-mvp
echo =========================================================
pause

