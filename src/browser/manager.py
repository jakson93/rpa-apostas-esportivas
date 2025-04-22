"""
Módulo para gerenciamento de sessões do navegador.

Este módulo implementa o gerenciamento de sessões do navegador,
permitindo criar, reutilizar e encerrar sessões de automação.
"""
import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading
import queue
from loguru import logger

from .automation import BrowserAutomation
from ..config.settings import get_config
from ..database.schemas import Bet
from ..database.supabase_client import SupabaseClient


class BrowserManager:
    """
    Classe para gerenciar sessões do navegador.
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de navegador.
        """
        self.config = get_config()
        self.browser = None
        self.db_client = SupabaseClient()
        self.bet_queue = queue.Queue()
        self.processing_thread = None
        self.running = False
        self.screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        
        # Cria o diretório de screenshots se não existir
        if not os.path.exists(self.screenshots_dir):
            os.makedirs(self.screenshots_dir)
    
    def start(self, username: str, password: str) -> bool:
        """
        Inicia o gerenciador de navegador.
        
        Args:
            username: Nome de usuário para login.
            password: Senha para login.
            
        Returns:
            bool: True se iniciado com sucesso, False caso contrário.
        """
        try:
            # Cria uma nova instância do navegador
            self.browser = BrowserAutomation(
                headless=self.config["browser"]["headless"]
            )
            
            # Inicia o navegador
            if not self.browser.start():
                logger.error("Falha ao iniciar o navegador.")
                return False
            
            # Realiza login
            if not self.browser.login(username, password):
                logger.error("Falha ao realizar login.")
                self.browser.stop()
                self.browser = None
                return False
            
            # Inicia a thread de processamento
            self.running = True
            self.processing_thread = threading.Thread(
                target=self._process_bet_queue,
                daemon=True
            )
            self.processing_thread.start()
            
            logger.info("Gerenciador de navegador iniciado com sucesso.")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao iniciar o gerenciador de navegador: {e}")
            if self.browser:
                self.browser.stop()
                self.browser = None
            return False
    
    def stop(self):
        """
        Para o gerenciador de navegador.
        """
        self.running = False
        
        # Aguarda a thread de processamento terminar
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5)
        
        # Para o navegador
        if self.browser:
            self.browser.stop()
            self.browser = None
        
        logger.info("Gerenciador de navegador parado com sucesso.")
    
    def add_bet_to_queue(self, bet: Bet):
        """
        Adiciona uma aposta à fila de processamento.
        
        Args:
            bet: Objeto Bet contendo os dados da aposta.
        """
        self.bet_queue.put(bet)
        logger.info(f"Aposta adicionada à fila: {bet.horse_name} - {bet.race}")
    
    def _process_bet_queue(self):
        """
        Processa a fila de apostas continuamente.
        """
        logger.info("Iniciando processador de fila de apostas")
        
        while self.running:
            try:
                # Tenta obter uma aposta da fila (com timeout para permitir verificação de self.running)
                try:
                    bet = self.bet_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Verifica se o navegador está ativo
                if not self.browser:
                    logger.error("Navegador não está ativo. Não é possível processar a aposta.")
                    continue
                
                # Atualiza o status da aposta para "processing"
                if bet.id:
                    self.db_client.update_bet_status(bet.id, "processing")
                
                # Captura screenshot antes da aposta
                screenshot_before = os.path.join(
                    self.screenshots_dir,
                    f"bet_{bet.id or datetime.now().strftime('%Y%m%d%H%M%S')}_before.png"
                )
                self.browser.take_screenshot(screenshot_before)
                
                # Realiza a aposta
                result = self.browser.place_bet(bet)
                
                # Captura screenshot após a aposta
                screenshot_after = os.path.join(
                    self.screenshots_dir,
                    f"bet_{bet.id or datetime.now().strftime('%Y%m%d%H%M%S')}_after.png"
                )
                self.browser.take_screenshot(screenshot_after)
                
                # Atualiza o status da aposta no banco de dados
                if bet.id:
                    if result["success"]:
                        self.db_client.update_bet_status(bet.id, "completed", result)
                        logger.info(f"Aposta {bet.id} concluída com sucesso.")
                    else:
                        self.db_client.update_bet_status(bet.id, "failed", result)
                        logger.error(f"Aposta {bet.id} falhou: {result.get('error', 'Erro desconhecido')}")
                
                # Registra a ação no log
                action_type = "bet_placed" if result["success"] else "bet_failed"
                description = f"Aposta em {bet.horse_name} na corrida {bet.race}"
                details = {
                    "result": result,
                    "screenshots": {
                        "before": screenshot_before,
                        "after": screenshot_after
                    }
                }
                
                self.db_client.log_action(action_type, description, bet.id, details)
                
                # Marca como processado na fila
                self.bet_queue.task_done()
                
                # Pequena pausa entre apostas
                time.sleep(2)
            
            except Exception as e:
                logger.error(f"Erro ao processar aposta da fila: {e}")
                time.sleep(5)  # Pausa maior em caso de erro
    
    def get_queue_size(self) -> int:
        """
        Retorna o tamanho atual da fila de apostas.
        
        Returns:
            int: Número de apostas na fila.
        """
        return self.bet_queue.qsize()
    
    def is_browser_active(self) -> bool:
        """
        Verifica se o navegador está ativo.
        
        Returns:
            bool: True se o navegador estiver ativo, False caso contrário.
        """
        return self.browser is not None
    
    def check_balance(self) -> Optional[float]:
        """
        Verifica o saldo da conta.
        
        Returns:
            float: Saldo atual ou None em caso de erro.
        """
        if not self.browser:
            logger.error("Navegador não está ativo. Não é possível verificar o saldo.")
            return None
        
        return self.browser.check_balance()


# Singleton para acesso global ao gerenciador de navegador
_browser_manager_instance = None

def get_browser_manager() -> BrowserManager:
    """
    Obtém a instância global do gerenciador de navegador.
    
    Returns:
        BrowserManager: Instância do gerenciador de navegador.
    """
    global _browser_manager_instance
    
    if _browser_manager_instance is None:
        _browser_manager_instance = BrowserManager()
    
    return _browser_manager_instance
