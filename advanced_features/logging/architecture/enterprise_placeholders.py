

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from .interfaces import LogEntry, ILogProcessor, ILogConsumer, ILogProducer


class IKafkaLogConsumer(ILogConsumer):

    @abstractmethod
    def set_topic(self, topic: str) -> None:
        pass
    
    @abstractmethod
    def set_bootstrap_servers(self, servers: List[str]) -> None:
        pass
    
    @abstractmethod
    def set_producer_config(self, config: Dict[str, Any]) -> None:
        pass


class ILogstashProcessor(ILogProcessor):

    @abstractmethod
    def add_filter(self, filter_name: str, filter_config: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def set_input_config(self, input_config: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def set_output_config(self, output_config: Dict[str, Any]) -> None:
        pass


class IFilebeatCollector(ILogProducer):
    
    @abstractmethod
    def add_input(self, input_type: str, input_config: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def set_output(self, output_type: str, output_config: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def set_registry_file(self, registry_file: str) -> None:
        pass


class IElasticsearchConsumer(ILogConsumer):
    
    @abstractmethod
    def set_index(self, index: str) -> None:
        pass
    
    @abstractmethod
    def set_hosts(self, hosts: List[str]) -> None:
        pass
    
    @abstractmethod
    def set_client_config(self, config: Dict[str, Any]) -> None:
        pass


class IWORMStorageConsumer(ILogConsumer):
    
    @abstractmethod
    def set_retention_period(self, days: int) -> None:
        pass
    
    @abstractmethod
    def set_compliance_mode(self, mode: str) -> None:
        pass
    
    @abstractmethod
    def enable_digital_signatures(self, enable: bool) -> None:
        pass


# Example of how these interfaces would be used in the future:
"""
# Create Kafka consumer
kafka_consumer = KafkaLogConsumer()
kafka_consumer.set_topic("banking.transactions")
kafka_consumer.set_bootstrap_servers(["kafka1:9092", "kafka2:9092"])
"""
