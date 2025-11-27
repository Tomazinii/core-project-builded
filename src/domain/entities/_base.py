from abc import ABC, abstractmethod
from src.shared.notification import Notification

from typing import Optional
import uuid
from datetime import datetime, timedelta

class Entity(ABC):
    """
    Classe base para todas as entidades do domínio.
    Implementa o padrão de notificação e garante que todas as entidades
    tenham um identificador único e capacidade de validação.
    """
    
    def __init__(self):
        self._notification = Notification()
    
    @property
    def notification(self) -> Notification:
        """Retorna a instância de notificação da entidade"""
        return self._notification
    
    def is_valid(self) -> bool:
        """Verifica se a entidade está em estado válido"""
        return not self._notification.has_errors()
    
    def get_validation_errors(self) -> list[str]:
        """Retorna a lista de erros de validação"""
        return self._notification.get_errors()
    
    def clear_notifications(self) -> None:
        """Limpa todas as notificações da entidade"""
        self._notification.clear()
    
    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and getattr(self, "id", None) == getattr(other, "id", None)

    def __hash__(self) -> int:
        return hash(getattr(self, "id", None))

class ValueObject(ABC):
    """
    Classe base para Value Objects.
    Value Objects são imutáveis e sua igualdade é baseada no valor, não na identidade.
    """
    
    def __init__(self, value):
        self._value = value
        self._validate()
    
    @abstractmethod
    def _validate(self) -> None:
        """Método abstrato para validação do valor"""
        pass
    
    @property
    def value(self):
        """Retorna o valor encapsulado"""
        return self._value
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        """Implementação obrigatória de igualdade baseada no valor"""
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        """Implementação obrigatória de hash baseada no valor"""
        pass
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self._value}')"


class AggregateRoot(Entity):
    """
    Classe base para Aggregate Roots.
    Aggregate Roots são entidades que servem como ponto de entrada
    para um conjunto de entidades relacionadas (agregado).
    """
    
    def __init__(self):
        super().__init__()
        self._domain_events = []
    
    def add_domain_event(self, event) -> None:
        """Adiciona um evento de domínio ao agregado"""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> list:
        """Retorna a lista de eventos de domínio"""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Limpa todos os eventos de domínio"""
        self._domain_events.clear()
    
    def has_domain_events(self) -> bool:
        """Verifica se existem eventos de domínio pendentes"""
        return len(self._domain_events) > 0
    
    
    
    
class BaseId:
    """
    Classe base para identificadores únicos usando UUID v4.
    Garante imutabilidade e encapsulamento do identificador.
    """
    
    def __init__(self, value: Optional[str] = None):
        self._value = str(value) if value else str(uuid.uuid4())
        self._validate()
    
    def _validate(self) -> None:
        """Valida se o valor é um UUID válido"""
        try:
            uuid.UUID(str(self._value))
        except ValueError:
            raise ValueError("Invalid UUID format")
    
    @property
    def value(self) -> str:
        """Retorna o valor do ID"""
        return self._value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BaseId):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self._value}')"


class Query(ValueObject):
    """
    Classe base para consultas.
    Encapsula o valor da consulta e garante que seja um string válido.
    """

    def __init__(self, value: str):
        super().__init__(value)

    def _validate(self) -> None:
        if not isinstance(self._value, str) or not self._value.strip():
            raise ValueError("Query deve ser uma string não vazia")
        if len(self._value) > 10_000:
            raise ValueError("Query deve ter no máximo 10_000 caracteres")

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self._value == other.value

    def __hash__(self) -> int:
        return hash(self._value)
    
    
    
    
class BaseTimestamp(ValueObject):
    """
    Value Object base para manipulação de timestamps.
    Fornece comportamento reutilizável para objetos que encapsulam datetime.
    """

    def __init__(self, value: datetime):
        super().__init__(value)

    def _validate(self) -> None:
        if not isinstance(self._value, datetime):
            raise ValueError("Timestamp deve ser um datetime válido")

    def is_after(self, other: 'BaseTimestamp') -> bool:
        return self._value > other._value

    def is_before(self, other: 'BaseTimestamp') -> bool:
        return self._value < other._value

    def add_time(self, **kwargs) -> 'BaseTimestamp':
        return self.__class__(self._value + timedelta(**kwargs))

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self._value == other.value

    def __hash__(self) -> int:
        return hash(self._value)