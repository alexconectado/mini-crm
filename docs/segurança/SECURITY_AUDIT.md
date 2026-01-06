# 🔒 Auditoria de Segurança - Mini CRM

**Data:** 6 de janeiro de 2026  
**Status:** ⚠️ **REQUER AJUSTES ANTES DE PRODUÇÃO**

---

## 📋 Resumo Executivo

A aplicação possui **boas práticas básicas** implementadas, mas há **8 problemas críticos** que devem ser corrigidos **antes de expor em subdomínio público**.

### Severity Levels:
- 🔴 **CRÍTICO** - Exploração fácil, dados em risco
- 🟠 **ALTO** - Vulnerabilidade significativa
- 🟡 **MÉDIO** - Risco moderado
- 🟢 **BAIXO** - Melhoria recomendada

---

## 🔴 PROBLEMAS CRÍTICOS

### 1. **SECRET_KEY exposto no repositório**
**Arquivo:** `config/settings.py`, linha 25

```python
SECRET_KEY = 'django-insecure-hq7tg^q35e)@u_+i%xae1pe@2*z4i8p(rr&0fi&u=9fq&#a*wc'
```

**Risco:** Qualquer pessoa com acesso ao repositório pode forjar sessões, tokens CSRF, etc.

**Solução:**
```bash
# 1. Gerar nova SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. Usar variável de ambiente
# Em settings.py:
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fallback-para-desenvolvimento')

# 3. Adicionar ao .env ou deployment
export DJANGO_SECRET_KEY="your-new-random-key-here"
```

---

### 2. **DEBUG = True em produção**
**Arquivo:** `config/settings.py`, linha 28

```python
DEBUG = True
```

**Risco:** 
- Expõe stack traces detalhados com caminhos de arquivo
- Mostra valores de variáveis de ambiente
- Permite exploração de informações sensíveis

**Solução:**
```python
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
# Em produção: DEBUG=False
```

---

### 3. **ALLOWED_HOSTS vazio**
**Arquivo:** `config/settings.py`, linha 30

```python
ALLOWED_HOSTS = []
```

**Risco:** Vulnerável a ataques Host Header Injection

**Solução:**
```python
ALLOWED_HOSTS = [
    'crm.seudominio.com',
    'www.crm.seudominio.com',
    os.environ.get('ALLOWED_HOST', 'localhost'),
]
```

---

### 4. **Sem proteção HTTPS/SSL**
**Configuração não existe**

**Risco:**
- Credenciais transmitidas em texto plano
- Cookies de sessão vulneráveis a intercepção
- Man-in-the-middle attacks

**Solução:**
```python
# Em settings.py (para HTTPS)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

---

### 5. **API endpoint sem verificação de acesso adequada**
**Arquivo:** `crm/views.py`, linha 925-1010 (`desempenho_vendedor_api`)

```python
@login_required  # ❌ Apenas login, não verifica se pode ver dados de outro vendedor
@require_POST
def desempenho_vendedor_api(request, vendedor_id):
```

**Risco:** Um vendedor pode acessar dados de outro vendedor alterando `vendedor_id` na URL

**Verificação atual:**
```python
if request.user.is_superuser:
    # Admin vê tudo (OK)
else:
    # Vendedor vê apenas seus dados (OK)
