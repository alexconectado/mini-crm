# 📋 CONFIGURAÇÃO DO FUNIL — DOCUMENTAÇÃO ADMIN

## Visão Geral

A página de **Configuração do Funil** permite que administradores personalizem:
- ✅ Quais **opções de resultado** aparecem no formulário
- ✅ Quais **próximos passos** são sugeridos
- ✅ Tudo por **coluna do funil** e **status do cliente**

### Acessar

**URL:** `https://crm.zandomax.com.br/crm/admin/configuracao-funil/`

**Permissão:** `is_superuser=True` (apenas admin)

---

## 🎯 O Que Muda e O Que NÃO Muda

### ✅ MUDA com a Configuração

- O que aparece no **select de Resultado** no formulário
- O que aparece no **select de Próximo Passo**
- A **ordem** de exibição das opções
- Se uma opção está **ativa** ou **inativa**

### ❌ NÃO MUDA (INTOCÁVEL)

- ❌ Lógica de **avanço de card** (resolve_next_stage)
- ❌ Pipeline automático (PIPELINE_RULES)
- ❌ Enum StatusPipelineChoices
- ❌ Histórico já registrado
- ❌ Validação de resultado no backend

**⚠️ Lógica de decisão NÃO usa a config. Continua usando PIPELINE_RULES.**

---

## 🏗️ Estrutura de Dados

### Modelos

#### FunilResultadoConfig
```python
coluna_pipeline  # ex: 'conta_para_contato'
status_cliente   # ex: 'novo'
key              # ex: 'contato_responsavel' (slug)
label            # ex: 'Falou com responsável' (UI)
ativo            # boolean (aparece ou não?)
ordem            # int (0-9: ordem de exibição)
```

#### FunilProximoPassoConfig
```python
coluna_pipeline  # ex: 'conta_para_contato'
status_cliente   # ex: 'novo'
label            # ex: 'Tentar contato novamente'
ativo            # boolean
ordem            # int
```

### Combinações Pré-Configuradas

**Cliente NOVO:**
- Conta para Contato: 4 resultados + 1 próximo passo

**Cliente ATIVO:**
- Conta para Contato: 4 resultados + 1 próximo passo

**Cliente INATIVO:**
- Conta para Contato: 4 resultados + 1 próximo passo

**Total:** 12 combinações de resultados iniciais

---

## 🖥️ Interface Web

### Layout

```
┌─ Abas de Coluna ────────────────────────────┐
│ [Conta para Contato] [Contato Feito] [...]  │
└─────────────────────────────────────────────┘

┌─ Grid 3 Colunas: Status do Cliente ─────────┐
│ ┌── NOVO ────┐ ┌── ATIVO ──┐ ┌── INATIVO ──┐│
│ │ Resultados │ │ Resultados│ │ Resultados │ │
│ │ - [ Ativo] │ │ - [ Ativo] │ │ - [ Ativo] │ │
│ │ - [Inativo]│ │ - [Inativo]│ │ - [Inativo]│ │
│ │            │ │            │ │            │ │
│ │ Próx Passos│ │ Próx Passos│ │ Próx Passos│ │
│ │ - [ Ativo] │ │ - [ Ativo] │ │ - [ Ativo] │ │
│ └────────────┘ └────────────┘ └────────────┘│
└─────────────────────────────────────────────┘
```

### Ações Disponíveis

| Ação | Endpoint | Efeito |
|------|----------|--------|
| Toggle Resultado | POST `/api/admin/toggle-resultado-ativo/{id}/` | Ativa/desativa resultado |
| Toggle Próximo Passo | POST `/api/admin/toggle-passo-ativo/{id}/` | Ativa/desativa próximo passo |
| Editar via Admin | Django Admin | Muda label, ordem, key |

### Cache

- **TTL:** 1 hora
- **Invalidação:** Automática ao toggle via API
- **Sem cache:** Ao acessar via Django Admin

---

## 🔄 Fluxo de Dados

### Carregar Resultados (registrar_contato)

```
1. Frontend acessa /registrar-contato/{id}/
2. Backend chama obter_resultados_config()
3. Busca em FunilResultadoConfig com filtros:
   - coluna_pipeline = coluna_atual
   - status_cliente = status_do_registro
   - ativo = True
4. Ordena por: ordem, label
5. Fallback: Se vazio, usa RESULTADO_POR_STATUS_CLIENTE (hardcoded)
6. Retorna JSON para Alpine.js
```

### Salvar Resultado

```
1. Vendedor seleciona resultado
2. POST /registrar-contato/{id}/
3. Backend valida:
   - resultado_code in valid_resultado_keys (de config)
   - Não aceita resultado inativo
4. Gera próximo_estágio via resolve_next_stage()
5. Salva em ContatoHistorico
6. Move card se necessário
```

