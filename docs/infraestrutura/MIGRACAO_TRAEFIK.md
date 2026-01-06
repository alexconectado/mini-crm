# 🚀 MIGRAÇÃO PARA TRAEFIK - GUIA PRÁTICO

**Objetivo:** Migrar de Nginx para Traefik (muito mais simples!)  
**Tempo:** ~30 minutos  
**Dificuldade:** Fácil  
**Status:** Recomendado

---

## ✅ POR QUE MIGRAR?

Você usa Traefik na VPS. Usar `docker-compose.traefik.yml`:

| Benefício | Antes (Nginx) | Depois (Traefik) |
|-----------|---------------|-----------------|
| SSL automático | ❌ Script | ✅ Nativo |
| SSL renewal | ❌ Cron job | ✅ Automático |
| Rate limiting | ❌ Manual | ✅ Labels |
| Config file | ❌ 150 linhas | ✅ 10 linhas |
| Dashboard | ❌ Não | ✅ Sim |
| Tempo setup | ❌ 45 min | ✅ 5 min |

---

## 🎯 PASSO A PASSO

### Passo 1: Parar containers antigos
```bash
cd /home/lekao/crm

# Parar Nginx
docker-compose down

# Ou se tiver outro Traefik rodando na VPS
docker stop mini-crm-traefik  # Se existir
```

### Passo 2: Configurar .env
```bash
# Editar .env
nano .env

# Adicionar/Atualizar:
ALLOWED_HOSTS=crm.seudominio.com,www.crm.seudominio.com
LETSENCRYPT_EMAIL=seu-email@gmail.com
DEBUG=False
DJANGO_SECRET_KEY=sua-nova-chave
DB_PASSWORD=senha-forte
USE_POSTGRES=True
```

### Passo 3: Iniciar com Traefik
```bash
# Use arquivo Traefik
docker-compose -f docker-compose.traefik.yml up -d

# Acompanhe logs
docker-compose -f docker-compose.traefik.yml logs -f web
```

### Passo 4: Verificar
```bash
# Ver containers
docker-compose -f docker-compose.traefik.yml ps

# Ver dashboard Traefik
# Acesse: http://localhost:8080

# Testar HTTPS (após certificado ser gerado)
curl -I https://crm.seudominio.com

# Ver logs do Traefik
docker-compose -f docker-compose.traefik.yml logs traefik | grep -i letsencrypt
```

### Passo 5: Limpar
```bash
# Remover arquivo Nginx (não precisa mais)
rm nginx.conf

# Backup do docker-compose.yml antigo (opcional)
mv docker-compose.yml docker-compose.nginx.yml.backup
```

---

## ⏱️ TIMELINE

