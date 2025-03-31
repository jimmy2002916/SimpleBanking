import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

from .interfaces import (
    LogEntry, ILogProducer, ILogProcessor, 
    ILogConsumer, ILogEnricher, ILogRouter
)


class JsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class SimpleLogProcessor(ILogProcessor):
    
    def __init__(self):
        self.consumers = []
    
    def process(self, log_entry: LogEntry) -> LogEntry:
        # Add processing timestamp if not present
        if 'processing_timestamp' not in log_entry.data:
            log_entry.set_value('processing_timestamp', datetime.now().isoformat())
        
        # Add log level if not present
        if 'log_level' not in log_entry.data:
            log_entry.set_value('log_level', 'INFO')
        
        return log_entry
    
    def attach_consumer(self, consumer: ILogConsumer) -> None:
        if consumer not in self.consumers:
            self.consumers.append(consumer)
    
    def detach_consumer(self, consumer: ILogConsumer) -> None:
        if consumer in self.consumers:
            self.consumers.remove(consumer)
    
    def forward_to_consumers(self, log_entry: LogEntry) -> None:
        for consumer in self.consumers:
            consumer.consume(log_entry)


class FileLogConsumer(ILogConsumer):
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        
        # Create directory for log file if it doesn't exist
        directory = os.path.dirname(log_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def consume(self, log_entry: LogEntry) -> bool:
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry.data, cls=JsonEncoder) + "\n")
            return True
        except Exception as e:
            print(f"Error writing to log file: {e}")
            return False
    
    def query(self, filter_criteria: Dict[str, Any]) -> List[LogEntry]:
        if not os.path.exists(self.log_file):
            return []
        
        matching_entries = []
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    # Check if entry matches all filter criteria
                    if all(data.get(key) == value for key, value in filter_criteria.items()):
                        matching_entries.append(LogEntry(data))
                except json.JSONDecodeError:
                    continue
        
        return matching_entries


class TimestampEnricher(ILogEnricher):
    
    def enrich(self, log_entry: LogEntry) -> LogEntry:
        if 'timestamp' not in log_entry.data:
            log_entry.set_value('timestamp', datetime.now().isoformat())
        
        return log_entry


class SimpleLogRouter(ILogRouter):
    
    def __init__(self):
        self.processors_by_action = {}
        self.default_processor = None
    
    def register_processor(self, action: str, processor: ILogProcessor) -> None:
        self.processors_by_action[action] = processor
    
    def set_default_processor(self, processor: ILogProcessor) -> None:
        self.default_processor = processor
    
    def route(self, log_entry: LogEntry) -> Optional[ILogProcessor]:
        action = log_entry.get_value('action')
        
        if action in self.processors_by_action:
            return self.processors_by_action[action]
        
        return self.default_processor


class BankingSystemLogProducer(ILogProducer):
    
    def __init__(self):
        self.processors = []
    
    def attach_processor(self, processor: ILogProcessor) -> None:
        if processor not in self.processors:
            self.processors.append(processor)
    
    def detach_processor(self, processor: ILogProcessor) -> None:
        if processor in self.processors:
            self.processors.remove(processor)
    
    def notify_processors(self, log_entry: LogEntry) -> None:
        for processor in self.processors:
            processed_entry = processor.process(log_entry)
            processor.forward_to_consumers(processed_entry)
    
    def create_log_entry(self, data: Dict[str, Any]) -> LogEntry:
        log_entry = LogEntry(data)
        self.notify_processors(log_entry)
        return log_entry
