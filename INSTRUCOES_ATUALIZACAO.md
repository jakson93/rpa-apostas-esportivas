# Instruções para Atualização do Projeto Local

Este documento contém instruções para atualizar seu projeto local com as alterações que foram enviadas para o GitHub.

## Pré-requisitos

- Git instalado em seu computador
- Python 3.10 ou superior instalado
- Pip (gerenciador de pacotes do Python)

## Passos para Atualização

### 1. Atualizar o Repositório Local

Se você já tem o repositório clonado em seu computador, siga estes passos para atualizar:

```bash
# Navegue até a pasta do projeto
cd caminho/para/rpa-apostas-esportivas

# Certifique-se de estar na branch main
git checkout main

# Obtenha as alterações mais recentes do GitHub
git pull origin main
```

### 2. Instalar ou Atualizar Dependências

```bash
# Instale ou atualize as dependências necessárias
pip install -r requirements.txt
```

### 3. Configurar o Arquivo .env

Verifique se o arquivo `.env` contém suas credenciais do Telegram. O arquivo deve ter o seguinte formato:

```
# Credenciais do Telegram
TELEGRAM_API_ID=24736957
TELEGRAM_API_HASH=23c14014600b065612502feb0c455109
TELEGRAM_BOT_TOKEN=6156089370:AAFNQQFaTAMyJdyMa8YU5MTAefAqNbMf9Cw
TELEGRAM_GROUP_ID=-1001534658039

# Credenciais do Supabase (opcional)
SUPABASE_URL=sua_url_supabase
SUPABASE_KEY=sua_chave_supabase

# Configurações de apostas
DEFAULT_STAKE=10
MAX_STAKE=100
MIN_STAKE=5

# Configurações do navegador
BROWSER_TYPE=chrome
HEADLESS=false

# Configurações da aplicação
DEBUG_MODE=true
LOG_LEVEL=INFO
```

### 4. Executar o Projeto

```bash
# Navegue até a pasta src
cd src

# Execute o programa principal
python main.py
```

## Principais Alterações

1. **Remoção da Simulação**: A simulação de chegada de apostas foi removida e substituída por uma integração real com o Telegram.

2. **Remoção do Gráfico de Evolução**: O gráfico de evolução de apostas foi removido da dashboard conforme solicitado.

3. **Automação Real**: O sistema agora aciona a automação para a bolsa de apostas quando uma aposta real é recebida do Telegram.

## Solução de Problemas

Se encontrar algum problema durante a atualização ou execução:

1. Verifique se todas as dependências foram instaladas corretamente
2. Confirme se o arquivo `.env` está configurado corretamente
3. Verifique os logs em `logs/app.log` para identificar possíveis erros
4. Se necessário, remova a pasta `telegram_session.session` e reinicie o programa para criar uma nova sessão do Telegram

Para mais detalhes sobre as alterações realizadas, consulte o arquivo `docs/ALTERACOES.md` no repositório.
