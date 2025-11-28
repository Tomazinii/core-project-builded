from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar, List, Any
from uuid import UUID

from src.shared.notification import Notification

TRepository = TypeVar("TRepository")
TInputDTO = TypeVar("TInputDTO")
TOutputDTO = TypeVar("TOutputDTO")


class UseCase(ABC, Generic[TRepository, TInputDTO, TOutputDTO]):
    """
    Classe base genérica para UseCases.
    Pode ser reutilizada por qualquer entidade/repositório.
    """

    def __init__(self, repository: TRepository):
        self._repository = repository

   
    @abstractmethod
    async def execute(self, input_dto: TInputDTO) -> TOutputDTO:
        """
        Método abstrato a ser implementado.
        """
        pass
