# Stacks de Desenvolvimento e Produção

## 📋 Resumo das Opções

| Opção | Ambiente | Uso | Comando |
|-------|----------|-----|---------|
| **runserver** | Local direto | Desenvolvimento rápido | `python manage.py runserver` |
| **docker-compose.local.yml** | Docker local | Testar com DB/Redis | `docker-compose -f docker-compose.local.yml up` |
| **docker-compose.traefik.yml** | Docker produção | Deploy com Traefik+SSL | `docker-compose -f docker-compose.traefik.yml up -d` |

---

## 🚀 RECOMENDADO: Fluxo de Desenvolvimento

### 1️⃣ **Desenvolvimento Rápido** (Código fonte local)

Usar `python manage.py runserver` quando está ajustando código:

```bash
cd /home/lekao/crm
source venv/bin/activate
# Certifique-se de estar com .env.local ou DEBUG=True
python manage.py runserver 0.0.0.0:8000
```

**Vantagens:**
- ✅ Reload automático ao salvar arquivos
- ✅ Django debug toolbar
- ✅ Mais rápido para iterações
- ✅ Stack local (PostgreSQL + Redis opcional)

---

### 2️⃣ **Testar Stack Completa** (Docker local)

Quando quer testar com Docker antes de commitar:

```bash
# Build da imagem
docker-compose -f docker-compose.local.yml build

# Subir containers
docker-compose -f docker-compose.local.yml up -d

# Ver logs
docker-compose -f docker-compose.local.yml logs -f web

# Rodar migrations
docker-compose -f docker-compose.local.yml exec web python manage.py migrate

# Acessar
http://localhost:8000
```

**Vantagens:**
- ✅ Testa o Dockerfile localmente
- ✅ Simula ambiente com DB e Redis containerizados
- ✅ Volume montado permite editar código
- ✅ Pronto para deploy

---

### 3️⃣ **Deploy em Produção** (Traefik)

Quando pronto para produção:

```bash
# Configurar .env com dados REAIS
vim /home/lekao/crm/.env

# Subir stack
docker-compose -f docker-compose.traefik.yml up -d

# Ver logs
docker-compose -f docker-compose.traefik.yml logs -f web

# Acessar
https://seu-dominio.com
```

---

## 🔄 Workflow Recomendado

```
1. Editar código localmente
   ↓
2. Testar com "runserver" (desenvolvimento rápido)
   ↓
3. Commitar no git
   ↓
4. (Opcional) Testar com docker-compose.local.yml
   ↓
5. Build e push da imagem para registry
   ↓
6. Deploy com docker-compose.traefik.yml em produção
```

---

## 📁 Arquivos de Configuração

```
/home/lekao/crm/
├── .env                           ← Produção (ignore no git)
├── .env.local                     ← Dev local com SQLite (ignore no git)
├── .env.dev                       ← Dev local com Docker (ignore no git)
├── .env.example                   ← Template (commitar)
│
├── docker-compose.yml             ← Legado (não usar)
├── docker-compose.local.yml       ← Para dev com Docker ✅
├── docker-compose.traefik.yml     ← Para produção ✅
│
├── Dockerfile                     ← Build da imagem
├── requirements.txt               ← Dependências Python
└── gunicorn.conf.py              ← Configuração Gunicorn
```

---

## 🛠️ Comandos Úteis

### Desenvolvimento com runserver

```bash
# Ativar venv
source venv/bin/activate

# Usar .env.local (DEBUG=True, SQLite)
# Rodar servidor
python manage.py runserver

# Testar API específica
curl http://localhost:8000/crm/kanban/
```

### Desenvolvimento com Docker

```bash
# Build apenas (não sobe containers)
docker-compose -f docker-compose.local.yml build

# Subir tudo
docker-compose -f docker-compose.local.yml up -d

# Só logs do web
docker-compose -f docker-compose.local.yml logs -f web

# Entrar no container
docker-compose -f docker-compose.local.yml exec web bash

# Rodar comando no container
docker-compose -f docker-compose.local.yml exec web python manage.py migrate

# Parar tudo
docker-compose -f docker-compose.local.yml down

# Parar e deletar volumes
docker-compose -f docker-compose.local.yml down -v
```

### Produção com Traefik

```bash
# Verificar se .env está correto
cat .env | grep -E "(DEBUG|ALLOWED_HOSTS|LETSENCRYPT)"

# Build da imagem
docker-compose -f docker-compose.traefik.yml build

# Subir
docker-compose -f docker-compose.traefik.yml up -d

# Ver status
docker-compose -f docker-compose.traefik.yml ps

# Ver logs
docker-compose -f docker-compose.traefik.yml logs -f web

# Traefik dashboard
http://localhost:8080

# Parar (mantém volumes)
docker-compose -f docker-compose.traefik.yml down

# Parar e limpar TUDO
docker-compose -f docker-compose.traefik.yml down -v
```

---

## ✅ Checklist de Desenvolvimento

### Antes de Commitar

- [ ] Código testado com `runserver`
- [ ] Sem erros no `python manage.py check`
- [ ] Migrations criadas se mudou models
- [ ] `.env` e `.env.local` estão no `.gitignore`
- [ ] Nenhum hardcoded secret foi commitado

### Antes de Deploy

- [ ] `.env.dev` não tem dados reais (é template)
- [ ] `docker-compose.local.yml` sobe sem erros
- [ ] Código commitado no git
- [ ] `.env` configurado com dados REAIS
- [ ] `docker-compose.traefik.yml` pronto para executar

---

## 🎯 TL;DR (Resumo Rápido)

```bash
# Para desenvolvimento (RECOMENDADO)
source venv/bin/activate
python manage.py runserver

# Para testar Docker localmente
docker-compose -f docker-compose.local.yml up -d
# Acessar em http://localhost:8000

# Para produção
docker-compose -f docker-compose.traefik.yml up -d
# Acessar em https://seu-dominio.com
```

---

## 🚨 Diferenças Principais

### runserver (desenvolvimento)
- Acesso direto ao código
- Reload automático
- Debug toolbar ativado
- Sem containerização

### docker-compose.local.yml (test Docker localmente)
- Containerizado como produção
- Pode editar código e ver em tempo real (volume montado)
- Database PostgreSQL containerizado
- Redis containerizado

### docker-compose.traefik.yml (produção)
- Containerizado com Traefik
- SSL automático com Let's Encrypt
- Rate limiting
- Security headers automáticos
- Zero downtime deployment

---

## 📝 Exemplo: Fluxo Completo

```bash
# 1. Clonar repositório
git clone https://github.com/seu-repo/crm.git
cd crm

# 2. Instalar dependências locais
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Ajustar código
vim crm/views.py          # Fazer alterações
python manage.py runserver # Testar localmente

# 4. Commitar
git add .
git commit -m "Ajuste na importação CSV"

# 5. (Opcional) Testar com Docker
docker-compose -f docker-compose.local.yml up -d
# http://localhost:8000
docker-compose -f docker-compose.local.yml down

# 6. Push para repositório
git push origin main

# 7. Na VPS, fazer deploy
ssh seu-servidor
cd /home/lekao/crm
git pull origin main
docker-compose -f docker-compose.traefik.yml up -d
```

---

**Resumo:** Use `runserver` para desenvolvimento rápido, `docker-compose.local.yml` para testar a stack completa antes de commitar, e `docker-compose.traefik.yml` para produção! 🎉
