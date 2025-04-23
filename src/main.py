"""
Módulo principal da aplicação.

Este módulo integra todos os componentes do sistema de automação de apostas,
conectando o fluxo desde a extração de dados do Telegram até a execução das apostas.
"""
import os
import sys
import asyncio
import threading
import signal
from typing import Dict, Any, Optional
from loguru import logger

from config.settings import get_config
from telegram.manager import TelegramManager, create_telegram_manager
from database.supabase_client import SupabaseClient
from database.schemas import Bet
from browser.manager import get_browser_manager
from gui.app import start_gui


class Application:
    """
    Classe principal da aplicação que integra todos os módulos.
    """
    
    def __init__(self):
        """
        Inicializa a aplicação.
        """
        self.config = get_config()
        self.db_client = SupabaseClient()
        self.telegram_manager = None
        self.browser_manager = get_browser_manager()
        self.running = False
        self.event_loop = None
        self.telegram_task = None
    
    async def start_telegram(self):
        """
        Inicia o módulo do Telegram.
        
        Returns:
            bool: True se iniciado com sucesso, False caso contrário.
        """
        try:
            # Cria e inicia o gerenciador do Telegram
            self.telegram_manager = await create_telegram_manager()
            
            # Registra o callback para processar apostas
            self.telegram_manager.register_bet_callback(self.process_bet)
            
            logger.info("Módulo do Telegram iniciado com sucesso.")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao iniciar o módulo do Telegram: {e}")
            return False
    
    def start_browser(self, username: str, password: str):
        """
        Inicia o módulo do navegador.
        
        Args:
            username: Nome de usuário para login.
            password: Senha para login.
            
        Returns:
            bool: True se iniciado com sucesso, False caso contrário.
        """
        try:
            # Inicia o gerenciador de navegador
            result = self.browser_manager.start(username, password)
            
            if result:
                logger.info("Módulo do navegador iniciado com sucesso.")
            else:
                logger.error("Falha ao iniciar o módulo do navegador.")
            
            return result
        
        except Exception as e:
            logger.error(f"Erro ao iniciar o módulo do navegador: {e}")
            return False
    
    async def process_bet(self, bet_data):
        """
        Processa uma nova aposta recebida do Telegram.
        
        Args:
            bet_data: Dados da aposta (objeto BetData ou dicionário).
        """
        try:
            # Converte para objeto Bet se for um dicionário
            if isinstance(bet_data, dict):
                # Salva a aposta no banco de dados
                saved_bet = await self.db_client.save_bet(bet_data)
                
                if saved_bet:
                    bet_id = saved_bet.get("id")
                    logger.info(f"Aposta salva no banco de dados com ID: {bet_id}")
                    
                    # Cria objeto Bet a partir dos dados salvos
                    bet = Bet.from_dict(saved_bet)
                else:
                    logger.error("Falha ao salvar aposta no banco de dados.")
                    return
            else:
                # Já é um objeto BetData, converte para Bet
                bet = Bet(
                    race=bet_data.race,
                    horse_name=bet_data.horse_name,
                    odds=bet_data.odds,
                    stake=bet_data.stake or float(self.config["betting"]["default_stake"]),
                    bet_type=bet_data.bet_type,
                    raw_message=bet_data.raw_message,
                    status="pending",
                    created_at=bet_data.created_at
                )
                
                # Salva a aposta no banco de dados
                saved_bet = await self.db_client.save_bet(bet.to_dict())
                
                if saved_bet:
                    bet.id = saved_bet.get("id")
                    logger.info(f"Aposta salva no banco de dados com ID: {bet.id}")
                else:
                    logger.error("Falha ao salvar aposta no banco de dados.")
                    return
            
            # Verifica se o stake está definido, caso contrário usa o padrão
            if not bet.stake:
                bet.stake = float(self.config["betting"]["default_stake"])
            
            # Adiciona a aposta à fila do navegador
            self.browser_manager.add_bet_to_queue(bet)
            
            # Registra a ação no log
            await self.db_client.log_action(
                "bet_queued",
                f"Aposta em {bet.horse_name} na corrida {bet.race} adicionada à fila",
                bet.id
            )
        
        except Exception as e:
            logger.error(f"Erro ao processar aposta: {e}")
    
    async def process_pending_bets(self):
        """
        Processa apostas pendentes do banco de dados.
        """
        try:
            # Obtém apostas pendentes
            pending_bets = await self.db_client.get_pending_bets()
            
            if pending_bets:
                logger.info(f"Encontradas {len(pending_bets)} apostas pendentes.")
                
                for bet_data in pending_bets:
                    # Converte para objeto Bet
                    bet = Bet.from_dict(bet_data)
                    
                    # Adiciona à fila do navegador
                    self.browser_manager.add_bet_to_queue(bet)
                    
                    # Atualiza o status para "queued"
                    await self.db_client.update_bet_status(bet.id, "queued")
                    
                    # Registra a ação no log
                    await self.db_client.log_action(
                        "bet_queued",
                        f"Aposta pendente em {bet.horse_name} na corrida {bet.race} adicionada à fila",
                        bet.id
                    )
            else:
                logger.info("Nenhuma aposta pendente encontrada.")
        
        except Exception as e:
            logger.error(f"Erro ao processar apostas pendentes: {e}")
    
    async def start_async(self):
        """
        Inicia a aplicação de forma assíncrona.
        
        Returns:
            bool: True se iniciado com sucesso, False caso contrário.
        """
        try:
            self.running = True
            
            # Inicia o módulo do Telegram
            telegram_result = await self.start_telegram()
            
            if not telegram_result:
                logger.error("Falha ao iniciar o módulo do Telegram. A aplicação não será iniciada.")
                self.running = False
                return False
            
            # Processa apostas pendentes
            await self.process_pending_bets()
            
            logger.info("Aplicação iniciada com sucesso.")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao iniciar a aplicação: {e}")
            self.running = False
            return False
    
    def start(self):
        """
        Inicia a aplicação.
        
        Returns:
            bool: True se iniciado com sucesso, False caso contrário.
        """
        # Cria um novo event loop para o Telegram
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        
        # Inicia o módulo do Telegram em uma thread separada
        self.telegram_task = self.event_loop.create_task(self.start_async())
        
        # Executa o event loop em uma thread separada
        threading.Thread(target=self._run_event_loop, daemon=True).start()
        
        return True
    
    def _run_event_loop(self):
        """
        Executa o event loop do asyncio em uma thread separada.
        """
        self.event_loop.run_forever()
    
    def stop(self):
        """
        Para a aplicação.
        """
        self.running = False
        
        # Para o módulo do Telegram
        if self.telegram_manager:
            asyncio.run_coroutine_threadsafe(self.telegram_manager.stop(), self.event_loop)
        
        # Para o módulo do navegador
        if self.browser_manager:
            self.browser_manager.stop()
        
        # Para o event loop
        if self.event_loop:
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
        
        logger.info("Aplicação parada com sucesso.")


def main():
    """
    Função principal para iniciar a aplicação.
    """
    # Configura o logger
    logger.remove()
    logger.add(
        os.path.join(os.getcwd(), "logs", "app.log"),
        rotation="10 MB",
        retention="1 week",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    logger.add(sys.stderr, level="INFO")
    
    # Inicia a aplicação
    app = Application()
    
    # Configura o handler para sinais de término
    def signal_handler(sig, frame):
        logger.info("Sinal de término recebido. Parando a aplicação...")
        app.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Inicia a interface gráfica
    start_gui()


if __name__ == "__main__":
    main()
