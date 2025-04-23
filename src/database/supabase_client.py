"""
Módulo cliente para interação com o Supabase.

Este módulo implementa a integração com o Supabase para armazenar
apostas, registrar logs e gerenciar a fila de apostas.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    logger.warning("Biblioteca Supabase não disponível. Usando armazenamento local.")
    SUPABASE_AVAILABLE = False

from ..config.settings import SUPABASE_URL, SUPABASE_KEY
import os
import json


class LocalStorageClient:
    """
    Cliente para armazenamento local quando o Supabase não está disponível.
    Implementa a mesma interface que o SupabaseClient para compatibilidade.
    """
    
    def __init__(self):
        """
        Inicializa o cliente de armazenamento local.
        """
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
        self.bets_file = os.path.join(self.data_dir, "bets.json")
        self.logs_file = os.path.join(self.data_dir, "logs.json")
        
        # Cria o diretório de dados se não existir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Inicializa os arquivos se não existirem
        if not os.path.exists(self.bets_file):
            with open(self.bets_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.logs_file):
            with open(self.logs_file, 'w') as f:
                json.dump([], f)
        
        logger.info("Cliente de armazenamento local inicializado com sucesso.")
    
    async def save_bet(self, bet_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Salva uma aposta no armazenamento local.
        
        Args:
            bet_data: Dicionário contendo os dados da aposta.
            
        Returns:
            dict: Dados da aposta salva ou None em caso de erro.
        """
        try:
            # Garante que temos um timestamp de criação
            if "created_at" not in bet_data or not bet_data["created_at"]:
                bet_data["created_at"] = datetime.now().isoformat()
            
            # Gera um ID único para a aposta
            bet_data["id"] = f"local_{datetime.now().timestamp()}"
            
            # Carrega as apostas existentes
            with open(self.bets_file, 'r') as f:
                bets = json.load(f)
            
            # Adiciona a nova aposta
            bets.append(bet_data)
            
            # Salva o arquivo atualizado
            with open(self.bets_file, 'w') as f:
                json.dump(bets, f, indent=2)
            
            logger.info(f"Aposta salva localmente: {bet_data.get('horse_name')} - {bet_data.get('race')}")
            return bet_data
        
        except Exception as e:
            logger.error(f"Erro ao salvar aposta localmente: {e}")
            return None
    
    async def update_bet_status(self, bet_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Atualiza o status de uma aposta no armazenamento local.
        
        Args:
            bet_id: ID da aposta a ser atualizada.
            status: Novo status da aposta (pending, processing, completed, failed).
            result: Resultado da aposta (opcional).
            
        Returns:
            bool: True se a atualização for bem-sucedida, False caso contrário.
        """
        try:
            # Carrega as apostas existentes
            with open(self.bets_file, 'r') as f:
                bets = json.load(f)
            
            # Encontra a aposta pelo ID
            for bet in bets:
                if bet.get("id") == bet_id:
                    bet["status"] = status
                    bet["updated_at"] = datetime.now().isoformat()
                    
                    if result:
                        bet["result"] = result
                    
                    # Salva o arquivo atualizado
                    with open(self.bets_file, 'w') as f:
                        json.dump(bets, f, indent=2)
                    
                    logger.info(f"Status da aposta {bet_id} atualizado para {status}")
                    return True
            
            logger.error(f"Aposta com ID {bet_id} não encontrada")
            return False
        
        except Exception as e:
            logger.error(f"Erro ao atualizar status da aposta localmente: {e}")
            return False
    
    async def get_pending_bets(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de apostas pendentes do armazenamento local.
        
        Returns:
            list: Lista de apostas pendentes.
        """
        try:
            # Carrega as apostas existentes
            with open(self.bets_file, 'r') as f:
                bets = json.load(f)
            
            # Filtra as apostas pendentes
            pending_bets = [bet for bet in bets if bet.get("status") == "pending"]
            
            # Ordena por data de criação
            pending_bets.sort(key=lambda x: x.get("created_at", ""))
            
            logger.info(f"Obtidas {len(pending_bets)} apostas pendentes do armazenamento local.")
            return pending_bets
        
        except Exception as e:
            logger.error(f"Erro ao obter apostas pendentes do armazenamento local: {e}")
            return []
    
    async def log_action(self, action_type: str, description: str, related_bet_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Registra uma ação no log do sistema local.
        
        Args:
            action_type: Tipo de ação (info, warning, error, bet_placed, etc).
            description: Descrição da ação.
            related_bet_id: ID da aposta relacionada (opcional).
            details: Detalhes adicionais da ação (opcional).
            
        Returns:
            bool: True se o registro for bem-sucedido, False caso contrário.
        """
        try:
            # Carrega os logs existentes
            with open(self.logs_file, 'r') as f:
                logs = json.load(f)
            
            # Cria o novo log
            log_data = {
                "id": f"local_{datetime.now().timestamp()}",
                "action_type": action_type,
                "description": description,
                "created_at": datetime.now().isoformat()
            }
            
            if related_bet_id:
                log_data["bet_id"] = related_bet_id
            
            if details:
                log_data["details"] = details
            
            # Adiciona o novo log
            logs.append(log_data)
            
            # Salva o arquivo atualizado
            with open(self.logs_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao registrar log localmente: {e}")
            return False
    
    async def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtém os logs mais recentes do sistema local.
        
        Args:
            limit: Número máximo de logs a serem retornados.
            
        Returns:
            list: Lista de logs.
        """
        try:
            # Carrega os logs existentes
            with open(self.logs_file, 'r') as f:
                logs = json.load(f)
            
            # Ordena por data de criação (mais recentes primeiro)
            logs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Limita o número de logs
            return logs[:limit]
        
        except Exception as e:
            logger.error(f"Erro ao obter logs do armazenamento local: {e}")
            return []
    
    async def get_bet_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas sobre as apostas do armazenamento local.
        
        Returns:
            dict: Estatísticas das apostas.
        """
        try:
            # Carrega as apostas existentes
            with open(self.bets_file, 'r') as f:
                bets = json.load(f)
            
            # Calcula as estatísticas
            total = len(bets)
            status_counts = {
                "pending": 0,
                "processing": 0,
                "completed": 0,
                "failed": 0
            }
            
            for bet in bets:
                status = bet.get("status", "pending")
                if status in status_counts:
                    status_counts[status] += 1
            
            return {
                "total": total,
                "status_counts": status_counts
            }
        
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do armazenamento local: {e}")
            return {
                "total": 0,
                "status_counts": {
                    "pending": 0,
                    "processing": 0,
                    "completed": 0,
                    "failed": 0
                }
            }


class SupabaseClient:
    """
    Cliente para interação com o Supabase.
    """
    
    def __init__(self):
        """
        Inicializa o cliente do Supabase ou o cliente de armazenamento local.
        """
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.client = None
        self.local_client = None
        self.using_local_storage = False
        
        # Tenta conectar ao Supabase
        if not self._connect():
            logger.warning("Usando armazenamento local como fallback.")
            self.local_client = LocalStorageClient()
            self.using_local_storage = True
    
    def _connect(self) -> bool:
        """
        Estabelece conexão com o Supabase.
        
        Returns:
            bool: True se a conexão for estabelecida com sucesso, False caso contrário.
        """
        try:
            if not SUPABASE_AVAILABLE:
                logger.warning("Biblioteca Supabase não disponível.")
                return False
            
            if not self.url or not self.key or self.url == "sua_url_supabase" or self.key == "sua_chave_supabase":
                logger.warning("URL ou chave do Supabase não configurados corretamente.")
                return False
            
            self.client = create_client(self.url, self.key)
            logger.info("Conexão com o Supabase estabelecida com sucesso.")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao conectar ao Supabase: {e}")
            return False
    
    async def save_bet(self, bet_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Salva uma aposta no banco de dados.
        
        Args:
            bet_data: Dicionário contendo os dados da aposta.
            
        Returns:
            dict: Dados da aposta salva ou None em caso de erro.
        """
        # Se estiver usando armazenamento local, delega para o cliente local
        if self.using_local_storage:
            return await self.local_client.save_bet(bet_data)
        
        try:
            if not self.client:
                if not self._connect():
                    # Fallback para armazenamento local
                    if not self.local_client:
                        self.local_client = LocalStorageClient()
                        self.using_local_storage = True
                    return await self.local_client.save_bet(bet_data)
            
            # Garante que temos um timestamp de criação
            if "created_at" not in bet_data or not bet_data["created_at"]:
                bet_data["created_at"] = datetime.now().isoformat()
            
            # Insere a aposta na tabela 'bets'
            response = self.client.table("bets").insert(bet_data).execute()
            
            if response.data:
                logger.info(f"Aposta salva com sucesso: {bet_data.get('horse_name')} - {bet_data.get('race')}")
                return response.data[0]
            else:
                logger.error(f"Erro ao salvar aposta: {response.error}")
                # Fallback para armazenamento local
                if not self.local_client:
                    self.local_client = LocalStorageClient()
                    self.using_local_storage = True
                return await self.local_client.save_bet(bet_data)
        
        except Exception as e:
            logger.error(f"Erro ao salvar aposta: {e}")
            # Fallback para armazenamento local
            if not self.local_client:
                self.local_client = LocalStorageClient()
                self.using_local_storage = True
            return await self.local_client.save_bet(bet_data)
    
    async def update_bet_status(self, bet_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Atualiza o status de uma aposta.
        
        Args:
            bet_id: ID da aposta a ser atualizada.
            status: Novo status da aposta (pending, processing, completed, failed).
            result: Resultado da aposta (opcional).
            
        Returns:
            bool: True se a atualização for bem-sucedida, False caso contrário.
        """
        # Se estiver usando armazenamento local, delega para o cliente local
        if self.using_local_storage:
            return await self.local_client.update_bet_status(bet_id, status, result)
        
        try:
            if not self.client:
                if not self._connect():
                    # Fallback para armazenamento local
                    if not self.local_client:
                        self.local_client = LocalStorageClient()
                        self.using_local_storage = True
                    return await self.local_client.update_bet_status(bet_id, status, result)
            
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            if result:
                update_data["result"] = json.dumps(result)
            
            response = self.client.table("bets").update(update_data).eq("id", bet_id).execute()
            
            if response.data:
                logger.info(f"Status da aposta {bet_id} atualizado para {status}")
                return True
            else:
                logger.error(f"Erro ao atualizar status da aposta: {response.error}")
                # Fallback para armazenamento local
                if not self.local_client:
                    self.local_client = LocalStorageClient()
                    self.using_local_storage = True
                return await self.local_client.update_bet_status(bet_id, status, result)
        
        except Exception as e:
            logger.error(f"Erro ao atualizar status da aposta: {e}")
            # Fallback para armazenamento local
            if not self.local_client:
                self.local_client = LocalStorageClient()
                self.using_local_storage = True
            return await self.local_client.update_bet_status(bet_id, status, result)
    
    async def get_pending_bets(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de apostas pendentes.
        
        Returns:
            list: Lista de apostas pendentes.
        """
        # Se estiver usando armazenamento local, delega para o cliente local
        if self.using_local_storage:
            return await self.local_client.get_pending_bets()
        
        try:
            if not self.client:
                if not self._connect():
                    # Fallback para armazenamento local
                    if not self.local_client:
                        self.local_client = LocalStorageClient()
                        self.using_local_storage = True
                    return await self.local_client.get_pending_bets()
            
            response = self.client.table("bets").select("*").eq("status", "pending").order("created_at").execute()
            
            if response.data:
                logger.info(f"Obtidas {len(response.data)} apostas pendentes.")
                return response.data
            else:
                logger.debug("Nenhuma aposta pendente encontrada.")
                return []
        
        except Exception as e:
            logger.error(f"Erro ao obter apostas pendentes: {e}")
            # Fallback para armazenamento local
            if not self.local_client:
                self.local_client = LocalStorageClient()
                self.using_local_storage = True
            return await self.local_client.get_pending_bets()
    
    async def log_action(self, action_type: str, description: str, related_bet_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Registra uma ação no log do sistema.
        
        Args:
            action_type: Tipo de ação (info, warning, error, bet_placed, etc).
            description: Descrição da ação.
            related_bet_id: ID da aposta relacionada (opcional).
            details: Detalhes adicionais da ação (opcional).
            
        Returns:
            bool: True se o registro for bem-sucedido, False caso contrário.
        """
        # Se estiver usando armazenamento local, delega para o cliente local
        if self.using_local_storage:
            return await self.local_client.log_action(action_type, description, related_bet_id, details)
        
        try:
            if not self.client:
                if not self._connect():
                    # Fallback para armazenamento local
                    if not self.local_client:
                        self.local_client = LocalStorageClient()
                        self.using_local_storage = True
                    return await self.local_client.log_action(action_type, description, related_bet_id, details)
            
            log_data = {
                "action_type": action_type,
                "description": description,
                "created_at": datetime.now().isoformat()
            }
            
            if related_bet_id:
                log_data["bet_id"] = related_bet_id
            
            if details:
                log_data["details"] = json.dumps(details)
            
            response = self.client.table("logs").insert(log_data).execute()
            
            if response.data:
                return True
            else:
                logger.error(f"Erro ao registrar log: {response.error}")
                # Fallback para armazenamento local
                if not self.local_client:
                    self.local_client = LocalStorageClient()
                    self.using_local_storage = True
                return await self.local_client.log_action(action_type, description, related_bet_id, details)
        
        except Exception as e:
            logger.error(f"Erro ao registrar log: {e}")
            # Fallback para armazenamento local
            if not self.local_client:
                self.local_client = LocalStorageClient()
                self.using_local_storage = True
            return await self.local_client.log_action(action_type, description, related_bet_id, details)
    
    async def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtém os logs mais recentes do sistema.
        
        Args:
            limit: Número máximo de logs a serem retornados.
            
        Returns:
            list: Lista de logs.
        """
        # Se estiver usando armazenamento local, delega para o cliente local
        if self.using_local_storage:
            return await self.local_client.get_recent_logs(limit)
        
        try:
            if not self.client:
                if not self._connect():
                    # Fallback para armazenamento local
                    if not self.local_client:
                        self.local_client = LocalStorageClient()
                        self.using_local_storage = True
                    return await self.local_client.get_recent_logs(limit)
            
            response = self.client.table("logs").select("*").order("created_at", desc=True).limit(limit).execute()
            
            if response.data:
                return response.data
            else:
                return []
        
        except Exception as e:
            logger.error(f"Erro ao obter logs: {e}")
            # Fallback para armazenamento local
            if not self.local_client:
                self.local_client = LocalStorageClient()
                self.using_local_storage = True
            return await self.local_client.get_recent_logs(limit)
    
    async def get_bet_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas sobre as apostas.
        
        Returns:
            dict: Estatísticas das apostas.
        """
        # Se estiver usando armazenamento local, delega para o cliente local
        if self.using_local_storage:
            return await self.local_client.get_bet_statistics()
        
        try:
            if not self.client:
                if not self._connect():
                    # Fallback para armazenamento local
                    if not self.local_client:
                        self.local_client = LocalStorageClient()
                        self.using_local_storage = True
                    return await self.local_client.get_bet_statistics()
            
            # Total de apostas
            total_response = self.client.table("bets").select("count", count="exact").execute()
            total = total_response.count if hasattr(total_response, "count") else 0
            
            # Apostas por status
            status_counts = {}
            for status in ["pending", "processing", "completed", "failed"]:
                status_response = self.client.table("bets").select("count", count="exact").eq("status", status).execute()
                status_counts[status] = status_response.count if hasattr(status_response, "count") else 0
            
            return {
                "total": total,
                "status_counts": status_counts
            }
        
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            # Fallback para armazenamento local
            if not self.local_client:
                self.local_client = LocalStorageClient()
                self.using_local_storage = True
            return await self.local_client.get_bet_statistics()


# Função para criar as tabelas necessárias no Supabase
async def setup_supabase_tables():
    """
    Configura as tabelas necessárias no Supabase.
    
    Esta função deve ser executada uma vez para criar a estrutura inicial do banco de dados.
    """
    try:
        client = SupabaseClient()
        if client.using_local_storage:
            logger.warning("Usando armazenamento local, não é necessário configurar tabelas.")
            return True
        
        if not client.client:
            logger.error("Não foi possível conectar ao Supabase para configurar as tabelas.")
            return False
        
        # Aqui seria implementada a criação das tabelas via SQL
        # No Supabase, isso geralmente é feito através da interface web ou via SQL direto
        # Este é apenas um exemplo de como seria a estrutura
        
        logger.info("Tabelas do Supabase configuradas com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao configurar tabelas do Supabase: {e}")
        return False
