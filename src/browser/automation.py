"""
Módulo principal para automação do navegador.

Este módulo implementa a automação do navegador para interagir
com o site de apostas esportivas.
"""
from typing import Dict, Any, Optional, List, Tuple
import time
import re
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException,
    StaleElementReferenceException, WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from ..config.settings import BROWSER_TYPE, HEADLESS
from ..database.schemas import Bet


class BrowserAutomation:
    """
    Classe para automação do navegador para interagir com o site de apostas.
    """
    
    # URL base do site de apostas
    BASE_URL = "https://bolsadeaposta.bet.br/dsbook/euro/sport/horseracing"
    
    def __init__(self, headless: Optional[bool] = None):
        """
        Inicializa a automação do navegador.
        
        Args:
            headless: Se True, executa o navegador em modo headless (sem interface gráfica).
                     Se None, usa a configuração global.
        """
        self.browser_type = BROWSER_TYPE.lower()
        self.headless = headless if headless is not None else HEADLESS
        self.driver = None
        self.logged_in = False
        self.timeout = 30  # Timeout padrão em segundos
    
    def start(self) -> bool:
        """
        Inicia o navegador.
        
        Returns:
            bool: True se o navegador foi iniciado com sucesso, False caso contrário.
        """
        try:
            if self.browser_type == "chrome":
                options = ChromeOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options
                )
            
            elif self.browser_type == "firefox":
                options = FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                
                self.driver = webdriver.Firefox(
                    service=Service(GeckoDriverManager().install()),
                    options=options
                )
            
            elif self.browser_type == "edge":
                options = EdgeOptions()
                if self.headless:
                    options.add_argument("--headless")
                
                self.driver = webdriver.Edge(
                    service=Service(EdgeChromiumDriverManager().install()),
                    options=options
                )
            
            else:
                logger.error(f"Tipo de navegador não suportado: {self.browser_type}")
                return False
            
            self.driver.maximize_window()
            logger.info(f"Navegador {self.browser_type} iniciado com sucesso.")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao iniciar o navegador: {e}")
            return False
    
    def stop(self):
        """
        Para o navegador.
        """
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Navegador fechado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao fechar o navegador: {e}")
            
            self.driver = None
            self.logged_in = False
    
    def login(self, username: str, password: str) -> bool:
        """
        Realiza login no site de apostas.
        
        Args:
            username: Nome de usuário.
            password: Senha.
            
        Returns:
            bool: True se o login foi bem-sucedido, False caso contrário.
        """
        if not self.driver:
            if not self.start():
                return False
        
        try:
            # Navega para a página inicial
            self.driver.get(self.BASE_URL)
            
            # Aguarda a página carregar
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Verifica se já está logado
            if self._is_logged_in():
                logger.info("Usuário já está logado.")
                self.logged_in = True
                return True
            
            # Clica no botão de login
            login_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.login-button, a.login-link"))
            )
            login_button.click()
            
            # Aguarda o formulário de login
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form.login-form, div.login-container"))
            )
            
            # Preenche o nome de usuário
            username_input = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'], input[name='username']"))
            )
            username_input.clear()
            username_input.send_keys(username)
            
            # Preenche a senha
            password_input = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password'], input[name='password']"))
            )
            password_input.clear()
            password_input.send_keys(password)
            
            # Clica no botão de submit
            submit_button = WebDriverWait(self.driver, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
            )
            submit_button.click()
            
            # Aguarda o login ser concluído
            time.sleep(3)
            
            # Verifica se o login foi bem-sucedido
            if self._is_logged_in():
                logger.info("Login realizado com sucesso.")
                self.logged_in = True
                return True
            else:
                logger.error("Falha ao realizar login. Verifique as credenciais.")
                return False
        
        except Exception as e:
            logger.error(f"Erro ao realizar login: {e}")
            return False
    
    def _is_logged_in(self) -> bool:
        """
        Verifica se o usuário está logado.
        
        Returns:
            bool: True se o usuário estiver logado, False caso contrário.
        """
        try:
            # Verifica a presença de elementos que indicam que o usuário está logado
            # Isso pode variar dependendo do site específico
            logged_in_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.user-info, span.username, button.logout")
            
            return len(logged_in_elements) > 0
        
        except Exception as e:
            logger.error(f"Erro ao verificar status de login: {e}")
            return False
    
    def navigate_to_race(self, race_name: str) -> bool:
        """
        Navega para a página de uma corrida específica.
        
        Args:
            race_name: Nome da corrida.
            
        Returns:
            bool: True se a navegação foi bem-sucedida, False caso contrário.
        """
        if not self.driver:
            logger.error("Navegador não iniciado.")
            return False
        
        if not self.logged_in:
            logger.error("Usuário não está logado.")
            return False
        
        try:
            # Navega para a página principal de corridas de cavalos
            self.driver.get(self.BASE_URL)
            
            # Aguarda a página carregar
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Procura pela corrida na lista
            race_elements = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.race-item, a.race-link"))
            )
            
            for element in race_elements:
                if race_name.lower() in element.text.lower():
                    element.click()
                    logger.info(f"Navegou para a corrida: {race_name}")
                    
                    # Aguarda a página da corrida carregar
                    WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.race-details, div.horses-list"))
                    )
                    
                    return True
            
            logger.error(f"Corrida não encontrada: {race_name}")
            return False
        
        except Exception as e:
            logger.error(f"Erro ao navegar para a corrida: {e}")
            return False
    
    def find_horse(self, horse_name: str) -> Optional[Tuple[Any, float]]:
        """
        Encontra um cavalo na página atual.
        
        Args:
            horse_name: Nome do cavalo.
            
        Returns:
            tuple: (elemento do cavalo, odds atual) ou None se não encontrado.
        """
        if not self.driver:
            logger.error("Navegador não iniciado.")
            return None
        
        try:
            # Procura por todos os elementos de cavalos na página
            horse_elements = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.horse-item, tr.horse-row"))
            )
            
            for element in horse_elements:
                # Verifica se o nome do cavalo está presente no elemento
                if horse_name.lower() in element.text.lower():
                    # Tenta encontrar o elemento de odds
                    try:
                        odds_element = element.find_element(By.CSS_SELECTOR, "span.odds, div.odds")
                        odds_text = odds_element.text.strip()
                        
                        # Extrai o valor numérico das odds
                        odds_match = re.search(r"(\d+\.?\d*)", odds_text)
                        if odds_match:
                            odds = float(odds_match.group(1))
                            logger.info(f"Cavalo encontrado: {horse_name} com odds {odds}")
                            return (element, odds)
                    
                    except (NoSuchElementException, ValueError) as e:
                        logger.warning(f"Erro ao extrair odds para o cavalo {horse_name}: {e}")
            
            logger.error(f"Cavalo não encontrado: {horse_name}")
            return None
        
        except Exception as e:
            logger.error(f"Erro ao procurar cavalo: {e}")
            return None
    
    def place_bet(self, bet: Bet) -> Dict[str, Any]:
        """
        Realiza uma aposta.
        
        Args:
            bet: Objeto Bet contendo os dados da aposta.
            
        Returns:
            dict: Resultado da aposta com status e detalhes.
        """
        if not self.driver:
            return {"success": False, "error": "Navegador não iniciado."}
        
        if not self.logged_in:
            return {"success": False, "error": "Usuário não está logado."}
        
        try:
            # Navega para a corrida
            if not self.navigate_to_race(bet.race):
                return {"success": False, "error": f"Corrida não encontrada: {bet.race}"}
            
            # Encontra o cavalo
            horse_result = self.find_horse(bet.horse_name)
            if not horse_result:
                return {"success": False, "error": f"Cavalo não encontrado: {bet.horse_name}"}
            
            horse_element, current_odds = horse_result
            
            # Clica no cavalo para selecioná-lo
            horse_element.click()
            
            # Aguarda o painel de apostas aparecer
            bet_slip = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.bet-slip, div.betting-panel"))
            )
            
            # Preenche o valor da stake
            stake_input = WebDriverWait(bet_slip, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input.stake-input, input[type='number']"))
            )
            stake_input.clear()
            stake_input.send_keys(str(bet.stake))
            
            # Clica no botão de confirmar aposta
            confirm_button = WebDriverWait(bet_slip, self.timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.place-bet, button.confirm-bet"))
            )
            confirm_button.click()
            
            # Aguarda a confirmação da aposta
            time.sleep(2)
            
            # Verifica se a aposta foi confirmada
            success_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.bet-success, div.confirmation-message")
            
            if success_elements:
                logger.info(f"Aposta realizada com sucesso: {bet.horse_name} na corrida {bet.race}")
                return {
                    "success": True,
                    "message": "Aposta realizada com sucesso",
                    "details": {
                        "horse": bet.horse_name,
                        "race": bet.race,
                        "odds": current_odds,
                        "stake": bet.stake,
                        "potential_return": current_odds * bet.stake
                    }
                }
            else:
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.bet-error, div.error-message")
                error_message = error_elements[0].text if error_elements else "Erro desconhecido ao confirmar aposta"
                
                logger.error(f"Erro ao realizar aposta: {error_message}")
                return {"success": False, "error": error_message}
        
        except Exception as e:
            logger.error(f"Erro ao realizar aposta: {e}")
            return {"success": False, "error": str(e)}
    
    def check_balance(self) -> Optional[float]:
        """
        Verifica o saldo da conta.
        
        Returns:
            float: Saldo atual ou None em caso de erro.
        """
        if not self.driver:
            logger.error("Navegador não iniciado.")
            return None
        
        if not self.logged_in:
            logger.error("Usuário não está logado.")
            return None
        
        try:
            # Procura pelo elemento que contém o saldo
            balance_element = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.balance, div.user-balance"))
            )
            
            balance_text = balance_element.text.strip()
            
            # Extrai o valor numérico do saldo
            balance_match = re.search(r"(\d+\.?\d*)", balance_text)
            if balance_match:
                balance = float(balance_match.group(1))
                logger.info(f"Saldo atual: {balance}")
                return balance
            
            logger.error(f"Não foi possível extrair o saldo do texto: {balance_text}")
            return None
        
        except Exception as e:
            logger.error(f"Erro ao verificar saldo: {e}")
            return None
    
    def take_screenshot(self, filename: str) -> bool:
        """
        Captura uma screenshot da página atual.
        
        Args:
            filename: Nome do arquivo para salvar a screenshot.
            
        Returns:
            bool: True se a screenshot foi capturada com sucesso, False caso contrário.
        """
        if not self.driver:
            logger.error("Navegador não iniciado.")
            return False
        
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot salva em: {filename}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao capturar screenshot: {e}")
            return False
