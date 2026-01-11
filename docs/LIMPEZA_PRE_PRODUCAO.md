# Limpeza de Dados - Pré-Produção

Este documento descreve como limpar todos os dados de teste antes de colocar o Mini-CRM em produção.

## ⚠️ ATENÇÃO

- Esta operação **NÃO pode ser desfeita**
- Todos os **registros comerciais** serão apagados
- Todos os **históricos de contato** serão apagados
- **Usuários e grupos** serão mantidos

## Métodos de Limpeza

### Método 1: Comando Django (Recomendado)

Dentro do container ou ambiente virtual:

```bash
python manage.py limpar_leads
```

Para forçar sem confirmação (cuidado!):

```bash
python manage.py limpar_leads --force
```

### Método 2: Script Python

```bash
python limpar_leads.py
```

### Método 3: Via Docker

Se estiver usando Docker:

```bash
docker exec -it crm_web_zandomax python manage.py limpar_leads
```

## O que é mantido

✅ Usuários
✅ Grupos e permissões
✅ Configurações do sistema
✅ Templates e views

## O que é removido

❌ Todos os registros comerciais (leads)
❌ Todos os históricos de contato
❌ Dados de teste

## Checklist Pré-Produção

- [ ] Fazer backup do banco de dados
- [ ] Verificar configurações em `config/settings.py`
- [ ] Executar `python manage.py limpar_leads`
- [ ] Confirmar que `DEBUG = False` em produção
- [ ] Verificar `ALLOWED_HOSTS` configurado
- [ ] Testar criação de novo lead
- [ ] Verificar métricas zeradas

## Backup Antes da Limpeza

Se estiver usando PostgreSQL:

```bash
# Backup
pg_dump -U postgres -h localhost crm_db > backup_antes_producao.sql

# Restaurar (se necessário)
psql -U postgres -h localhost crm_db < backup_antes_producao.sql
```

Se estiver usando SQLite:

```bash
# Backup
cp db.sqlite3 db.sqlite3.backup

# Restaurar (se necessário)
cp db.sqlite3.backup db.sqlite3
```

## Após a Limpeza

1. Acesse o Kanban e verifique que está vazio
2. Teste criar um novo lead
3. Verifique as métricas (devem estar zeradas)
4. Pronto para produção! 🚀
