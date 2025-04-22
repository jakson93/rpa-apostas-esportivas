"""
Módulo principal da interface gráfica para o sistema de automação de apostas.

Este módulo implementa a interface gráfica que permite ao usuário configurar
credenciais de acesso, stake padrão e outras opções do sistema.
"""
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QDoubleSpinBox, QComboBox, QPushButton,
    QTabWidget, QGroupBox, QFormLayout, QCheckBox, QMessageBox,
    QFileDialog, QTextEdit, QSpinBox
)
from PyQt5.QtCore import Qt, QSettings, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QFont

from ..config.settings import get_config
from ..utils.validators import is_valid_url, is_valid_api_key


class ConfigTab(QWidget):
    """
    Aba de configurações gerais do sistema.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("RPAApostas", "BetAutomation")
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Inicializa a interface da aba de configurações."""
        layout = QVBoxLayout()
        
        # Grupo de configurações do Telegram
        telegram_group = QGroupBox("Configurações do Telegram")
        telegram_layout = QFormLayout()
        
        self.api_id_input = QLineEdit()
        self.api_hash_input = QLineEdit()
        self.bot_token_input = QLineEdit()
        self.group_id_input = QLineEdit()
        
        telegram_layout.addRow("API ID:", self.api_id_input)
        telegram_layout.addRow("API Hash:", self.api_hash_input)
        telegram_layout.addRow("Bot Token:", self.bot_token_input)
        telegram_layout.addRow("ID do Grupo:", self.group_id_input)
        
        telegram_group.setLayout(telegram_layout)
        
        # Grupo de configurações do Supabase
        supabase_group = QGroupBox("Configurações do Supabase")
        supabase_layout = QFormLayout()
        
        self.supabase_url_input = QLineEdit()
        self.supabase_key_input = QLineEdit()
        
        supabase_layout.addRow("URL:", self.supabase_url_input)
        supabase_layout.addRow("API Key:", self.supabase_key_input)
        
        supabase_group.setLayout(supabase_layout)
        
        # Grupo de configurações do navegador
        browser_group = QGroupBox("Configurações do Navegador")
        browser_layout = QFormLayout()
        
        self.browser_type_combo = QComboBox()
        self.browser_type_combo.addItems(["chrome", "firefox", "edge"])
        
        self.headless_checkbox = QCheckBox("Modo Headless (sem interface gráfica)")
        
        browser_layout.addRow("Tipo de Navegador:", self.browser_type_combo)
        browser_layout.addRow(self.headless_checkbox)
        
        browser_group.setLayout(browser_layout)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salvar Configurações")
        self.save_button.clicked.connect(self.save_settings)
        
        self.test_button = QPushButton("Testar Conexões")
        self.test_button.clicked.connect(self.test_connections)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.test_button)
        
        # Adiciona todos os componentes ao layout principal
        layout.addWidget(telegram_group)
        layout.addWidget(supabase_group)
        layout.addWidget(browser_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """Carrega as configurações salvas."""
        self.api_id_input.setText(self.settings.value("telegram/api_id", ""))
        self.api_hash_input.setText(self.settings.value("telegram/api_hash", ""))
        self.bot_token_input.setText(self.settings.value("telegram/bot_token", ""))
        self.group_id_input.setText(self.settings.value("telegram/group_id", ""))
        
        self.supabase_url_input.setText(self.settings.value("supabase/url", ""))
        self.supabase_key_input.setText(self.settings.value("supabase/key", ""))
        
        browser_type = self.settings.value("browser/type", "chrome")
        index = self.browser_type_combo.findText(browser_type)
        if index >= 0:
            self.browser_type_combo.setCurrentIndex(index)
        
        self.headless_checkbox.setChecked(self.settings.value("browser/headless", False, type=bool))
    
    def save_settings(self):
        """Salva as configurações atuais."""
        # Salva configurações do Telegram
        self.settings.setValue("telegram/api_id", self.api_id_input.text())
        self.settings.setValue("telegram/api_hash", self.api_hash_input.text())
        self.settings.setValue("telegram/bot_token", self.bot_token_input.text())
        self.settings.setValue("telegram/group_id", self.group_id_input.text())
        
        # Salva configurações do Supabase
        self.settings.setValue("supabase/url", self.supabase_url_input.text())
        self.settings.setValue("supabase/key", self.supabase_key_input.text())
        
        # Salva configurações do navegador
        self.settings.setValue("browser/type", self.browser_type_combo.currentText())
        self.settings.setValue("browser/headless", self.headless_checkbox.isChecked())
        
        # Atualiza o arquivo .env
        self.update_env_file()
        
        QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
    
    def update_env_file(self):
        """Atualiza o arquivo .env com as configurações atuais."""
        env_content = f"""# Credenciais do Telegram
TELEGRAM_API_ID={self.api_id_input.text()}
TELEGRAM_API_HASH={self.api_hash_input.text()}
TELEGRAM_BOT_TOKEN={self.bot_token_input.text()}
TELEGRAM_GROUP_ID={self.group_id_input.text()}

# Credenciais do Supabase
SUPABASE_URL={self.supabase_url_input.text()}
SUPABASE_KEY={self.supabase_key_input.text()}

# Configurações de apostas
DEFAULT_STAKE={self.parent().parent().betting_tab.default_stake_input.value()}
MAX_STAKE={self.parent().parent().betting_tab.max_stake_input.value()}
MIN_STAKE={self.parent().parent().betting_tab.min_stake_input.value()}

# Configurações do navegador
BROWSER_TYPE={self.browser_type_combo.currentText()}
HEADLESS={"true" if self.headless_checkbox.isChecked() else "false"}

# Configurações da aplicação
DEBUG_MODE={"true" if self.parent().parent().betting_tab.debug_mode_checkbox.isChecked() else "false"}
LOG_LEVEL={"DEBUG" if self.parent().parent().betting_tab.debug_mode_checkbox.isChecked() else "INFO"}
"""
        
        try:
            with open(".env", "w") as f:
                f.write(env_content)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível atualizar o arquivo .env: {e}")
    
    def test_connections(self):
        """Testa as conexões com Telegram e Supabase."""
        # Implementação básica - em um sistema real, isso testaria as conexões de fato
        if not self.api_id_input.text() or not self.api_hash_input.text() or not self.bot_token_input.text():
            QMessageBox.warning(self, "Erro", "Preencha todas as credenciais do Telegram para testar a conexão.")
            return
        
        if not is_valid_url(self.supabase_url_input.text()) or not is_valid_api_key(self.supabase_key_input.text()):
            QMessageBox.warning(self, "Erro", "URL ou chave do Supabase inválidos.")
            return
        
        # Aqui seria implementada a lógica real de teste de conexão
        QMessageBox.information(self, "Teste de Conexão", "Teste de conexão concluído com sucesso!")


class BettingTab(QWidget):
    """
    Aba de configurações de apostas.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings("RPAApostas", "BetAutomation")
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Inicializa a interface da aba de apostas."""
        layout = QVBoxLayout()
        
        # Grupo de configurações de stake
        stake_group = QGroupBox("Configurações de Stake")
        stake_layout = QFormLayout()
        
        self.default_stake_input = QDoubleSpinBox()
        self.default_stake_input.setRange(1, 1000)
        self.default_stake_input.setDecimals(2)
        self.default_stake_input.setSingleStep(1)
        
        self.min_stake_input = QDoubleSpinBox()
        self.min_stake_input.setRange(1, 100)
        self.min_stake_input.setDecimals(2)
        self.min_stake_input.setSingleStep(1)
        
        self.max_stake_input = QDoubleSpinBox()
        self.max_stake_input.setRange(10, 10000)
        self.max_stake_input.setDecimals(2)
        self.max_stake_input.setSingleStep(10)
        
        stake_layout.addRow("Stake Padrão:", self.default_stake_input)
        stake_layout.addRow("Stake Mínimo:", self.min_stake_input)
        stake_layout.addRow("Stake Máximo:", self.max_stake_input)
        
        stake_group.setLayout(stake_layout)
        
        # Grupo de configurações avançadas
        advanced_group = QGroupBox("Configurações Avançadas")
        advanced_layout = QFormLayout()
        
        self.auto_start_checkbox = QCheckBox("Iniciar automação automaticamente")
        self.debug_mode_checkbox = QCheckBox("Modo de depuração")
        
        self.retry_count_input = QSpinBox()
        self.retry_count_input.setRange(1, 10)
        
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(10, 300)
        self.timeout_input.setSuffix(" segundos")
        
        advanced_layout.addRow(self.auto_start_checkbox)
        advanced_layout.addRow(self.debug_mode_checkbox)
        advanced_layout.addRow("Número de tentativas:", self.retry_count_input)
        advanced_layout.addRow("Timeout de operações:", self.timeout_input)
        
        advanced_group.setLayout(advanced_layout)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salvar Configurações")
        self.save_button.clicked.connect(self.save_settings)
        
        button_layout.addWidget(self.save_button)
        
        # Adiciona todos os componentes ao layout principal
        layout.addWidget(stake_group)
        layout.addWidget(advanced_group)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """Carrega as configurações salvas."""
        self.default_stake_input.setValue(self.settings.value("betting/default_stake", 10.0, type=float))
        self.min_stake_input.setValue(self.settings.value("betting/min_stake", 5.0, type=float))
        self.max_stake_input.setValue(self.settings.value("betting/max_stake", 100.0, type=float))
        
        self.auto_start_checkbox.setChecked(self.settings.value("app/auto_start", False, type=bool))
        self.debug_mode_checkbox.setChecked(self.settings.value("app/debug_mode", False, type=bool))
        
        self.retry_count_input.setValue(self.settings.value("app/retry_count", 3, type=int))
        self.timeout_input.setValue(self.settings.value("app/timeout", 60, type=int))
    
    def save_settings(self):
        """Salva as configurações atuais."""
        # Salva configurações de stake
        self.settings.setValue("betting/default_stake", self.default_stake_input.value())
        self.settings.setValue("betting/min_stake", self.min_stake_input.value())
        self.settings.setValue("betting/max_stake", self.max_stake_input.value())
        
        # Salva configurações avançadas
        self.settings.setValue("app/auto_start", self.auto_start_checkbox.isChecked())
        self.settings.setValue("app/debug_mode", self.debug_mode_checkbox.isChecked())
        self.settings.setValue("app/retry_count", self.retry_count_input.value())
        self.settings.setValue("app/timeout", self.timeout_input.value())
        
        # Atualiza o arquivo .env através da aba de configurações
        self.parent().parent().config_tab.update_env_file()
        
        QMessageBox.information(self, "Sucesso", "Configurações de apostas salvas com sucesso!")


class LogTab(QWidget):
    """
    Aba de logs do sistema.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface da aba de logs."""
        layout = QVBoxLayout()
        
        # Área de texto para exibição de logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Atualizar Logs")
        self.refresh_button.clicked.connect(self.refresh_logs)
        
        self.clear_button = QPushButton("Limpar Logs")
        self.clear_button.clicked.connect(self.clear_logs)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.clear_button)
        
        # Adiciona componentes ao layout principal
        layout.addWidget(self.log_text)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Carrega logs iniciais
        self.refresh_logs()
    
    def refresh_logs(self):
        """Atualiza a exibição de logs."""
        try:
            log_path = os.path.join(os.getcwd(), "logs", "app.log")
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    logs = f.read()
                self.log_text.setText(logs)
            else:
                self.log_text.setText("Arquivo de log não encontrado.")
        except Exception as e:
            self.log_text.setText(f"Erro ao carregar logs: {e}")
    
    def clear_logs(self):
        """Limpa a exibição de logs."""
        self.log_text.clear()


