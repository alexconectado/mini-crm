# Mini-CRM Operacional Zandomax

Sistema de controle de esforço comercial e avanço de contas.

## Stack Tecnológica

- **Backend**: Django 6.0
- **Frontend**: Django Templates (server-side)
- **Estilo**: TailwindCSS (via CDN)
- **Interações**: Alpine.js (drag & drop)
- **Banco de Dados**: SQLite (MVP)

## Instalação

1. **Criar ambiente virtual e ativar**:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Instalar dependências**:
```bash
pip install -r requirements.txt
```

3. **Executar migrations**:
```bash
python manage.py migrate
```

4. **Criar superusuário**:
```bash
python manage.py createsuperuser
```

5. **Rodar servidor**:
```bash
python manage.py runserver
```

6. **Acessar**:
- Interface principal: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Funcionalidades Implementadas

### ✅ Prompt 1 - Schema e Models
- Models `RegistroComercial` e `ContatoHistorico`
- Enums para Origem e Status Pipeline
- Django Admin customizado com badges e filtros
- Campo origem não editável após criação

### ✅ Prompt 2 - Backlog + Kanban
- Interface com backlog lateral
- Kanban principal com 6 colunas (importado, contatado, conversou, interesse, pedido, perdido)
- Drag & drop manual entre colunas
- Mover registros entre Backlog ↔ Kanban
- TailwindCSS para estilização
- Alpine.js para interações

### ✅ Prompt 3 - Registro de Contato
- Formulário de registro de contato (≤30s)
- Timestamp automático
- Campo resultado obrigatório
- Atualização opcional de status
- Histórico completo de contatos

### ✅ Prompt 4 - Origem Obrigatória
- Campo origem como select obrigatório
- 8 valores pré-definidos
- Bloqueado após criação (read-only no admin)

### ✅ Prompt 5 - Importação CSV
- Upload manual de CSV
- Validação de campos obrigatórios
- Associação automática ao vendedor logado
- Feedback de erros e sucessos

### ✅ Prompt 6 - Métricas Básicas
- Total de registros
- Total de contatos
- Contatos do dia
- Distribuição por status
- Filtro por vendedor (vendedor vê apenas seus registros)

### ✅ Prompt 7 - Fora de Escopo
- ❌ Sem automações
- ❌ Sem integrações externas
- ❌ Sem API REST
- ❌ Sem Django REST Framework
- ❌ Sem funcionalidades financeiras

## Estrutura do Projeto

```
crm/
├── config/              # Configurações do Django
├── crm/                 # App principal
│   ├── models.py        # Models (RegistroComercial, ContatoHistorico)
│   ├── views.py         # Views (kanban, registro contato, métricas, CSV)
│   ├── admin.py         # Django Admin customizado
│   ├── urls.py          # URLs do app
│   ├── templates/       # Templates HTML
│   └── templatetags/    # Template filters
├── docs/                # Documentação e prompts
├── db.sqlite3          # Banco de dados
└── manage.py           # Django management
```

## Uso

### Como Vendedor
1. Acesse o Kanban
2. Veja seus registros no Backlog (lateral esquerda)
3. Clique em um registro para movê-lo ao Kanban
4. Arraste cards entre colunas para atualizar status
5. Registre contatos clicando no botão "Registrar Contato"
6. Visualize suas métricas na página de Métricas

### Como Gestor (Superusuário)
- Vê todos os registros de todos os vendedores
- Acessa métricas consolidadas
- Não interfere em registros individuais

### Importar CSV
1. Prepare CSV com colunas: `nome_empresa,telefone,cidade,uf,origem,codigo_winthor`
2. Acesse "Importar CSV" no menu
3. Faça upload do arquivo
4. Registros vão para o Backlog automaticamente

## Regras de Negócio

- **Backlog**: Todos os registros não ativos
- **Kanban**: Apenas trabalho em andamento (ação consciente do vendedor)
- **Origem**: Não pode ser alterada após criação
- **Registro de Contato**: Obrigatório para avançar vendas
- **Vendedor**: Vê apenas seus próprios registros
- **Gestor**: Vê todos, mas não interfere

## Critérios de Sucesso (30 dias)

- [ ] Uso diário pelo time
- [ ] Registro consistente
- [ ] Gargalos visíveis
- [ ] Decisão baseada em dados

## Observações

Sistema intencionalmente simples. Qualquer tentativa de complexificação deve ser evitada.