```

**Problema:** A verificação ocorre no início, mas não valida se `vendedor_id` corresponde ao usuário atual.

**Solução:**
```python
@login_required
@require_POST
def desempenho_vendedor_api(request, vendedor_id):
    # Validar que o usuário só pode ver seus próprios dados
    if not request.user.is_superuser and request.user.id != vendedor_id:
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    # ... resto do código
```

---

### 6. **CSV Import sem validação de arquivo**
**Arquivo:** `crm/views.py`, linha 859-922

```python
csv_file = request.FILES['csv_file']
decoded_file = csv_file.read().decode('utf-8').splitlines()
```

**Riscos:**
- Sem limite de tamanho (DoS via arquivo gigante)
- Sem validação de tipo MIME
- Sem validação de nome de arquivo
- Pode processar arquivos malformados

**Solução:**
```python
def importar_csv_view(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # ✅ Validar tamanho (máx 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            context = {'error': 'Arquivo muito grande (máx 5MB)'}
            return render(request, 'crm/importar_csv.html', context)
        
        # ✅ Validar tipo MIME
        if csv_file.content_type not in ['text/csv', 'application/vnd.ms-excel']:
            context = {'error': 'Arquivo deve ser CSV válido'}
            return render(request, 'crm/importar_csv.html', context)
        
        # ✅ Validar extensão
        if not csv_file.name.endswith('.csv'):
            context = {'error': 'Arquivo deve ter extensão .csv'}
            return render(request, 'crm/importar_csv.html', context)
        
        # ... resto do código
```

---

### 7. **Sem Rate Limiting em APIs**
**Afeta:** Todos os endpoints POST (`atualizar_status`, `registrar_contato`, etc)

**Risco:** Brute force, DoS attacks

**Solução:** Instalar `django-ratelimit`

```bash
pip install django-ratelimit
```

Adicionar a decoradores:
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='100/h', method='POST')
@comercial_required
def atualizar_status(request, registro_id):
    # ...
```

---

### 8. **Banco de dados SQLite em produção**
**Arquivo:** `config/settings.py`, linha 73-77

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Riscos:**
- Sem controle de concorrência
- Sem backup automático
- Sem replicação
- Sem criptografia de dados

**Solução:** Usar PostgreSQL em produção

```python
# settings.py
if os.environ.get('USE_POSTGRES') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
```

---

## 🟠 PROBLEMAS ALTOS

### 9. **Session timeout não configurado**
**Recomendação:**
```python
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

---

### 10. **Logs não configurados**
**Recomendação:** Adicionar logging estruturado para auditoria

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/crm.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'crm': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

### 11. **Sem validação de entrada (em alguns campos)**
Embora o Django ORM proteja contra SQL Injection, há campos que aceitam input direto:

```python
# crm/views.py, linha 227-233
nome_empresa = request.POST.get('nome_empresa', '').strip()
telefone = request.POST.get('telefone', '').strip()
```

**Adicionar validação:**
```python
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\d{10,15}$',
    message='Telefone deve ter 10-15 dígitos'
)

class RegistroComercial(models.Model):
    # ...
    telefone = models.CharField(
        max_length=15,
        validators=[phone_validator]
    )
```

---

## 🟡 PROBLEMAS MÉDIOS

### 12. **Sem proteção CSRF em templates**
**Verificação:** Revisar se todo form tem `{% csrf_token %}`

---

### 13. **Cache inseguro para dados sensíveis**
**Arquivo:** `config/settings.py`, linha 81-88

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # ❌ Dados em memória da aplicação - inseguro em cluster
    }
}
```

**Solução para produção:** Usar Redis

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

## 🟢 MELHORIAS RECOMENDADAS

### 14. **Adicionar Content Security Policy (CSP)**
```python
# Usar django-csp
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),  # ⚠️ Remover unsafe-inline depois
    'style-src': ("'self'", "'unsafe-inline'"),
}
```

---

### 15. **Adicionar segurança de headers**
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## ✅ O QUE JÁ ESTÁ BOM

- ✅ Middleware de segurança ativado
- ✅ Autenticação implementada
- ✅ Decoradores de autorização (grupo_required, comercial_required, admin_required)
- ✅ Sem queries raw SQL
- ✅ ORM Django protegendo contra SQL Injection
- ✅ CSRF middleware ativado
- ✅ XFrame middleware ativado
- ✅ Timestamps de auditoria (criado_em, atualizado_em)
- ✅ Soft delete implementado (arquivado)

---

## 📋 CHECKLIST PRÉ-PRODUÇÃO

### CRÍTICO (Fazer antes de expor):
- [ ] Gerar nova SECRET_KEY e usar variáveis de ambiente
- [ ] Definir DEBUG = False
- [ ] Configurar ALLOWED_HOSTS com domínio real
- [ ] Ativar HTTPS/SSL
- [ ] Adicionar validação de acesso em `desempenho_vendedor_api`
- [ ] Adicionar validação de upload CSV
- [ ] Configurar banco de dados PostgreSQL
- [ ] Adicionar Rate Limiting

### ALTO (Fazer antes de semana 1):
- [ ] Configurar logs
- [ ] Session timeout
- [ ] Redis para cache

### MÉDIO (Fazer antes do mês 1):
- [ ] CSP headers
- [ ] Validação de entrada
- [ ] Testes de segurança

---

## 🚀 PRÓXIMOS PASSOS

1. **Criar arquivo `.env`** para secrets
2. **Atualizar requirements.txt** com dependências de segurança
3. **Implementar migrations** para validadores
4. **Testar em staging** antes de produção
5. **Configurar backup** do banco de dados

