"""
Script para testar a integração com o Telegram e a extração de dados de apostas.

Este script testa a conexão com o Telegram usando as credenciais configuradas
e verifica se é possível extrair corretamente os dados das mensagens de apostas.
"""
import asyncio
import os
import sys
from datetime import datetime
from loguru import logger

# Adiciona o diretório src ao path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import get_config
from src.telegram.monitor import TelegramMonitor
from src.telegram.parser import MessageParser, is_bet_message
from src.database.supabase_client import SupabaseClient

# Configura o logger
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO"
)

# Mensagens de teste para verificar os padrões de expressão regular
TEST_MESSAGES = [
    """
    Corrida: Hipódromo Nacional
    Cavalo: Relâmpago Negro
    Odds: 2.5
    Stake: 20
    Tipo: win
    """,
    """
    Aposta: Hipódromo Internacional - Trovão Veloz @ 3.2
    """,
    """
    Corrida Jockey Club: Pé de Vento (1.8)
    """
]

async def test_message_parsing():
    """Testa a análise de mensagens usando os padrões de expressão regular."""
    logger.info("Testando análise de mensagens...")
    
    for i, message in enumerate(TEST_MESSAGES):
        logger.info(f"Testando mensagem {i+1}:")
        logger.info(f"Conteúdo: {message.strip()}")
        
        # Verifica se a mensagem é identificada como uma aposta
        is_bet = is_bet_message(message)
        logger.info(f"É uma aposta? {is_bet}")
        
        # Tenta extrair os dados da aposta
        bet_data = MessageParser.parse_message(message)
        
        if bet_data:
            logger.info(f"Dados extraídos: Corrida: {bet_data.race}, Cavalo: {bet_data.horse_name}, Odds: {bet_data.odds}")
        else:
            logger.error("Falha ao extrair dados da aposta.")
        
        logger.info("-" * 50)

async def test_telegram_connection():
    """Testa a conexão com o Telegram usando as credenciais configuradas."""
    logger.info("Testando conexão com o Telegram...")
    
    config = get_config()
    
    # Verifica se as credenciais estão configuradas
    telegram_config = config["telegram"]
    if not all([
        telegram_config["api_id"],
        telegram_config["api_hash"],
        telegram_config["group_id"]
    ]):
        logger.error("Credenciais do Telegram não configuradas corretamente.")
        return False
    
    logger.info("Credenciais do Telegram configuradas corretamente.")
    
    # Cria uma instância do monitor do Telegram
    db_client = SupabaseClient()
    monitor = TelegramMonitor(db_client)
    
    # Registra um handler para mensagens
    received_messages = []
    
    async def message_handler(message_data):
        logger.info(f"Mensagem recebida: {message_data}")
        received_messages.append(message_data)
    
    monitor.add_bet_handler(message_handler)
    
    # Tenta iniciar o monitor (sem bloquear)
    logger.info("Iniciando monitor do Telegram...")
    
    # Cria uma task para o monitor
    monitor_task = asyncio.create_task(monitor.start())
    
    # Aguarda alguns segundos para verificar se a conexão foi estabelecida
    try:
        # Aguarda até 30 segundos para ver se recebemos alguma mensagem
        for _ in range(30):
            if monitor.is_running:
                logger.info("Monitor do Telegram iniciado com sucesso.")
                break
            
            logger.info("Aguardando inicialização do monitor...")
            await asyncio.sleep(1)
        
        if not monitor.is_running:
            logger.warning("Tempo limite excedido, mas o monitor pode estar funcionando.")
        
        # Aguarda mais alguns segundos para receber mensagens
        logger.info("Aguardando mensagens por 10 segundos...")
        await asyncio.sleep(10)
        
        # Verifica se recebemos alguma mensagem
        if received_messages:
            logger.info(f"Recebidas {len(received_messages)} mensagens.")
        else:
            logger.info("Nenhuma mensagem recebida durante o período de teste.")
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
    finally:
        # Para o monitor
        logger.info("Parando o monitor do Telegram...")
        await monitor.stop()
        
        # Cancela a task
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
    
    logger.info("Teste de conexão com o Telegram concluído.")
    return True

async def main():
    """Função principal para executar os testes."""
    logger.info("Iniciando testes de integração com o Telegram...")
    
    # Testa a análise de mensagens
    await test_message_parsing()
    
    # Testa a conexão com o Telegram
    connection_result = await test_telegram_connection()
    
    if connection_result:
        logger.info("Testes concluídos com sucesso.")
    else:
        logger.error("Falha nos testes de conexão com o Telegram.")

if __name__ == "__main__":
    asyncio.run(main())
