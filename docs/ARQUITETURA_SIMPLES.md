# Arquitetura Simples e Profissional - Sem Loops

## 🎯 A Solução

**Problema:** Múltiplos `.env` causando confusão

**Solução:** `.env` único + `settings.py` inteligente = Automático

---

## 📋 Como Funciona

### Desenvolvimento Local (runserver)
```bash
cd /home/lekao/crm
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

**Automático:**
- ✅ DEBUG=True (detectado, sem HTTP)
- ✅ ALLOWED_HOSTS=localhost (funciona)
- ✅ SQLite (rápido)
- ✅ HTTP (sem HTTPS)
- ✅ Cache em memória

**Acesso:** http://localhost:8000


### Testar com Docker Localmente
```bash
docker-compose -f docker-compose.local.yml up -d
```

**Automático:**
- ✅ DEBUG=True (em .env)
- ✅ PostgreSQL containerizado
- ✅ Redis containerizado
- ✅ HTTP (sem HTTPS)

**Acesso:** http://localhost:8000


### Produção (VPS com Traefik)
```bash
# 1. Editar .env com dados REAIS
vim .env
# Adicionar:
# DEBUG=False
# ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
# LETSENCRYPT_EMAIL=seu-email@dominio.com

# 2. Subir
docker-compose -f docker-compose.traefik.yml up -d
```

**Automático:**
- ✅ DEBUG=False (em .env)
- ✅ SECURE_SSL_REDIRECT=True (settings.py detecta)
- ✅ SESSION_COOKIE_SECURE=True (settings.py detecta)
- ✅ CSRF_COOKIE_SECURE=True (settings.py detecta)
- ✅ HSTS (settings.py detecta)
- ✅ Security headers (settings.py detecta)

**Acesso:** https://seu-dominio.com (com SSL automático)

---

## 🔍 Como settings.py Detecta

```python
# config/settings.py

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Se DEBUG não está definido, padrão é False
# Se DEBUG=False, ativa TODAS as segurança automaticamente:

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    # ... mais headers
```

---

## 📁 Estrutura de Arquivos

```
/home/lekao/crm/
├── .env                              ← ÚNICO arquivo (3 linhas)
├── .env.example                      ← Template para documentação
├── .env.simple                       ← Referência com comentários
│
├── .gitignore                        ← Exclui .env (não commita)
│
├── docker-compose.local.yml          ← Dev/test com Docker
├── docker-compose.traefik.yml        ← Produção com SSL
│
├── config/
│   └── settings.py                   ← Detecta dev vs prod automaticamente
│
└── ...
```

---

## ✅ Arquivos .gitignore (Essencial!)

```
# Não commitar .env com dados reais
.env
.env.local
.env.dev

# Okjá são templates/documentação
# .env.example pode ser commitado
# .env.simple pode ser commitado
```

---

## 🚀 Workflow de Desenvolvimento

### 1. Dia a dia (desenvolvimento)
```bash
source venv/bin/activate
python manage.py runserver

# Editar código normalmente
# Reload automático
# Sem SSL (HTTP local)
# Acesso em http://localhost:8000
```

### 2. Antes de commitar
```bash
# Testar com Docker (opcional)
docker-compose -f docker-compose.local.yml up -d
# ... testar em http://localhost:8000
docker-compose -f docker-compose.local.yml down

# Depois, commitar (sem .env)
git add .
git commit -m "Ajuste na importação CSV"
git push
```

### 3. Deployment em produção
```bash
# Na VPS:
git clone ...
cd crm

# Criar .env com dados REAIS
cat > .env << 'EOF'
DJANGO_SECRET_KEY=novo-secret-aleatorio
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
DEBUG=False
LETSENCRYPT_EMAIL=seu-email@dominio.com
EOF

# Subir com Traefik (SSL automático)
docker-compose -f docker-compose.traefik.yml up -d
```

---

## 🎯 O que Mudou

### ❌ ANTES (Complicado)
- 3 arquivos .env (.env, .env.local, .env.dev)
- Confusão qual usar
- Loops de erro com HTTPS/HTTP

### ✅ DEPOIS (Simples)
- 1 arquivo .env (3 linhas!)
- settings.py detecta automaticamente
- runserver = HTTP automático
- Traefik = HTTPS automático
- Zero loops

---

## 📝 .env Final (Copiar e Colar)

```bash
# Django Secret Key (mude em produção!)
DJANGO_SECRET_KEY=+5c7^irspp62bjq#((sw0b$8ven19%zm5f3l_ws2^5w$$^*zdc

# Allowed hosts
ALLOWED_HOSTS=localhost,127.0.0.1

# APENAS para produção (descomente):
# DEBUG=False
# ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
# LETSENCRYPT_EMAIL=seu-email@dominio.com
```

---

## 🔒 Segurança

- ✅ .env NUNCA é commitado (gitignore)
- ✅ Secrets nunca ficam em código
- ✅ Em produção: SSL, HSTS, security headers (automático)
- ✅ Em dev: HTTP simples (mais rápido)

---

## 🎉 Resumo

| Cenário | Comando | DEBUG | HTTPS | SQLite | Auto |
|---------|---------|-------|-------|--------|------|
| **Dev** | `runserver` | True | ❌ | ✅ | ✅ |
| **Test Docker** | `docker-compose.local.yml` | True | ❌ | ❌ | ✅ |
| **Produção** | `docker-compose.traefik.yml` | False | ✅ | ❌ | ✅ |

---

## ❓ Perguntas Comuns

**P: Como testar HTTPS localmente?**
A: Não é necessário! runserver é HTTP por design. Se precisa testar SSL, use docker-compose.traefik.yml, mas é overkill para dev.

**P: Preciso resetar .env?**
A: Não! Mesmo arquivo funciona em dev e produção. Basta descomentar DEBUG=False e ALLOWED_HOSTS na produção.

**P: E se cometer um erro no .env?**
A: `python manage.py check` mostra erros. Se ficar perdido, volte ao `.env.simple` para referência.

---

**Conclusão:** Zero loops, máxima simplicidade, máxima profissionalismo! 🎯
