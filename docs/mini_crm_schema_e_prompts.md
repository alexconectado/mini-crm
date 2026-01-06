# Mini-CRM Operacional — Especificação Oficial

> Documento de referência para construção do **Mini-CRM Operacional da Zandomax**.
> 
> **Objetivo:** controle de esforço comercial e avanço de contas, sem substituir ERP, CRM ou ferramentas de conversa.
> 
> **Escopo fechado (MVP – 30 dias).**

---

## 1. Princípios do Sistema

- Menos funcionalidade = mais uso
- Conversa acontece fora (Chatwoot / telefone)
- Registro acontece dentro (Mini-CRM)
- Registro rápido (≤ 30s)
- Sem automação inteligente
- Sem integração bidirecional
- Sistema descartável se não gerar valor

---

## 2. Papéis de Usuário

### Vendedor
- Visualiza apenas sua própria base
- Puxa registros do backlog para o Kanban
- Registra contatos e resultados
- Não edita pipeline global

### Gestor
- Visualiza todos os vendedores
- Acessa métricas consolidadas
- Não interfere em registros individuais

---

## 3. Estrutura Geral

### Visão da Interface

- Coluna lateral: **Backlog** (lista completa de contas/leads)
- Área principal: **Kanban** (trabalho em andamento)
- Aba embutida (iframe/link): **Chatwoot – Inbox de Conversa**

---

## 4. Schema de Dados (Definitivo)

### 4.1 Entidade: Registro Comercial

| Campo | Tipo | Obrigatório | Observações |
|-----|-----|-------------|-------------|
| id | UUID | Sim | Chave interna |
| codigo_winthor | String | Não | Nullable até conversão |
| nome_empresa | String | Sim | Nome comercial |
| telefone | String | Sim | Texto livre |
| cidade | String | Sim | — |
| uf | String(2) | Sim | — |
| vendedor_id | UUID | Sim | Somente leitura para vendedor |
| origem | Enum | Sim | Lista suspensa |
| status_pipeline | Enum | Sim | Kanban |
| ultimo_contato | Datetime | Não | Preenchido no registro |
| resultado_ultimo_contato | Text | Não | Curto |
| proximo_passo | Text | Não | Curto |
| data_conversao_cliente | Datetime | Não | Quando virar Winthor |
| criado_em | Datetime | Sim | Automático |

---

### 4.2 Enum: Origem (Obrigatório)

Valores iniciais:

- base_winthor (automático / read-only)
- google
- site
- instagram
- indicacao
- prospeccao_fria
- whatsapp_ativo
- outros

Regras:
- Campo obrigatório
- Lista suspensa
- Não editável após salvar
- Não permite criação de novos valores no MVP

---

### 4.3 Enum: Status Pipeline (Kanban)

Ordem fixa inicial:

1. importado
2. contatado
3. conversou
4. interesse
5. pedido
6. perdido

Regras:
- Apenas um pipeline ativo
- Cards entram no Kanban apenas quando puxados do backlog

---

## 5. Backlog

### Função
- Armazenar toda a base existente
- Não representa trabalho ativo

### Regras
- Crescimento ilimitado
- Cards só entram no Kanban por ação consciente do vendedor

---

## 6. Kanban

### Função
- Representar trabalho em andamento

### Regras
- Limite implícito (recomendado 10–20 cards por vendedor)
- Card parado > 7 dias = alerta de processo

---

## 7. Registro de Contato

### Evento principal do sistema

Ao registrar contato:
- Timestamp automático
- Campo resultado obrigatório
- Atualização opcional de status

Regra:
> Conversa sem registro = não aconteceu

---

## 8. Chatwoot (Camada de Conversa)

Uso permitido:
- Inbox
- Resposta ao cliente
- Etiquetas simples

Etiquetas oficiais:
- novo_contato
- conversou
- interesse
- pedido
- perdido

Chatwoot **não é fonte da verdade**.

---

## 9. Métricas

### Por vendedor
- Registros importados
- Contatos realizados
- Conversas
- Interesses
- Pedidos
- Perdidos

### Consolidadas
- Contatos/dia
- Conversas/dia
- Taxa de avanço

---

## 10. Integração com Winthor (Compatibilidade)

- Winthor é fonte da verdade pós-venda
- Mini-CRM prepara o dado
- Conversão gera CSV manual para cadastro

---

## 11. Fora de Escopo (Proibido)

- Automação
- Integração bidirecional
- Financeiro
- Estoque
- CRM completo
- Marketing

---

## 12. Critério de Sucesso (30 dias)

- Uso diário pelo time
- Registro consistente
- Gargalos visíveis
- Decisão baseada em dado

---


> **Nota final:**
> Este sistema é intencionalmente simples. Qualquer tentativa de complexi