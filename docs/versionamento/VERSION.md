# Mini CRM - Versionamento

## [1.0.0] - 2026-01-06 - VERSÃO PÚBLICA (PRÉ-PRODUÇÃO)

### ✨ Features Implementadas:
- **Kanban visual** com cards por status pipeline
- **Gestão de leads** com CRUD completo
- **Métricas** por período (Dia/Semana/Mês)
- **Desempenho de vendedores** com taxas de conversão
- **Import CSV** para bulk upload de leads
- **Arquivos** para leads não qualificados
- **Contas ativas** para conversões bem-sucedidas
- **Gestão de usuários** (Admin only)
- **Autenticação** com Django Auth
- **Autorização** por grupo (Admin, Comercial)
- **Paginação** em todas as views com "Carregar Mais"
- **Cache** para performance
- **9 índices de banco de dados** para otimização

### 🔒 Segurança Implementada:
- ✅ Autenticação login/logout
- ✅ Autorização por grupos
- ✅ CSRF protection
- ✅ XFrame protection
- ✅ ORM queries (SQL Injection protection)
- ✅ Session security (HTTPOnly cookies)
- ✅ Soft delete (arquivos)
- ✅ Auditoria (created_at, updated_at)

### 🔧 Ajustes de Segurança Realizados (v1.0.0):
- ✅ SECRET_KEY movido para variáveis de ambiente
- ✅ DEBUG configurável via .env
- ✅ ALLOWED_HOSTS dinâmico
- ✅ HTTPS/SSL headers configurados para produção
- ✅ Session timeout: 1 hora
- ✅ HTTPOnly cookies para session
- ✅ Validação de arquivo CSV (tamanho, extensão, MIME type)
- ✅ Proteção de acesso em API (não permitir ver dados de outro vendedor)
- ✅ python-dotenv para .env support

### 📋 Checklist PRÉ-PRODUÇÃO:
- ⚠️ **TODO**: Instalar dependências: `pip install -r requirements.txt`
- ⚠️ **TODO**: Criar `.env` a partir de `.env.example`
- ⚠️ **TODO**: Gerar nova SECRET_KEY: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- ⚠️ **TODO**: Configurar PostgreSQL (opcional, recomendado)
- ⚠️ **TODO**: Configurar Redis para cache (opcional)
- ⚠️ **TODO**: Configurar HTTPS com Let's Encrypt
- ⚠️ **TODO**: Rodar testes de segurança
- ⚠️ **TODO**: Backup de banco de dados
- ⚠️ **TODO**: Monitoramento e logs

### 🐛 Bugs Corrigidos:
- ✅ Kanban cards mostrando 0 (fixed `get_item` filter)
- ✅ Template error em metricas.html (missing `{% endblock %}`)
- ✅ Período filter não funcionando (changed to date-based filtering)
- ✅ Admin não vendo dados de todos vendedores (fixed API logic)

### 📚 Documentação:
- `SECURITY_AUDIT.md` - Auditoria completa de segurança
- `README.md` - Instruções de setup
- `.env.example` - Template de variáveis de ambiente

---

## [0.9.0] - 2026-01-05 - Scalability Implementation

### ✨ Melhorias de Performance:
- Implementou 9 índices de banco de dados
- Paginação com "Carregar Mais"
- Cache de 5 minutos para listagens
- Otimização de queries com select_related/prefetch_related

### 🔧 Ajustes:
- Métricas separadas por Origem e Cidades
- Removeu filtros dropdown (usar botões de período)
- Kanban cards com período (Dia/Semana/Mês)

---

## [0.8.0] - 2026-01-02 - Initial Release

### ✨ Core Features:
- Kanban board
- Lead management
- Metrics dashboard
- User management
- CSV import

---

## Convenção de Versionamento

Usamos **Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes

## Deployment

### Development:
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Production:
```bash
# 1. Criar .env com valores reais
cp .env.example .env
# Editar .env com settings de produção

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 4. Aplicar migrações
python manage.py migrate

# 5. Usar gunicorn (não runserver)
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Próximas Features (v1.1.0):

- [ ] Relatórios exportáveis (PDF/Excel)
- [ ] Integração WhatsApp Web
- [ ] Automação de follow-up
- [ ] Análise de funil de vendas
- [ ] Dashboard em tempo real (WebSockets)
- [ ] Mobile app
- [ ] API REST pública (com autenticação)
- [ ] Integração CRM externo
