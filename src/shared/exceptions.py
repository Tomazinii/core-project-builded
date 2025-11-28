"""
Exceções de Domínio
"""
from typing import List, Optional


class DomainException(Exception):
    """
    Exceção lançada quando há violação de regras de domínio.
    Carrega uma lista de erros de validação.
    """
    
    def __init__(self, errors: List[str], message: Optional[str] = None):
        """
        Args:
            errors: Lista de mensagens de erro
            message: Mensagem principal opcional
        """
        self.errors = errors
        self.message = message or "Erro de validação de domínio"
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Retorna representação em string da exceção"""
        if len(self.errors) == 1:
            return f"{self.message}: {self.errors[0]}"
        
        errors_str = "\n  - ".join(self.errors)
        return f"{self.message}:\n  - {errors_str}"
    
    def __repr__(self) -> str:
        """Retorna representação técnica da exceção"""
        return f"DomainException(errors={self.errors}, message='{self.message}')"
    
    def has_errors(self) -> bool:
        """Verifica se há erros"""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[str]:
        """Retorna lista de erros"""
        return self.errors
    
    def get_first_error(self) -> Optional[str]:
        """Retorna o primeiro erro da lista"""
        return self.errors[0] if self.errors else None


class EntityNotFoundException(DomainException):
    """
    Exceção lançada quando uma entidade não é encontrada.
    """
    
    def __init__(self, entity_name: str, entity_id: str):
        """
        Args:
            entity_name: Nome da entidade (ex: "Organização", "Usuário")
            entity_id: ID da entidade não encontrada
        """
        self.entity_name = entity_name
        self.entity_id = entity_id
        message = f"{entity_name} não encontrada"
        errors = [f"{entity_name} com ID '{entity_id}' não foi encontrada"]
        super().__init__(errors=errors, message=message)


class DuplicateEntityException(DomainException):
    """
    Exceção lançada quando há tentativa de criar entidade duplicada.
    """
    
    def __init__(self, entity_name: str, field_name: str, field_value: str):
        """
        Args:
            entity_name: Nome da entidade (ex: "Organização", "Usuário")
            field_name: Nome do campo que está duplicado (ex: "slug", "email")
            field_value: Valor duplicado
        """
        self.entity_name = entity_name
        self.field_name = field_name
        self.field_value = field_value
        message = f"{entity_name} duplicada"
        errors = [f"{entity_name} com {field_name} '{field_value}' já existe"]
        super().__init__(errors=errors, message=message)


class BusinessRuleViolationException(DomainException):
    """
    Exceção lançada quando há violação de regra de negócio.
    """
    
    def __init__(self, rule_description: str):
        """
        Args:
            rule_description: Descrição da regra de negócio violada
        """
        self.rule_description = rule_description
        message = "Violação de regra de negócio"
        errors = [rule_description]
        super().__init__(errors=errors, message=message)


class InvalidOperationException(DomainException):
    """
    Exceção lançada quando uma operação inválida é tentada.
    """
    
    def __init__(self, operation: str, reason: str):
        """
        Args:
            operation: Nome da operação
            reason: Razão pela qual a operação é inválida
        """
        self.operation = operation
        self.reason = reason
        message = f"Operação inválida: {operation}"
        errors = [reason]
        super().__init__(errors=errors, message=message)