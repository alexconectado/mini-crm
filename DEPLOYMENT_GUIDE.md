# 🚀 Guia de Deployment - Mini CRM

## Índice
1. [Desenvolvimento Local](#desenvolvimento-local)
2. [Docker Local](#docker-local)
3. [Produção com VPS](#produção-com-vps)
4. [Troubleshooting](#troubleshooting)

---

## Desenvolvimento Local

### Pré-requisitos
- Python 3.10+
- pip
- virtualenv (opcional, mas recomendado)

### Setup

```bash
# 1. Clonar repositório
git clone https://github.com/alexconectado/mini-crm.git
cd mini-crm

# 2. Criar virtualenv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Editar .env com seus valores (deixar DEBUG=True)

# 5. Rodas migrations
python manage.py migrate

# 6. Criar superuser
python manage.py createsuperuser

# 7. Iniciar servidor
python manage.py runserver

# 8. Acessar
http://localhost:8000/crm/
```

### Usuários de Teste
```
Admin: hudson / 123456
Vendedor: vendedor1 / 123456
```

---

## Docker Local

Ideal para testar com PostgreSQL antes de subir em VPS.

### Pré-requisitos
- Docker
- Docker Compose

### Setup

```bash
# 1. Clonar repositório
git clone https://github.com/alexconectado/mini-crm.git
cd mini-crm

# 2. Copiar .env.example
cp .env.example .env

# 3. Editar .env (ajustar para Docker local)
# DEBUG=True
# ALLOWED_HOSTS=localhost,127.0.0.1,web
# USE_POSTGRES=True
# DB_HOST=db
# DB_NAME=crm_db
# DB_USER=crm_user
# DB_PASSWORD=crm_senha_local

# 4. Build e iniciar containers
docker-compose -f docker-compose.local.yml up -d

# 5. Verificar logs
docker-compose -f docker-compose.local.yml logs -f web

# 6. Acessar
http://localhost:8000/crm/

# 7. Parar containers
docker-compose -f docker-compose.local.yml down
```

### Comandos úteis

```bash
# Ver status dos containers
docker-compose -f docker-compose.local.yml ps

# Ver logs em tempo real
docker-compose -f docker-compose.local.yml logs -f web

# Acessar shell do container
docker-compose -f docker-compose.local.yml exec web bash

# Rodas migrations dentro do container
docker-compose -f docker-compose.local.yml exec web python manage.py migrate

# Criar superuser no container
docker-compose -f docker-compose.local.yml exec web python manage.py createsuperuser

# Parar e remover tudo (incluindo dados)
docker-compose -f docker-compose.local.yml down -v
```

---

## Produção com VPS

### Arquitetura
```
Internet
   ↓
Traefik (Reverse Proxy + SSL)
   ↓
Django (Gunicorn)
   ↓
PostgreSQL + Redis
```

### Pré-requisitos
- VPS com Docker e Docker Compose
- Domínio apontando para IP da VPS
- SSH acesso à VPS
- 1GB RAM mínimo, 2GB recomendado

### Step-by-step

#### 1. Acessar VPS
```bash
ssh root@seu-vps-ip
```

#### 2. Instalar Docker e Docker Compose
```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar
docker --version
docker-compose --version
```

#### 3. Clonar projeto
```bash
cd /opt
git clone https://github.com/alexconectado/mini-crm.git crm
cd crm
```

#### 4. Criar .env para produção
```bash
cat > .env <<'EOF'
# Django
DEBUG=False
DJANGO_SECRET_KEY=gerar-chave-segura-aqui
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
SITE_URL=https://seu-dominio.com

# Database
USE_POSTGRES=True
DB_ENGINE=django.db.backends.postgresql
DB_HOST=db
DB_PORT=5432
DB_NAME=crm_prod
DB_USER=crm_user
DB_PASSWORD=gerar-senha-forte-aqui

# Redis
REDIS_URL=redis://redis:6379/1
CACHE_ENABLED=True

# SSL
LETSENCRYPT_EMAIL=seu-email@example.com
SSL_ENABLED=True

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
EOF
```

**⚠️ Importante:** Gerar chaves seguras:
```bash
# Gerar DJANGO_SECRET_KEY
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Gerar DB_PASSWORD (16 caracteres aleatórios)
openssl rand -base64 12
```

#### 5. Build e deploy
```bash
# Build da imagem
docker-compose -f docker-compose.traefik.yml build

# Iniciar containers
docker-compose -f docker-compose.traefik.yml up -d

# Aguardar 30 segundos e verificar logs
sleep 30
docker-compose -f docker-compose.traefik.yml logs web | tail -20
```

#### 6. Criar superuser
```bash
docker-compose -f docker-compose.traefik.yml exec web python manage.py createsuperuser
```

#### 7. Testar acesso
```bash
# HTTP deve redirecionar para HTTPS
curl -I http://seu-dominio.com
# Deve retornar 301 com Location: https://seu-dominio.com

# HTTPS deve funcionar
curl -I https://seu-dominio.com
# Deve retornar 200
```

#### 8. Acessar aplicação
```
https://seu-dominio.com
```

### Após deploy

#### Verificar Health Check
```bash
docker-compose -f docker-compose.traefik.yml exec web curl -f http://localhost:8000/crm/
```

#### Ver Traefik Dashboard (opcional)
```
http://seu-dominio.com:8080
```
⚠️ **Remover em produção** (comentar porta 8080 no docker-compose)

#### Backups automáticos
```bash
# Fazer backup manual do banco
docker-compose -f docker-compose.traefik.yml exec db pg_dump -U crm_user crm_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker-compose -f docker-compose.traefik.yml exec -T db psql -U crm_user crm_prod < backup_YYYYMMDD_HHMMSS.sql
```

---

## Troubleshooting

### Erro: "Connection refused" ao conectar ao banco
```bash
# Verificar se containers estão rodando
docker-compose ps

# Verificar logs do banco
docker-compose logs db

# Solução: Reiniciar containers
docker-compose down
docker-compose up -d
```

### Erro: "Static files not found"
```bash
# Coletar static files novamente
docker-compose exec web python manage.py collectstatic --noinput

# Reiniciar web
docker-compose restart web
```

### Erro: "Permission denied" ao clonar/fazer push
```bash
# Usar HTTPS ao invés de SSH
git remote set-url origin https://github.com/alexconectado/mini-crm.git
```

### App lento ou timeout
```bash
# Verificar recursos
docker stats

# Aumentar timeout no Traefik
# (editar docker-compose.traefik.yml, seção 'timeout' do serviço web)

# Verificar logs
docker-compose logs -f web
```

### Certificado SSL não funcionando
```bash
# Verificar logs do Traefik
docker-compose logs traefik | grep -i "Let's Encrypt\|certificate\|acme"

# Certificado pode levar 1-2 minutos na primeira vez
# Aguardar e acessar via HTTPS

# Se continuar falhando:
# 1. Verificar se domínio está apontando corretamente (nslookup seu-dominio.com)
# 2. Verificar se porta 80 está aberta (curl -I http://seu-dominio.com)
# 3. Remover arquivo letsencrypt/acme.json e tentar novamente
rm -rf letsencrypt/acme.json
docker-compose restart traefik
```

### Erro "Secret key is not set" em produção
```bash
# Verificar se .env está carregando
docker-compose exec web env | grep DJANGO_SECRET_KEY

# Solução: Editar .env e adicionar valor real
# Reiniciar containers
docker-compose down
docker-compose up -d
```

---

## Operações Comuns em Produção

### Fazer update do código
```bash
cd /opt/crm
git pull origin main
docker-compose -f docker-compose.traefik.yml down
docker-compose -f docker-compose.traefik.yml build
docker-compose -f docker-compose.traefik.yml up -d
```

### Ver logs em tempo real
```bash
docker-compose -f docker-compose.traefik.yml logs -f web
```

### Parar aplicação (manutenção)
```bash
docker-compose -f docker-compose.traefik.yml down
```

### Reiniciar aplicação
```bash
docker-compose -f docker-compose.traefik.yml up -d
```

### Monitorar recursos
```bash
docker stats
```

---

## Checklist Final

- [ ] `.env` criado com valores reais
- [ ] `DJANGO_SECRET_KEY` gerado e único
- [ ] `DB_PASSWORD` alterada
- [ ] Domínio apontando para IP da VPS
- [ ] Docker e Docker Compose instalados
- [ ] Containers iniciados com `docker-compose up -d`
- [ ] Migrations rodadas automaticamente
- [ ] Superuser criado
- [ ] HTTPS funcionando (curl -I https://seu-dominio.com)
- [ ] Login funcionando em https://seu-dominio.com
- [ ] Kanban carregando dados
- [ ] Backups configurados

---

## Support

Para problemas ou dúvidas:
1. Verificar logs: `docker-compose logs -f web`
2. Verificar `.env`: Valores estão corretos?
3. Verificar domínio: `nslookup seu-dominio.com`
4. Abrir issue no GitHub: https://github.com/alexconectado/mini-crm/issues

---

**Versão:** v1.0.0  
**Última atualização:** 6 de janeiro de 2026
