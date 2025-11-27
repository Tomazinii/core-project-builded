class Notification:
    """
    Implementação do Notification Pattern para capturar e propagar erros de domínio.
    Evita o uso de exceptions diretas, permitindo que outras camadas avaliem os erros.
    """
    
    def __init__(self):
        self._errors: list[str] = []
    
    def add_error(self, message: str) -> None:
        """Adiciona um erro à lista de notificações"""
        if message and message.strip():
            self._errors.append(message.strip())
    
    def add_errors(self, messages: list[str]) -> None:
        """Adiciona múltiplos erros à lista de notificações"""
        for message in messages:
            self.add_error(message)
    
    def has_errors(self) -> bool:
        """Verifica se existem erros registrados"""
        return len(self._errors) > 0
    
    def get_errors(self) -> list[str]:
        """Retorna uma cópia da lista de erros"""
        return self._errors.copy()
    
    def get_errors_as_string(self, separator: str = "; ") -> str:
        """Retorna os erros como uma string concatenada"""
        return separator.join(self._errors)
    
    def clear(self) -> None:
        """Limpa todas as notificações"""
        self._errors.clear()
    
    def merge(self, other_notification: 'Notification') -> None:
        """Mescla erros de outra notificação"""
        if other_notification and other_notification.has_errors():
            self._errors.extend(other_notification.get_errors())
    
    def __len__(self) -> int:
        """Retorna o número de erros"""
        return len(self._errors)
    
    def __bool__(self) -> bool:
        """Permite uso em contextos booleanos (True se tem erros)"""
        return self.has_errors()
    
    def __str__(self) -> str:
        """Representação string das notificações"""
        return self.get_errors_as_string()
    
    def __repr__(self) -> str:
        """Representação para debug"""
        return f"Notification(errors={len(self._errors)})"