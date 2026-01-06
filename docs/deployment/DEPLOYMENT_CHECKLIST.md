# 🚀 DEPLOYMENT CHECKLIST - Mini CRM v1.0.0

**Objetivo:** Expor aplicação em subdomínio público com segurança

---

## 📋 PRÉ-DEPLOYMENT (ANTES DE QUALQUER DEPLOY)

### Segurança Base
- [ ] SECRET_KEY foi regenerada (não usar .env.example)
- [ ] DEBUG foi setado como False
- [ ] ALLOWED_HOSTS contém domínio real
- [ ] .env foi criado e NÃO foi commitado
- [ ] .gitignore inclui .env

### Dependências
- [ ] `pip install -r requirements.txt` executado
- [ ] Todas as dependências instaladas sem erros
- [ ] Python 3.10+ confirmado
- [ ] PostgreSQL 12+ instalado (ou usar Docker)

### Testes
- [ ] `python manage.py check` passou
- [ ] `python manage.py check --deploy` revisto
- [ ] Página inicial carrega sem erros
- [ ] Login funciona
- [ ] Kanban carrega dados
- [ ] CSV import valida

---

## 🐳 DEPLOYMENT COM DOCKER (RECOMENDADO)

### Setup
- [ ] Docker instalado (`docker --version`)
- [ ] Docker Compose instalado (`docker-compose --version`)
- [ ] Arquivo .env criado com valores reais
  - [ ] DJANGO_SECRET_KEY nova
  - [ ] DEBUG=False
  - [ ] ALLOWED_HOSTS configurado
  - [ ] DB_PASSWORD alterada

### Build & Run
- [ ] Build da imagem: `docker-compose build`
- [ ] Containers iniciados: `docker-compose up -d`
- [ ] Logs verificados: `docker-compose logs -f web`
- [ ] Health check passou: `curl http://localhost:8000`
- [ ] Migrations rodaram automaticamente
- [ ] Static files coletados

### Acesso
- [ ] HTTP funciona: `http://localhost:80`
- [ ] Redireciona para HTTPS (se SSL configurado)
- [ ] Login funciona
- [ ] Dados aparecem corretamente

---

## 🔐 SSL/HTTPS CONFIGURATION

### Let's Encrypt (Recomendado)
- [ ] `certbot` instalado
- [ ] Certificado obtido: `certbot certonly --standalone -d seu-dominio.com`
- [ ] Paths em nginx.conf atualizados:
  - `/etc/letsencrypt/live/seu-dominio.com/fullchain.pem`
  - `/etc/letsencrypt/live/seu-dominio.com/privkey.pem`
- [ ] Auto-renewal configurado: `certbot renew --dry-run`
- [ ] HTTPS funciona: `https://seu-dominio.com`

### Headers de Segurança
- [ ] HSTS header ativado
- [ ] X-Frame-Options ativado
- [ ] X-Content-Type-Options ativado
- [ ] CSP header testado

---

## 🗄️ DATABASE CONFIGURATION

### PostgreSQL (Produção)
- [ ] PostgreSQL 12+ instalado
- [ ] Database criado: `createdb crm_db`
- [ ] User criado: `createuser crm_user`
- [ ] Credenciais em .env configuradas
- [ ] Migração rodou: `python manage.py migrate`
- [ ] Dados iniciais criados (superuser, grupos)

### Backup
- [ ] Backup automático agendado
- [ ] Teste de restore realizado
- [ ] Retenção de backups definida (30 dias)
- [ ] Backup em local seguro (S3, external HD)

### Performance
- [ ] Índices criados (já no schema)
- [ ] Query optimization testada
- [ ] Database logging habilitado (para monitoring)

---

## ⚡ PERFORMANCE & CACHING

### Redis (Opcional mas Recomendado)
- [ ] Redis instalado (`redis-server`)
- [ ] Redis URL em .env configurada
- [ ] Cache funcionando (testar com `redis-cli`)
- [ ] TTL configurado (5 minutos)

### Gunicorn (App Server)
- [ ] Gunicorn instalado
- [ ] gunicorn.conf.py revisado
- [ ] Workers configurados (CPU cores * 2 + 1)
- [ ] Timeout setado (30s)
- [ ] Logging habilitado

### Nginx (Reverse Proxy)
- [ ] Nginx instalado
- [ ] nginx.conf revisado
- [ ] Gzip compression habilitado
- [ ] Rate limiting configurado
- [ ] Static files serving otimizado

---

## 📊 MONITORAMENTO & LOGGING

### Logging
- [ ] Logging estruturado configurado
- [ ] Arquivo de log criado: `/var/log/crm.log`
- [ ] Log rotation configurado (logrotate)
- [ ] Senha/token nunca aparecem em logs