| Tempo | Ação |
|-------|------|
| 0 min | Começar |
| 2 min | Parar containers antigos |
| 5 min | Configurar .env |
| 10 min | Iniciar Traefik |
| 15 min | Aguardar certificado SSL (Let's Encrypt) |
| 25 min | Verificar tudo |
| 30 min | Limpar arquivos antigos |

---

## 🔐 SEGURANÇA AUTOMÁTICA

Traefik já cuida de:

```yaml
✅ HTTP → HTTPS redirect
✅ HSTS (força HTTPS)
✅ X-Frame-Options (clickjacking)
✅ X-Content-Type-Options (MIME sniffing)
✅ Rate limiting (100 req/s)
✅ Gzip compression
✅ SSL/TLS moderno
✅ Certificado Let's Encrypt automático
```

Tudo configurado em **labels Docker**! 🎯

---

## 📊 DASHBOARD TRAEFIK

Acesse: **http://localhost:8080**

Você verá:
- ✅ Routers HTTP/HTTPS
- ✅ Serviços rodando
- ✅ Middlewares ativas
- ✅ Status SSL
- ✅ Estatísticas

---

## 🐛 TROUBLESHOOTING

### "SSL não está sendo gerado"
```bash
# Ver logs
docker-compose -f docker-compose.traefik.yml logs traefik | grep acme

# Verificar arquivo ACME
ls -la letsencrypt/acme.json

# Se vazio, tentar forçar
docker-compose -f docker-compose.traefik.yml restart traefik
```

### "Certificado não renova"
```bash
# Traefik renova automaticamente 30 dias antes
# Verificar status
docker-compose -f docker-compose.traefik.yml logs traefik | tail -20
```

### "Rate limiting muito agressivo"
```bash
# Editar docker-compose.traefik.yml
# Linha com "ratelimit.average=100" → mudar para 200 ou 500
docker-compose -f docker-compose.traefik.yml up -d  # Reiniciar
```

### "DNS não resolvendo"
```bash
# Verificar
nslookup crm.seudominio.com
dig crm.seudominio.com

# Aguardar propagação (até 48h)
```

---

## ✨ ANTES vs DEPOIS

### ❌ Antes (Nginx)
```
1. Manter nginx.conf (150 linhas)
2. Configurar Let's Encrypt manualmente
3. Renew via cron job
4. Rate limiting via módulo
5. Headers de segurança manual
6. Sem dashboard
7. Recarregar Nginx quando muda config
8. 30-45 minutos de setup
```

### ✅ Depois (Traefik)
```
1. Nenhum arquivo de config (tudo em labels)
2. Let's Encrypt automático
3. Renew automático
4. Rate limiting via label
5. Headers automáticos
6. Dashboard em http://8080
7. Auto-discovery (sem recarregar)
8. 5 minutos de setup
9. Dashboard para monitorar tudo
```

---

## 🎯 CHECKLIST MIGRAÇÃO

```
[ ] Backup do .env
[ ] Parar containers Nginx
[ ] Configurar .env (ALLOWED_HOSTS, LETSENCRYPT_EMAIL)
[ ] Iniciar docker-compose.traefik.yml
[ ] Aguardar SSL (2-5 min)
[ ] Verificar em https://seu-dominio.com
[ ] Testar dashboard em http://localhost:8080
[ ] Deletar nginx.conf
[ ] Backup docker-compose.yml antigo
[ ] Documentar mudança
[ ] Celebrar! 🎉
```

---

## 📝 CONFIGURAÇÃO MÍNIMA

### .env (essencial)
```bash
ALLOWED_HOSTS=crm.seu-dominio.com
LETSENCRYPT_EMAIL=seu-email@gmail.com
DJANGO_SECRET_KEY=chave-gerada-aleatoria
DEBUG=False
DB_PASSWORD=senha-postgresql
```

### Executar
```bash
docker-compose -f docker-compose.traefik.yml up -d
```

**Pronto! Tudo automático a partir daqui.** ✨

---

## 🚀 NA VPS (Produção)

### 1. Clone/Pull código
```bash
cd /opt/mini-crm
git pull origin main
```

### 2. Configure .env
```bash
cp .env.example .env
nano .env  # Editar valores reais
```

### 3. Execute
```bash
docker-compose -f docker-compose.traefik.yml up -d
```

### 4. Monitore
```bash
# Ver logs
docker-compose -f docker-compose.traefik.yml logs -f web

# Ver status
docker-compose -f docker-compose.traefik.yml ps

# Dashboard
# http://sua-vps:8080
```

### 5. Verifique SSL
```bash
# Deve retornar 200 e certificado válido
curl -I https://crm.seu-dominio.com

# Ver data de expiração
curl -I https://crm.seu-dominio.com 2>&1 | grep -i "expire"
```

---

## 💡 DICAS

1. **Usar Traefik já existente na VPS?**
   - Se já tiver Traefik rodando, pode integrar o Mini CRM
   - Use network compartilhada: `networks: shared_traefik`

2. **Múltiplos domínios?**
   ```bash
   ALLOWED_HOSTS=crm.seudominio.com,app.seudominio.com,www.crm.seudominio.com
   ```

3. **Email para renovação SSL?**
   ```bash
   LETSENCRYPT_EMAIL=seu-email@gmail.com
   ```

4. **Rate limiting customizado?**
   - Edit `docker-compose.traefik.yml`
   - Mude linha: `average=100` → `average=500`

---

## 🎯 CONCLUSÃO

Migrar para Traefik é:
- ✅ Simples (30 minutos)
- ✅ Seguro (automático)
- ✅ Profissional (dashboard)
- ✅ Escalável (label-based)

**Recomendação:** Faça agora! 🚀

---

## 📞 DÚVIDAS?

Consulte:
- `docs/infraestrutura/TRAEFIK.md` - Guia completo
- `docker-compose.traefik.yml` - Configuração
- `docs/SETUP.md` - Troubleshooting

---

**Versão:** 1.0.0  
**Status:** ✅ Pronto para migração  
**Data:** 6 de janeiro de 2026

