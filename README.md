# RPA para Apostas Esportivas

Este projeto implementa uma solução de automação RPA (Robotic Process Automation) para apostas esportivas, integrando extração de dados do Telegram com automação de navegador para realizar apostas automaticamente no site [Bolsa de Aposta](https://bolsadeaposta.bet.br/dsbook/euro/sport/horseracing).

## Funcionalidades

- **Extração de dados do Telegram**: Monitoramento de mensagens em grupos específicos para identificar e extrair informações de apostas.
- **Interface gráfica**: GUI para configuração de credenciais, stake padrão e outras opções.
- **Banco de dados**: Integração com Supabase para armazenamento de apostas, logs e gerenciamento de fila de apostas.
- **Automação de apostas**: Execução automática de apostas no site alvo com base nas informações extraídas.

## Estrutura do Projeto

```
rpa_apostas_esportivas/
├── src/
│   ├── telegram/     # Módulo para interação com a API do Telegram
│   ├── gui/          # Interface gráfica para configuração
│   ├── database/     # Integração com Supabase
│   ├── browser/      # Automação de navegador
│   ├── utils/        # Funções utilitárias
│   └── config/       # Configurações do sistema
├── tests/            # Testes automatizados
└── docs/             # Documentação adicional
```

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`
- Conta no Supabase
- Credenciais de API do Telegram

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITORIO]
cd rpa_apostas_esportivas
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

## Configuração

1. Configure suas credenciais do Telegram no arquivo `.env`
2. Configure suas credenciais do Supabase no arquivo `.env`
3. Inicie a aplicação GUI para configurar as opções de apostas

## Uso

```bash
python src/main.py
```

## Desenvolvimento

Para contribuir com o projeto:

1. Crie um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Envie para o branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

[Especificar a licença]