### Monitoring
- [ ] Health check endpoint testado
- [ ] Uptime monitor configurado (Uptime Robot)
- [ ] Error tracking configurado (Sentry, opcional)
- [ ] Performance monitoring (New Relic, DataDog, opcional)

### Alertas
- [ ] CPU > 80% → alerta
- [ ] Memória > 85% → alerta
- [ ] Disk > 90% → alerta
- [ ] Resposta > 2s → alerta
- [ ] Erro 5xx → alerta

---

## 🛡️ SEGURANÇA FINAL

### Firewall
- [ ] Porta 22 (SSH) restrita a IPs conhecidos
- [ ] Porta 80 (HTTP) aberta (redireciona para 443)
- [ ] Porta 443 (HTTPS) aberta
- [ ] Outras portas fechadas

### Acesso
- [ ] SSH key-based login (não password)
- [ ] Sudo sem password desativado
- [ ] Fail2ban ativado
- [ ] Rate limiting no Nginx ativado

### Credenciais
- [ ] Nenhum hardcoded no código
- [ ] Todos em .env ou environment variables
- [ ] Secrets manager em produção (recomendado)
- [ ] Rotação de senhas agendada

### Data
- [ ] Backups criptografados
- [ ] LGPD/GDPR considerado
- [ ] Retenção de dados definida
- [ ] Right to be forgotten implementado

---

## 🧪 TESTES PRÉ-PRODUÇÃO

### Funcionalidade
- [ ] Kanban carrega dados
- [ ] Filtros funcionam (Dia/Semana/Mês)
- [ ] CSV import valida
- [ ] Soft delete funciona
- [ ] Permissões funcionam

### Segurança
- [ ] Nenhum SQL injection detectado
- [ ] Nenhum XSS detectado
- [ ] CSRF token presente
- [ ] Session hijacking impossível
- [ ] Rate limiting funciona

### Performance
- [ ] Página carrega < 2s
- [ ] API responde < 500ms
- [ ] Sem memory leaks
- [ ] Cache funciona

### Escalabilidade
- [ ] Pode lidar com 1000+ simultâneos (teste de carga)
- [ ] Database não fica bottleneck
- [ ] Gunicorn worker responde bem
- [ ] Redis cache funciona

---

## 📝 DOCUMENTAÇÃO & COMUNICAÇÃO

### Documentação
- [ ] README.md atualizado
- [ ] API documentation criada (se aplicável)
- [ ] Runbooks criados (como restaurar, etc)
- [ ] Troubleshooting guide criado

### Comunicação
- [ ] Usuários notificados da data de launch
- [ ] Suporte preparado (FAQ, helpdesk)
- [ ] On-call rotation definido
- [ ] Escalation path documentado

### Rollback
- [ ] Plano de rollback criado
- [ ] Versão anterior testada para rollback
- [ ] Backup anterior validado
- [ ] Tempo estimado de rollback < 5 minutos

---

## 🚀 GO LIVE

### Dia do Deploy
- [ ] Backup pré-deploy realizado
- [ ] Team em standby durante deploy
- [ ] Monitoramento ativado
- [ ] Smoke tests executados pós-deploy

### Pós-Deploy (Primeira Hora)
- [ ] Health check passa
- [ ] Logs sem erros críticos
- [ ] Usuários conseguem acessar
- [ ] Performance normal

### Pós-Deploy (Primeiro Dia)
- [ ] Nenhum alerta crítico
- [ ] Backups rodando
- [ ] Logs coletando corretamente
- [ ] Usuários reportando feedback

### Pós-Deploy (Primeira Semana)
- [ ] Monitoramento estável
- [ ] Nenhuma vulnerabilidade crítica encontrada
- [ ] Performance consistente
- [ ] Retroalimentação de usuários

---

## 📊 CHECKLIST FINAL

| Item | Status | Responsável |
|------|--------|-------------|
| Segurança | [ ] | |
| Database | [ ] | |
| Cache | [ ] | |
| Logs | [ ] | |
| Monitoring | [ ] | |
| Testes | [ ] | |
| Documentação | [ ] | |
| Comunicação | [ ] | |
| Deploy | [ ] | |

---

## 🎯 SUCESSO SIGNIFICA:

✅ Aplicação respondendo em produção  
✅ Nenhum alerta crítico em 24h  
✅ Usuários conseguem fazer login  
✅ Dados carregam corretamente  
✅ Backups rodando  
✅ Logs coletando  
✅ Monitoramento ativado  

---

**Versão:** 1.0.0  
**Data:** 6 de janeiro de 2026

Boa sorte com o deployment! 🚀

