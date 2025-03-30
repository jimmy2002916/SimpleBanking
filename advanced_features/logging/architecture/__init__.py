"""
Scalable logging architecture for the Simple Banking System.

This package provides a scalable logging architecture that can grow
from a simple file-based implementation to an enterprise-level solution.
"""

# Import main components for easier access
from .interfaces import (
    LogEntry, ILogProducer, ILogProcessor, 
    ILogConsumer, ILogEnricher, ILogRouter
)
from .simple_implementation import (
    SimpleLogProcessor, FileLogConsumer, TimestampEnricher,
    SimpleLogRouter, BankingSystemLogProducer
)
from .facade import LoggingFacade
from .enterprise_placeholders import (
    IKafkaLogConsumer, ILogstashProcessor, IFilebeatCollector,
    IElasticsearchConsumer, IWORMStorageConsumer
)