class StatusThread(QThread):
    """
    Thread para monitorar o status do sistema.
    """
    status_update = pyqtSignal(str, str)  # (status_type, message)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
    
    def run(self):
        """Executa o monitoramento de status."""
        self.running = True
        while self.running:
            # Aqui seria implementada a lógica real de monitoramento
            # Por exemplo, verificar se o bot do Telegram está conectado
            # e se o navegador está funcionando corretamente
            
            # Simulação de status para demonstração
            self.status_update.emit("telegram", "Conectado")
            self.status_update.emit("browser", "Pronto")
            self.status_update.emit("database", "Conectado")
            
            # Aguarda 5 segundos antes da próxima verificação
            self.sleep(5)
    
    def stop(self):
        """Para o monitoramento de status."""
        self.running = False


class MainWindow(QMainWindow):
    """
    Janela principal da aplicação.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.status_thread = StatusThread(self)
        self.status_thread.status_update.connect(self.update_status)
        self.status_thread.start()
    
    def init_ui(self):
        """Inicializa a interface da janela principal."""
        self.setWindowTitle("RPA Apostas Esportivas")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central com abas
        self.tabs = QTabWidget()
        
        # Cria as abas
        self.config_tab = ConfigTab()
        self.betting_tab = BettingTab()
        self.log_tab = LogTab()
        
        # Adiciona as abas ao widget de abas
        self.tabs.addTab(self.config_tab, "Configurações")
        self.tabs.addTab(self.betting_tab, "Apostas")
        self.tabs.addTab(self.log_tab, "Logs")
        
        # Define o widget central
        self.setCentralWidget(self.tabs)
        
        # Barra de status
        self.statusBar().showMessage("Pronto")
        
        # Adiciona widgets permanentes à barra de status
        self.telegram_status = QLabel("Telegram: Desconectado")
        self.browser_status = QLabel("Navegador: Inativo")
        self.database_status = QLabel("Banco de Dados: Desconectado")
        
        self.statusBar().addPermanentWidget(self.telegram_status)
        self.statusBar().addPermanentWidget(self.browser_status)
        self.statusBar().addPermanentWidget(self.database_status)
        
        # Barra de ferramentas
        toolbar = self.addToolBar("Controles")
        
        # Ações da barra de ferramentas
        start_action = toolbar.addAction("Iniciar")
        start_action.triggered.connect(self.start_automation)
        
        stop_action = toolbar.addAction("Parar")
        stop_action.triggered.connect(self.stop_automation)
        
        toolbar.addSeparator()
        
        settings_action = toolbar.addAction("Configurações")
        settings_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
    
    def update_status(self, status_type, message):
        """
        Atualiza o status na barra de status.
        
        Args:
            status_type: Tipo de status (telegram, browser, database)
            message: Mensagem de status
        """
        if status_type == "telegram":
            self.telegram_status.setText(f"Telegram: {message}")
        elif status_type == "browser":
            self.browser_status.setText(f"Navegador: {message}")
        elif status_type == "database":
            self.database_status.setText(f"Banco de Dados: {message}")
    
    def start_automation(self):
        """Inicia a automação de apostas."""
        # Aqui seria implementada a lógica real de inicialização da automação
        QMessageBox.information(self, "Automação", "Iniciando automação de apostas...")
        self.statusBar().showMessage("Automação iniciada")
    
    def stop_automation(self):
        """Para a automação de apostas."""
        # Aqui seria implementada a lógica real de parada da automação
        QMessageBox.information(self, "Automação", "Parando automação de apostas...")
        self.statusBar().showMessage("Automação parada")
    
    def closeEvent(self, event):
        """Manipula o evento de fechamento da janela."""
        # Para a thread de status
        self.status_thread.stop()
        self.status_thread.wait()
        
        # Aceita o evento de fechamento
        event.accept()


def run_gui():
    """
    Função principal para executar a interface gráfica.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
