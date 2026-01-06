# Mini CRM - Sistema de Gestão de Leads

## 🚀 Setup Inicial

### Pré-requisitos:
- Python 3.10+
- pip/virtualenv
- PostgreSQL (recomendado para produção)

### Instalação:

1. **Clone o repositório:**
```bash
git clone <seu-repo>
cd crm
```

2. **Crie um virtualenv:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com seus valores
```

5. **Aplique as migrações:**
```bash
python manage.py migrate
```

6. **Crie um superuser:**
```bash
python manage.py createsuperuser
```

7. **Execute o servidor (development):**
```bash
python manage.py runserver
```

Acesse em: `http://localhost:8000/crm/`

---

## 🔒 Segurança

### IMPORTANTE ANTES DE EXPOR EM PRODUÇÃO:

Revise o arquivo [SECURITY_AUDIT.md](SECURITY_AUDIT.md) para um checklist completo.

**Passos críticos:**

1. **Gere uma nova SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Coloque o resultado em `.env`:
```
DJANGO_SECRET_KEY=seu-novo-valor-aqui
```

2. **Configure DEBUG=False:**
```
DEBUG=False
```

3. **Configure ALLOWED_HOSTS:**
```
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
```

4. **Configure HTTPS:**
- Use Let's Encrypt para certificado SSL gratuito
- Ative redirects HTTPS em `.env` e `settings.py`

5. **Use PostgreSQL em produção:**
```bash
pip install psycopg2-binary
```

Configure em `.env`:
```
USE_POSTGRES=True
DB_NAME=crm_db
DB_USER=crm_user
DB_PASSWORD=senha-forte
DB_HOST=seu-host-postgres
DB_PORT=5432
```

---

## 📊 Features

### Página Kanban (`/crm/`)
- Visualização de leads por status
- Cards com informações do cliente
- Ações: Avançar, Retornar, Arquivar
- Paginação com "Carregar Mais"
- Filtro por vendedor (Admin) ou próprios leads

### Métrica (`/crm/metricas/`)
- Estatísticas por período (Dia/Semana/Mês)
- Breakdown por origem do lead
- Análise de cidades
- Taxas de conversão

### Meu Desempenho (`/crm/meu-desempenho/`)
- Desempenho individual com período
- Taxas de conversão
- Total de leads

### Contas Ativas (`/crm/contas-ativas/`)
- Leads que viraram clientes
- Paginação
- Filtro por vendedor

### Arquivados (`/crm/arquivados/`)
- Leads que não qualificaram
- Possibilidade de restaurar

### Importar CSV (`/crm/importar-csv/`)
- Bulk import de leads
- Validação automática
- Relatório de erros

### Gestão de Usuários (`/crm/gestao-usuarios/`) - Admin Only
- CRUD de usuários
- Atribuição de grupos

---

## 🗄️ Banco de Dados

### Modelos:

**RegistroComercial**
- id (UUID)
- nome_empresa
- telefone
- cidade / uf
- origem
- canal_contato
- status_pipeline (conta_para_contato, contato_feito, negociacao_cotacao, pedido_realizado, conta_ativa, arquivada)
- vendedor (FK User)
- no_kanban (boolean)
- criado_em / atualizado_em
- arquivado (soft delete)

**ContatoHistorico**
- id (UUID)
- registro (FK RegistroComercial)
- resultado
- status_anterior / status_novo
- criado_em

**User** (Django Auth)
- username
- email
- groups (Admin, Comercial, Gerente)

### Índices:
- vendedor + criado_em
- status_pipeline + vendedor
- arquivado + criado_em
- origem + vendedor
- cidade + vendedor
- canal_contato

---

## 🔧 Configuração de Produção

### Usando Gunicorn + Nginx:

1. **Instale gunicorn:**
```bash
pip install gunicorn
```

2. **Crie arquivo de configuração** (`gunicorn.conf.py`):
```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
max_requests = 1000
max_requests_jitter = 100
timeout = 30
```

3. **Execute com gunicorn:**
```bash
gunicorn config.wsgi:application --config gunicorn.conf.py
```

4. **Configure Nginx como reverse proxy** (veja documentação)

### Backup de Banco de Dados:

```bash
# PostgreSQL
pg_dump crm_db > backup_$(date +%Y%m%d).sql

# Restaurar
psql crm_db < backup_20260106.sql
```

### Monitoring:

Recomendamos:
- **Logs**: ELK Stack ou Papertrail
- **Uptime**: Uptime Robot
- **Performance**: New Relic ou DataDog
- **Erros**: Sentry.io

---

## 📱 API Endpoints

### GET /crm/ - Kanban View
Requer: Login

### POST /crm/api/desempenho-vendedor/<vendedor_id>/
Requer: Login + Autorização
Payload:
```json
{
  "periodo": "dia" | "semana" | "mes"
}
```
Response:
```json
{
  "vendedor_nome": "string",
  "total_leads": 123,
  "conta_para_contato": 50,
  "contatos_realizados": 30,
  "negociacoes": 10,
  "pedidos": 5,
  "contas_ativas": 5,
  "taxa_contato": 60,
  "taxa_negociacao": 33,
  "taxa_pedido": 50,
  "taxa_recorrencia": 100
}
```

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### Erro: "ALLOWED_HOSTS"
Configure `ALLOWED_HOSTS` em `.env`:
```
ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com
```

### Erro: "No such table"
Execute migrations:
```bash
python manage.py migrate
```

### Performance lenta
- Verifique índices: `python manage.py sqlsequencereset crm`
- Habilite cache: Configure Redis em `.env`
- Aumente workers em produção

---

## 📞 Suporte

Para reportar bugs ou sugerir features, abra uma issue no repositório.

---

## 📄 Licença

[Sua Licença]

---

## 🙏 Agradecimentos

Desenvolvido com Django 6.0 e ❤️ 

**Versão:** 1.0.0  
**Última atualização:** 6 de janeiro de 2026
