import unittest
import os
import json
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List

from advanced_features.logging.architecture.interfaces import (
    LogEntry, ILogProducer, ILogProcessor, ILogConsumer
)
from advanced_features.logging.architecture.simple_implementation import (
    SimpleLogProcessor, FileLogConsumer, TimestampEnricher,
    SimpleLogRouter, BankingSystemLogProducer
)
from advanced_features.logging.architecture.facade import LoggingFacade


class MockLogConsumer(ILogConsumer):

    def __init__(self):
        self.logs = []
    
    def consume(self, log_entry: LogEntry) -> bool:
        self.logs.append(log_entry)
        return True
    
    def query(self, filter_criteria: Dict[str, Any]) -> List[LogEntry]:
        return [
            log for log in self.logs
            if all(log.get_value(key) == value for key, value in filter_criteria.items())
        ]


class MockLogProcessor(ILogProcessor):

    def __init__(self):
        self.consumers = []
        self.processed_entries = []
    
    def process(self, log_entry: LogEntry) -> LogEntry:
        log_entry.set_value('processed_by', 'MockLogProcessor')
        self.processed_entries.append(log_entry)
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


class TestLoggingArchitecture(unittest.TestCase):

    def setUp(self):
        self.log_file = "test_architecture.log"
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    
    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    
    def test_log_entry(self):
        data = {
            "action": "test",
            "account_id": "ACC0001",
            "amount": Decimal("100.00")
        }
        entry = LogEntry(data)
        
        self.assertEqual(entry.get_value("action"), "test")
        self.assertEqual(entry.get_value("account_id"), "ACC0001")
        self.assertEqual(entry.get_value("amount"), Decimal("100.00"))
        self.assertIsNone(entry.get_value("non_existent"))
        self.assertEqual(entry.get_value("non_existent", "default"), "default")
        
        entry.set_value("status", "success")
        self.assertEqual(entry.get_value("status"), "success")
        
        self.assertEqual(entry.to_dict(), {
            "action": "test",
            "account_id": "ACC0001",
            "amount": Decimal("100.00"),
            "status": "success"
        })
    
    def test_file_log_consumer(self):
        consumer = FileLogConsumer(self.log_file)
        
        entry = LogEntry({
            "action": "test",
            "account_id": "ACC0001",
            "amount": "100.00",
            "timestamp": datetime.now().isoformat()
        })
        
        self.assertTrue(consumer.consume(entry))
        
        self.assertTrue(os.path.exists(self.log_file))
        
        with open(self.log_file, 'r') as f:
            content = f.read().strip()
            data = json.loads(content)
            self.assertEqual(data["action"], "test")
            self.assertEqual(data["account_id"], "ACC0001")
            self.assertEqual(data["amount"], "100.00")
    
    def test_simple_log_processor(self):
        processor = SimpleLogProcessor()
        consumer = MockLogConsumer()
        processor.attach_consumer(consumer)
        
        entry = LogEntry({
            "action": "test",
            "account_id": "ACC0001"
        })
        
        processed_entry = processor.process(entry)
        self.assertTrue("processing_timestamp" in processed_entry.data)
        self.assertTrue("log_level" in processed_entry.data)
        
        processor.forward_to_consumers(processed_entry)
        
        self.assertEqual(len(consumer.logs), 1)
        self.assertEqual(consumer.logs[0].get_value("action"), "test")
        
        processor.detach_consumer(consumer)
        self.assertEqual(len(processor.consumers), 0)
    
    def test_timestamp_enricher(self):
        enricher = TimestampEnricher()
        entry = LogEntry({
            "action": "test",
            "account_id": "ACC0001"
        })
        
        enriched_entry = enricher.enrich(entry)
        
        self.assertTrue("timestamp" in enriched_entry.data)
        
        timestamp = "2023-01-01T12:00:00"
        entry_with_timestamp = LogEntry({
            "action": "test",
            "account_id": "ACC0001",
            "timestamp": timestamp
        })
        
        enriched_entry = enricher.enrich(entry_with_timestamp)
        
        self.assertEqual(enriched_entry.get_value("timestamp"), timestamp)
    
    def test_simple_log_router(self):
        router = SimpleLogRouter()
        
        deposit_processor = MockLogProcessor()
        withdraw_processor = MockLogProcessor()
        default_processor = MockLogProcessor()
        
        router.register_processor("deposit", deposit_processor)
        router.register_processor("withdraw", withdraw_processor)
        router.set_default_processor(default_processor)
        
        deposit_entry = LogEntry({"action": "deposit", "account_id": "ACC0001"})
        withdraw_entry = LogEntry({"action": "withdraw", "account_id": "ACC0001"})
        transfer_entry = LogEntry({"action": "transfer", "account_id": "ACC0001"})
        
        self.assertEqual(router.route(deposit_entry), deposit_processor)
        self.assertEqual(router.route(withdraw_entry), withdraw_processor)
        self.assertEqual(router.route(transfer_entry), default_processor)
    
    def test_banking_system_log_producer(self):
        producer = BankingSystemLogProducer()
        processor = MockLogProcessor()
        
        producer.attach_processor(processor)
        
        data = {
            "action": "test",
            "account_id": "ACC0001"
        }
        producer.create_log_entry(data)
        
        self.assertEqual(len(processor.processed_entries), 1)
        self.assertEqual(processor.processed_entries[0].get_value("action"), "test")
        
        producer.detach_processor(processor)
        self.assertEqual(len(producer.processors), 0)
    
    def test_logging_facade(self):
        facade = LoggingFacade(self.log_file)
        
        facade.log_transaction({
            "action": "deposit",
            "account_id": "ACC0001",
            "amount": "100.00"
        })
        
        self.assertTrue(os.path.exists(self.log_file))
        
        facade.log_transaction({
            "action": "withdraw",
            "account_id": "ACC0001",
            "amount": "50.00"
        })
        
        facade.log_transaction({
            "action": "transfer",
            "from_account_id": "ACC0001",
            "to_account_id": "ACC0002",
            "amount": "25.00"
        })
        
        all_logs = facade.get_all_logs()
        self.assertEqual(len(all_logs), 3)
        
        account_logs = facade.get_logs_by_account("ACC0001")
        self.assertEqual(len(account_logs), 3)
        
        deposit_logs = facade.get_logs_by_action("deposit")
        self.assertEqual(len(deposit_logs), 1)
        self.assertEqual(deposit_logs[0]["action"], "deposit")
        
        withdraw_logs = facade.get_logs_by_action("withdraw")
        self.assertEqual(len(withdraw_logs), 1)
        self.assertEqual(withdraw_logs[0]["action"], "withdraw")
    
    def test_end_to_end_flow(self):
        producer = BankingSystemLogProducer()
        processor = SimpleLogProcessor()
        consumer = FileLogConsumer(self.log_file)
        
        producer.attach_processor(processor)
        processor.attach_consumer(consumer)
        
        producer.create_log_entry({
            "action": "deposit",
            "account_id": "ACC0001",
            "amount": "100.00",
            "status": "success"
        })
        
        producer.create_log_entry({
            "action": "withdraw",
            "account_id": "ACC0001",
            "amount": "50.00",
            "status": "success"
        })
        
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            
            deposit_log = json.loads(lines[0])
            self.assertEqual(deposit_log["action"], "deposit")
            self.assertEqual(deposit_log["account_id"], "ACC0001")
            
            withdraw_log = json.loads(lines[1])
            self.assertEqual(withdraw_log["action"], "withdraw")
            self.assertEqual(withdraw_log["account_id"], "ACC0001")


if __name__ == "__main__":
    unittest.main()
