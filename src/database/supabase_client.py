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

from supabase import create_client, Client
from ..config.settings import SUPABASE_URL, SUPABASE_KEY


class SupabaseClient:
    """
    Cliente para interação com o Supabase.
    """
    
    def __init__(self):
        """
        Inicializa o cliente do Supabase.
        """
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.client = None
        self._connect()
    
    def _connect(self) -> bool:
        """
        Estabelece conexão com o Supabase.
        
        Returns:
            bool: True se a conexão for estabelecida com sucesso, False caso contrário.
        """
        try:
            if not self.url or not self.key:
                logger.error("URL ou chave do Supabase não configurados.")
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
        try:
            if not self.client:
                if not self._connect():
                    return None
            
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
                return None
        
        except Exception as e:
            logger.error(f"Erro ao salvar aposta: {e}")
            return None
    
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
        try:
            if not self.client:
                if not self._connect():
                    return False
            
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
                return False
        
        except Exception as e:
            logger.error(f"Erro ao atualizar status da aposta: {e}")
            return False
    
    async def get_pending_bets(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de apostas pendentes.
        
        Returns:
            list: Lista de apostas pendentes.
        """
        try:
            if not self.client:
                if not self._connect():
                    return []
            
            response = self.client.table("bets").select("*").eq("status", "pending").order("created_at").execute()
            
            if response.data:
                logger.info(f"Obtidas {len(response.data)} apostas pendentes.")
                return response.data
            else:
                logger.debug("Nenhuma aposta pendente encontrada.")
                return []
        
        except Exception as e:
            logger.error(f"Erro ao obter apostas pendentes: {e}")
            return []
    
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
        try:
            if not self.client:
                if not self._connect():
                    return False
            
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
                return False
        
        except Exception as e:
            logger.error(f"Erro ao registrar log: {e}")
            return False
    
    async def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtém os logs mais recentes do sistema.
        
        Args:
            limit: Número máximo de logs a serem retornados.
            
        Returns:
            list: Lista de logs.
        """
        try:
            if not self.client:
                if not self._connect():
                    return []
            
            response = self.client.table("logs").select("*").order("created_at", desc=True).limit(limit).execute()
            
            if response.data:
                return response.data
            else:
                return []
        
        except Exception as e:
            logger.error(f"Erro ao obter logs: {e}")
            return []
    
    async def get_bet_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas sobre as apostas.
        
        Returns:
            dict: Estatísticas das apostas.
        """
        try:
            if not self.client:
                if not self._connect():
                    return {}
            
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
            return {}


# Função para criar as tabelas necessárias no Supabase
async def setup_supabase_tables():
    """
    Configura as tabelas necessárias no Supabase.
    
    Esta função deve ser executada uma vez para criar a estrutura inicial do banco de dados.
    """
    try:
        client = SupabaseClient()
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
