"""
Módulo para definição de esquemas de dados para o banco de dados.

Este módulo contém classes e funções para definir a estrutura dos dados
que serão armazenados no Supabase.
"""
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime
import json


@dataclass
class Bet:
    """Esquema para armazenamento de apostas."""
    race: str
    horse_name: str
    odds: float
    stake: Optional[float] = None
    bet_type: str = "win"
    raw_message: str = ""
    status: str = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o objeto para um dicionário compatível com o Supabase.
        
        Returns:
            dict: Dicionário com os dados da aposta.
        """
        data = asdict(self)
        
        # Converte datetime para string ISO
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        
        if self.updated_at:
            data["updated_at"] = self.updated_at.isoformat()
        
        # Converte result para JSON string se não for None
        if self.result:
            data["result"] = json.dumps(self.result)
        
        # Remove id se for None
        if self.id is None:
            del data["id"]
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bet':
        """
        Cria um objeto Bet a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados da aposta.
            
        Returns:
            Bet: Objeto Bet criado a partir do dicionário.
        """
        # Cria uma cópia para não modificar o original
        bet_data = data.copy()
        
        # Converte strings ISO para datetime
        if "created_at" in bet_data and bet_data["created_at"]:
            if isinstance(bet_data["created_at"], str):
                bet_data["created_at"] = datetime.fromisoformat(bet_data["created_at"].replace("Z", "+00:00"))
        
        if "updated_at" in bet_data and bet_data["updated_at"]:
            if isinstance(bet_data["updated_at"], str):
                bet_data["updated_at"] = datetime.fromisoformat(bet_data["updated_at"].replace("Z", "+00:00"))
        
        # Converte result de JSON string para dicionário
        if "result" in bet_data and bet_data["result"]:
            if isinstance(bet_data["result"], str):
                bet_data["result"] = json.loads(bet_data["result"])
        
        return cls(**bet_data)


@dataclass
class LogEntry:
    """Esquema para armazenamento de logs."""
    action_type: str
    description: str
    created_at: Optional[datetime] = None
    bet_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte o objeto para um dicionário compatível com o Supabase.
        
        Returns:
            dict: Dicionário com os dados do log.
        """
        data = asdict(self)
        
        # Converte datetime para string ISO
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        
        # Converte details para JSON string se não for None
        if self.details:
            data["details"] = json.dumps(self.details)
        
        # Remove id se for None
        if self.id is None:
            del data["id"]
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """
        Cria um objeto LogEntry a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados do log.
            
        Returns:
            LogEntry: Objeto LogEntry criado a partir do dicionário.
        """
        # Cria uma cópia para não modificar o original
        log_data = data.copy()
        
        # Converte string ISO para datetime
        if "created_at" in log_data and log_data["created_at"]:
            if isinstance(log_data["created_at"], str):
                log_data["created_at"] = datetime.fromisoformat(log_data["created_at"].replace("Z", "+00:00"))
        
        # Converte details de JSON string para dicionário
        if "details" in log_data and log_data["details"]:
            if isinstance(log_data["details"], str):
                log_data["details"] = json.loads(log_data["details"])
        
        return cls(**log_data)


# Definição da estrutura das tabelas no Supabase
SUPABASE_SCHEMA = {
    "bets": {
        "id": "uuid primary key default uuid_generate_v4()",
        "race": "text not null",
        "horse_name": "text not null",
        "odds": "numeric not null",
        "stake": "numeric",
        "bet_type": "text not null default 'win'",
        "raw_message": "text",
        "status": "text not null default 'pending'",
        "result": "jsonb",
        "created_at": "timestamptz default now()",
        "updated_at": "timestamptz"
    },
    "logs": {
        "id": "uuid primary key default uuid_generate_v4()",
        "action_type": "text not null",
        "description": "text not null",
        "bet_id": "uuid references bets(id)",
        "details": "jsonb",
        "created_at": "timestamptz default now()"
    }
}


# SQL para criar as tabelas no Supabase
def get_create_tables_sql() -> str:
    """
    Retorna o SQL para criar as tabelas no Supabase.
    
    Returns:
        str: SQL para criar as tabelas.
    """
    sql = """
    -- Habilita a extensão uuid-ossp para gerar UUIDs
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Tabela de apostas
    CREATE TABLE IF NOT EXISTS bets (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        race TEXT NOT NULL,
        horse_name TEXT NOT NULL,
        odds NUMERIC NOT NULL,
        stake NUMERIC,
        bet_type TEXT NOT NULL DEFAULT 'win',
        raw_message TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        result JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ
    );
    
    -- Tabela de logs
    CREATE TABLE IF NOT EXISTS logs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        action_type TEXT NOT NULL,
        description TEXT NOT NULL,
        bet_id UUID REFERENCES bets(id),
        details JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    -- Índices para melhorar a performance
    CREATE INDEX IF NOT EXISTS idx_bets_status ON bets(status);
    CREATE INDEX IF NOT EXISTS idx_bets_created_at ON bets(created_at);
    CREATE INDEX IF NOT EXISTS idx_logs_action_type ON logs(action_type);
    CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at);
    CREATE INDEX IF NOT EXISTS idx_logs_bet_id ON logs(bet_id);
    """
    
    return sql
