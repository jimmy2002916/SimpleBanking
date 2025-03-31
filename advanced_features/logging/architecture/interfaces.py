from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class LogEntry:

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        
    def get_value(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
        
    def set_value(self, key: str, value: Any) -> None:
        self.data[key] = value
        
    def to_dict(self) -> Dict[str, Any]:
        return self.data


class ILogProducer(ABC):
    @abstractmethod
    def attach_processor(self, processor: 'ILogProcessor') -> None:
        pass
    
    @abstractmethod
    def detach_processor(self, processor: 'ILogProcessor') -> None:
        pass
    
    @abstractmethod
    def notify_processors(self, log_entry: LogEntry) -> None:
        pass


class ILogProcessor(ABC):
    @abstractmethod
    def process(self, log_entry: LogEntry) -> LogEntry:
        pass
    
    @abstractmethod
    def attach_consumer(self, consumer: 'ILogConsumer') -> None:
        pass
    
    @abstractmethod
    def detach_consumer(self, consumer: 'ILogConsumer') -> None:
        pass
    
    @abstractmethod
    def forward_to_consumers(self, log_entry: LogEntry) -> None:
        pass


class ILogConsumer(ABC):
    
    @abstractmethod
    def consume(self, log_entry: LogEntry) -> bool:
        pass
    
    @abstractmethod
    def query(self, filter_criteria: Dict[str, Any]) -> List[LogEntry]:
        pass


class ILogRouter(ABC):
    
    @abstractmethod
    def route(self, log_entry: LogEntry) -> Optional[ILogProcessor]:
        pass


class ILogEnricher(ABC):
    
    @abstractmethod
    def enrich(self, log_entry: LogEntry) -> LogEntry:
        pass


class LoggingConfig:

    def __init__(self):
        """Initialize logging configuration with default values."""
        self.retention_period_days = 30
        self.max_log_size_mb = 100
        self.log_level = "INFO"
        self.enable_encryption = False
        self.enable_compression = False
        self.batch_size = 100
        self.flush_interval_seconds = 5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "retention_period_days": self.retention_period_days,
            "max_log_size_mb": self.max_log_size_mb,
            "log_level": self.log_level,
            "enable_encryption": self.enable_encryption,
            "enable_compression": self.enable_compression,
            "batch_size": self.batch_size,
            "flush_interval_seconds": self.flush_interval_seconds
        }