---

## 🛠️ Casos de Uso

### Caso 1: Desativar Opção

**Objetivo:** "Remover 'Número inválido' para clientes NOVO"

**Ação:**
1. Ir para Configuração → Conta para Contato
2. Card "Cliente Novo"
3. Clicar botão "✕ Inativo" ao lado de "Número inválido"
4. ✅ Pronto! Deixa de aparecer no select

**Efeito:**
- Novo registro NOVO não verá "Número inválido"
- Registros antigos continuam com histórico intacto
- Validação backend rejeita se enviado diretamente

### Caso 2: Reordenar Opções

**Objetivo:** "Colocar 'Falou com responsável' por último"

**Ação:**
1. Ir para Django Admin → FunilResultadoConfig
2. Filtrar: coluna=conta_para_contato, status=novo
3. Editar "Falou com responsável"
4. Mudar "ordem" de 1 para 4
5. ✅ Salvar

**Efeito:**
- Select mostra em ordem: 2, 3, 4 (antiga 1)

### Caso 3: Adicionar Opção Nova

**Objetivo:** "Adicionar 'Ligou do escritório' para clientes NOVO"

**Ação:**
1. Django Admin → FunilResultadoConfig → Adicionar
2. Preencher:
   - Coluna: Conta para Contato
   - Status: novo
   - Key: ligou_escritorio
   - Label: "Ligou do escritório"
   - Ordem: 5
   - Ativo: ✓
3. Salvar

**⚠️ IMPORTANTE:** Key deve existir em `RESULT_LABELS` ou lógica quebra

---

## 🔒 Segurança

### Proteções

✅ **is_superuser:** Acesso restrito  
✅ **CSRF token:** Obrigatório em POST  
✅ **Sem exclusão física:** Usa ativo=False  
✅ **Histórico preservado:** Não afeta ContatoHistorico  
✅ **Fallback seguro:** Se config vazia, volta ao hardcoded  

### Riscos Mitigados

| Risco | Proteção |
|-------|----------|
| Admin remove tudo | Config vazia → fallback automático |
| Admin muda key inválida | Validação backend rejeita |
| Admin quebra pipeline | Pipeline_RULES não muda |
| Exclusão acidental | Soft delete (ativo=False) |

---

## 📊 Seed Inicial

Executar seed de dados iniciais:

```bash
docker exec crm_web_zandomax python manage.py seed_funil_config
```

Popula:
- ✅ 4 resultados × 3 status = 12 configs
- ✅ 1 próximo passo × 3 status = 3 configs
- ✅ Todos ativos por padrão

---

## 🔧 Troubleshooting

### "Select vazio no formulário"

**Causas:**
1. Todas as opções estão `ativo=False`
2. Nenhuma config existe para esse status

**Solução:**
1. Checar em Admin → FunilResultadoConfig
2. Filtrar por coluna e status
3. Ativar pelo menos uma opção

### "Resultado rejeitado (validação backend)"

**Causas:**
1. Key do resultado não existe em FunilResultadoConfig
2. Está `ativo=False`

**Solução:**
1. Adicionar em Admin ou executar seed
2. Ativar via toggle ou Admin

### "Cache antigo aparecendo"

**Causas:**
1. TTL de 1 hora

**Solução:**
1. Esperar 1h OU
2. Reiniciar container
3. Usar Django shell:
   ```bash
   python manage.py shell
   from crm.funil_config_utils import invalidar_cache_funil
   invalidar_cache_funil()
   ```

---

## 📝 Exemplo de Fluxo Completo

### Setup Inicial

```bash
# 1. Migrations aplicadas
python manage.py migrate

# 2. Seed inicial
python manage.py seed_funil_config

# 3. Criar usuário admin
python manage.py createsuperuser
```

### Admin Customiza

```
1. Admin acessa /crm/admin/configuracao-funil/
2. Desativa "Número inválido" para NOVO
3. Reordena para: [Contato, Responsável Indisponível, Não atendeu]
4. Clica toggle → cache invalidado
```

### Vendedor Experimenta

```
1. Abre registro NOVO
2. Click "Registrar Contato"
3. Select mostra apenas 3 opções (sem "Número inválido")
4. Seleciona "Responsável não disponível"
5. Sistema agenda retorno
6. Card permanece em "Conta para Contato"
```

---

## 🚀 Próximas Extensões

- [ ] Editar label sem sair da página (inline)
- [ ] Arrastar para reordenar (drag-drop)
- [ ] Importar/exportar configurações (JSON)
- [ ] Auditoria: quem mudou o quê e quando
- [ ] Versionamento de configurações

---

**Última atualização:** 2026-01-10  
**Versão:** Phase 2.1  
**Status:** ✅ Em produção
