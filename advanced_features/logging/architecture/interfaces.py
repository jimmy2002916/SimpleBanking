"""
Logging Architecture Interfaces

This module defines the core interfaces for a scalable, enterprise-ready
logging architecture. It follows a modular design that can scale from
a simple file-based implementation to a distributed system using
technologies like Filebeat, Logstash, and Kafka.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class LogEntry:
    """Represents a standardized log entry across the system."""
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize a log entry with data.
        
        Args:
            data: Dictionary containing log data
        """
        self.data = data
        
    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a value from the log entry."""
        return self.data.get(key, default)
        
    def set_value(self, key: str, value: Any) -> None:
        """Set a value in the log entry."""
        self.data[key] = value
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary."""
        return self.data


class ILogProducer(ABC):
    """
    Interface for components that generate logs.
    
    In an enterprise setting, this would be implemented by various
    banking systems, ATMs, trading platforms, etc.
    """
    
    @abstractmethod
    def attach_processor(self, processor: 'ILogProcessor') -> None:
        """
        Attach a log processor to this producer.
        
        Args:
            processor: The log processor to attach
        """
        pass
    
    @abstractmethod
    def detach_processor(self, processor: 'ILogProcessor') -> None:
        """
        Detach a log processor from this producer.
        
        Args:
            processor: The log processor to detach
        """
        pass
    
    @abstractmethod
    def notify_processors(self, log_entry: LogEntry) -> None:
        """
        Notify all attached processors about a new log entry.
        
        Args:
            log_entry: The log entry to process
        """
        pass


class ILogProcessor(ABC):
    """
    Interface for components that process logs.
    
    In an enterprise setting, this would be implemented by components
    like Logstash, custom enrichment services, or Kafka Streams.
    """
    
    @abstractmethod
    def process(self, log_entry: LogEntry) -> LogEntry:
        """
        Process a log entry.
        
        Args:
            log_entry: The log entry to process
            
        Returns:
            The processed log entry
        """
        pass
    
    @abstractmethod
    def attach_consumer(self, consumer: 'ILogConsumer') -> None:
        """
        Attach a log consumer to this processor.
        
        Args:
            consumer: The log consumer to attach
        """
        pass
    
    @abstractmethod
    def detach_consumer(self, consumer: 'ILogConsumer') -> None:
        """
        Detach a log consumer from this processor.
        
        Args:
            consumer: The log consumer to detach
        """
        pass
    
    @abstractmethod
    def forward_to_consumers(self, log_entry: LogEntry) -> None:
        """
        Forward a processed log entry to all attached consumers.
        
        Args:
            log_entry: The processed log entry to forward
        """
        pass


class ILogConsumer(ABC):
    """
    Interface for components that consume logs.
    
    In an enterprise setting, this would be implemented by components
    like Elasticsearch, Kafka topics, WORM storage, or analytics systems.
    """
    
    @abstractmethod
    def consume(self, log_entry: LogEntry) -> bool:
        """
        Consume a log entry.
        
        Args:
            log_entry: The log entry to consume
            
        Returns:
            True if consumption was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def query(self, filter_criteria: Dict[str, Any]) -> List[LogEntry]:
        """
        Query log entries based on filter criteria.
        
        Args:
            filter_criteria: Criteria to filter log entries
            
        Returns:
            List of matching log entries
        """
        pass


class ILogRouter(ABC):
    """
    Interface for components that route logs to different processors or consumers.
    
    In an enterprise setting, this would be implemented by components
    like Kafka topics, routing rules in Logstash, or custom routing services.
    """
    
    @abstractmethod
    def route(self, log_entry: LogEntry) -> Optional[ILogProcessor]:
        """
        Route a log entry to the appropriate processor.
        
        Args:
            log_entry: The log entry to route
            
        Returns:
            The processor to handle the log entry, or None if no processor is found
        """
        pass


class ILogEnricher(ABC):
    """
    Interface for components that enrich logs with additional information.
    
    In an enterprise setting, this would be implemented by components
    like Logstash filters, custom enrichment services, or Kafka Streams.
    """
    
    @abstractmethod
    def enrich(self, log_entry: LogEntry) -> LogEntry:
        """
        Enrich a log entry with additional information.
        
        Args:
            log_entry: The log entry to enrich
            
        Returns:
            The enriched log entry
        """
        pass


class LoggingConfig:
    """Configuration for the logging system."""
    
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
        """Convert configuration to dictionary."""
        return {
            "retention_period_days": self.retention_period_days,
            "max_log_size_mb": self.max_log_size_mb,
            "log_level": self.log_level,
            "enable_encryption": self.enable_encryption,
            "enable_compression": self.enable_compression,
            "batch_size": self.batch_size,
            "flush_interval_seconds": self.flush_interval_seconds
        }
