# 📦 Versionamento Mini CRM Zandomax

## v2.0.0 - Phase 2 Completo (2026-01-10)

### 🎯 Status: PRODUÇÃO ESTÁVEL

**Commit Principal:** `b824903`

### ✅ Implementação Completa

#### PASSO 1: Campo `status_cliente` (commit acb78b5)
- ✅ Migration 0007 aplicada e testada
- ✅ Campo com choices: novo, ativo, inativo
- ✅ Default: 'novo'
- ✅ Sem quebra de compatibilidade

#### PASSO 2: Cadastro Manual (commit 34a51c3)
- ✅ Select com 3 opções de status
- ✅ Integrado no formulário de criação rápida
- ✅ Validação backend

#### PASSO 3: Dinâmica de Resultados (commit d2db350)
- ✅ 4 opções por status_cliente em "Conta para Contato"
- ✅ Novo: contato_responsavel, responsavel_indisponivel, nao_atendeu, numero_invalido
- ✅ Ativo: contato_responsavel, em_negociacao, aceitou, aguardando_resposta
- ✅ Inativo: contato_responsavel, sem_interesse, sem_perfil, numero_invalido

#### PASSO 4: Importação Excel (commit b99ff58)
- ✅ Substituído CSV por Excel (openpyxl)
- ✅ Seletor global de status_cliente
- ✅ Validação de arquivo (5MB max, .xlsx/.xls)
- ✅ Tratamento de erros por linha

#### Refinamentos Visuais
- Badge "Perfil do Cliente" na página de detalhes (commit b824903)
- Valores: CLIENTE NOVO (azul), CLIENTE ATIVO (verde), CLIENTE INATIVO (cinza)
- Removido do card para não poluir Kanban

### 🔧 Configurações

**Banco de Dados:**
- PostgreSQL 15
- 7 migrations aplicadas
- Índices de performance em place

**Django:**
- Versão 6.0
- Validação em RESULTADO_POR_STATUS_CLIENTE (rules.py)
- Pipeline automático funcional

**Frontend:**
- Alpine.js 3.x
- Tailwind CSS (CDN)
- Compatível com navegadores modernos

### 📊 Métricas

- **Opções dinâmicas:** 3 perfis × 4 resultados = 12 combinações
- **Auto-arquivamento:** 2 tentativas de retorno
- **Limite Kanban:** 8 cards por coluna
- **Status visíveis:** 4 colunas (exclu ai CONTA_ATIVA e ARQUIVADA)

### 🔒 Restrições Mantidas

- ✅ Pipeline não alterado
- ✅ Funil intacto (6 estágios)
- ✅ Sem novo estágio criado
- ✅ Migrations reversíveis
- ✅ Sem mudança em outros módulos

### 🚀 Deploy

```bash
# Copiar para container
docker cp /opt/crm/crm/views.py crm_web_zandomax:/app/crm/views.py
docker cp /opt/crm/crm/models.py crm_web_zandomax:/app/crm/models.py
docker cp /opt/crm/crm/templates/ crm_web_zandomax:/app/crm/templates/
docker cp /opt/crm/requirements.txt crm_web_zandomax:/app/requirements.txt

# Aplicar migrations
docker exec crm_web_zandomax python manage.py migrate

# Reinicar
docker restart crm_web_zandomax
```

### 📝 Checklist Pré-Produção

- [x] Migrations testadas
- [x] Backend validado
- [x] Frontend renderiza corretamente
- [x] Auto-arquivamento funciona
- [x] Importação Excel processada
- [x] Histórico persistido
- [x] Sem regressões detectadas
- [x] Versioning aplicado

### 🔄 Próximas Fases

**Phase 3 (Futuro):**
- Simplificação da coluna "Conta para Contato" (prompt canônico)
- Remoção de opções redundantes
- Próximo passo fixo ("Tentar contato novamente")

---

## v1.0.0 - Initial Release

**Commit:** `a9ef291`

- Kanban com 6 estágios
- Gestão de usuários
- Dashboard de métricas
- Importação CSV (substituída em v2.0.0)
- Auto-arquivamento básico

---

## Roadmap Futuro

### Phase 3: Simplificação Coluna "Conta para Contato"
- [ ] Resultado + 4 opções fechadas
- [ ] Próximo passo fixo (não select)
- [ ] Avanço automático por resultado
- [ ] Observações mantidas

### Phase 4: Integrações
- [ ] Webhook com Winthor
- [ ] Sincronização bidirecional
- [ ] API REST pública

### Phase 5: Analytics
- [ ] Dashboard executivo
- [ ] Previsões via ML
- [ ] Relatórios customizados

---

**Última atualização:** 2026-01-10  
**Ambiente:** Produção Estável  
**Status:** ✅ Auditado e Versionado
