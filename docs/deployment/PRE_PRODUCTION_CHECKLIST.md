# 📋 Checklist Pré-Produção - Mini CRM

**Data de início:** 6 de janeiro de 2026  
**Ambiente alvo:** Subdomínio público  
**Status:** ⏳ EM PROGRESSO

---

## 🔴 CRÍTICO - FAZER ANTES DE EXPOR

### Segurança Base
- [x] Gerar nova SECRET_KEY
- [x] DEBUG = False em .env produção
- [x] ALLOWED_HOSTS configurado
- [x] .env.example criado
- [x] python-dotenv instalado
- [ ] **TODO**: HTTPS/SSL certificate (Let's Encrypt)
- [ ] **TODO**: Testar SECURE_SSL_REDIRECT
- [ ] **TODO**: Validar que HTTPS força redirecionamento

### Banco de Dados
- [ ] **TODO**: Migrar para PostgreSQL (recomendado)
- [ ] **TODO**: Backup strategy definida
- [ ] **TODO**: Database password configurada
- [ ] **TODO**: Permissões de arquivo DB restringidas

### API Security
- [x] Validação de acesso em `desempenho_vendedor_api`
- [x] Validação de arquivo CSV (tamanho, extensão, MIME)
- [ ] **TODO**: Rate limiting ativado (django-ratelimit)
- [ ] **TODO**: Testar que não pode ver dados de outro vendedor

### Secrets Management
- [x] Arquivo .env criado
- [ ] **TODO**: .env não commitado (.gitignore)
- [ ] **TODO**: Secrets armazenados de forma segura (não em plain text)
- [ ] **TODO**: Variáveis de ambiente configuradas em deployment

### Dados Sensíveis
- [ ] **TODO**: Remover dados de teste do banco
- [ ] **TODO**: Resetar senhas de teste
- [ ] **TODO**: Verificar logs não expostos publicamente

---

## 🟠 ALTO - FAZER ANTES DA PRIMEIRA SEMANA

### Performance
- [x] Cache configurado (LocMemCache)
- [ ] **TODO**: Redis instalado e configurado
- [ ] **TODO**: Testes de carga
- [ ] **TODO**: Monitoramento de queries lentas

### Autenticação & Autorização
- [ ] **TODO**: Session timeout testado (1 hora)
- [ ] **TODO**: Logout limpa todos os dados de sessão
- [ ] **TODO**: Grupos de usuários testados (Admin, Comercial)
- [ ] **TODO**: HTTPOnly cookies ativados (já no settings)

### Logging & Auditoria
- [ ] **TODO**: Logging configurado (arquivo ou serviço)
- [ ] **TODO**: Ações sensíveis registradas (login, mudanças, exclusões)
- [ ] **TODO**: Logs não expostos publicamente
- [ ] **TODO**: Log rotation configurado

### Monitoramento
- [ ] **TODO**: Health check endpoint criado
- [ ] **TODO**: Alertas configurados (uptime, errors)
- [ ] **TODO**: Backups automáticos agendados

---

## 🟡 MÉDIO - FAZER ANTES DO MÊS 1

### Validação de Input
- [x] CSV validation (tamanho, tipo, extensão)
- [ ] **TODO**: Validação regex para telefone
- [ ] **TODO**: Sanitização de strings longas
- [ ] **TODO**: Teste de XSS (entradas maliciosas)

### Headers de Segurança
- [x] X-Frame-Options configurado
- [x] X-Content-Type-Options configurado
- [x] XSS Protection ativado
- [ ] **TODO**: Content-Security-Policy testado
- [ ] **TODO**: Verificar Headers com https://securityheaders.com

### Compliance
- [ ] **TODO**: Privacidade de dados (LGPD/GDPR)
- [ ] **TODO**: Retenção de dados definida
- [ ] **TODO**: Right to be forgotten implementado
- [ ] **TODO**: Termos de serviço/Privacidade criados

---

## 🟢 BAIXO - FAZER ANTES DO MÊS 3

### Code Quality
- [ ] **TODO**: Testes unitários escritos
- [ ] **TODO**: Testes de integração
- [ ] **TODO**: Coverage > 80%
- [ ] **TODO**: Code review realizado

### Escalabilidade
- [ ] **TODO**: Testes de carga (1000+ usuários simultâneos)
- [ ] **TODO**: Load balancing configurado (se necessário)
- [ ] **TODO**: Database replication (se necessário)
- [ ] **TODO**: CDN para assets estáticos

### Documentação
- [x] README.md criado
- [x] SETUP.md criado
- [x] SECURITY_AUDIT.md criado
- [ ] **TODO**: API documentation (Swagger/OpenAPI)
- [ ] **TODO**: Runbooks para troubleshooting

---

## 📝 Testes Obrigatórios

### Funcionalidade
- [ ] **TODO**: Kanban cards mostram dados corretos
- [ ] **TODO**: Filtros por período funcionam (Dia/Semana/Mês)
- [ ] **TODO**: CSV import valida corretamente
- [ ] **TODO**: Soft delete (arquivar) funciona
- [ ] **TODO**: Permissões por grupo funcionam

### Segurança
- [ ] **TODO**: Nenhum SQL injection detectado
- [ ] **TODO**: Nenhum XSS detectado
- [ ] **TODO**: Nenhum CSRF detectado
- [ ] **TODO**: Session hijacking não é possível
- [ ] **TODO**: Força brute é limitada (rate limiting)
- [ ] **TODO**: Usuário não pode ver dados de outro usuário

### Performance
- [ ] **TODO**: Página principal carrega em < 2s
- [ ] **TODO**: API responde em < 500ms
- [ ] **TODO**: Database queries otimizadas
- [ ] **TODO**: Sem memory leaks

---

## 🔍 Verificação Final (Release Checklist)

Antes de expor ao público:

- [ ] Revisar SECURITY_AUDIT.md
- [ ] Rodar `python manage.py check --deploy`
- [ ] Testar HTTPS em staging
- [ ] Backup inicial do banco
- [ ] Comunicado aos usuários pronto
- [ ] Plano de rollback documentado
- [ ] Observabilidade testada
- [ ] Escalonamento para on-call definido

---

## 📞 Contatos de Emergência

- **Security issues**: security@seu-email.com
- **On-call**: [número/slack]
- **Escalation**: [gerente]

---

## 📊 Progresso

```
Crítico:    30% ████░░░░░░░░░░░░░░░░░░ (3/10)
Alto:       0%  ░░░░░░░░░░░░░░░░░░░░░░ (0/6)
Médio:      20% ██░░░░░░░░░░░░░░░░░░░░ (1/5)
Baixo:      40% ████░░░░░░░░░░░░░░░░░░ (2/5)

TOTAL:      18% ██░░░░░░░░░░░░░░░░░░░░ (6/33 items)
```

---

## 🚀 Deployment Steps

1. [ ] Merge de todas as mudanças em `main`
2. [ ] Tag de versão criada: `v1.0.0`
3. [ ] Build de docker image (se usando docker)
4. [ ] Deploy em staging
5. [ ] Testes em staging passando
6. [ ] Backup de produção
7. [ ] Deploy em produção
8. [ ] Smoke tests passando
9. [ ] Monitoramento ativado
10. [ ] Comunicação de release enviada

---

**Última atualização:** 6 de janeiro de 2026  
**Responsável:** [Seu nome]
