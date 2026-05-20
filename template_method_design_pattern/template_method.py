"""
Template Method Design Pattern - Advanced Implementation
Real-world scenario: ETL Data Pipeline
The pipeline skeleton (extract->validate->transform->load->notify)
is fixed in the base class. Each concrete pipeline overrides only
the steps that differ.
"""

from __future__ import annotations
import logging
import time
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class PipelineRecord:
    id: str
    data: dict
    source: str
    valid: bool = True
    errors: list[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    pipeline_name: str
    started_at: datetime
    finished_at: datetime
    records_extracted: int = 0
    records_valid: int = 0
    records_loaded: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        return (self.finished_at - self.started_at).total_seconds() * 1000

    def display(self) -> None:
        status = "SUCCESS" if not self.errors else "PARTIAL"
        print(f"\n  Pipeline:  {self.pipeline_name}")
        print(f"  Status:    {status}")
        print(f"  Duration:  {self.duration_ms:.1f}ms")
        print(f"  Extracted: {self.records_extracted}")
        print(f"  Valid:     {self.records_valid}")
        print(f"  Loaded:    {self.records_loaded}")
        if self.errors:
            print(f"  Errors:    {len(self.errors)}")
            for e in self.errors[:3]:
                print(f"    - {e}")


# ---------------------------------------------------------------------------
# Abstract base — defines the template method
# ---------------------------------------------------------------------------

class DataPipeline(ABC):
    """
    The Abstract Class. `run()` is the template method — it defines
    the fixed algorithm skeleton. Subclasses override individual steps.
    """

    def __init__(self, name: str):
        self.name = name
        self._result: PipelineResult = None

    # ---- TEMPLATE METHOD (do not override) ----
    def run(self) -> PipelineResult:
        logger.info(f"[{self.name}] Pipeline starting...")
        started = datetime.now()
        self._result = PipelineResult(self.name, started, started)

        try:
            # Step 1: Setup (hook — optional)
            self.setup()

            # Step 2: Extract
            logger.info(f"[{self.name}] Extracting data...")
            records = self.extract()
            self._result.records_extracted = len(records)

            # Step 3: Validate
            logger.info(f"[{self.name}] Validating {len(records)} records...")
            valid_records = self.validate(records)
            self._result.records_valid = len(valid_records)

            # Step 4: Transform
            logger.info(f"[{self.name}] Transforming data...")
            transformed = self.transform(valid_records)

            # Step 5: Load
            logger.info(f"[{self.name}] Loading {len(transformed)} records...")
            loaded = self.load(transformed)
            self._result.records_loaded = loaded

            # Step 6: Notify (hook — optional)
            self.on_success(self._result)

        except Exception as e:
            self._result.errors.append(str(e))
            logger.error(f"[{self.name}] Pipeline failed: {e}")
            self.on_failure(e, self._result)

        finally:
            # Step 7: Teardown (hook — optional)
            self.teardown()
            self._result.finished_at = datetime.now()

        return self._result

    # ---- Abstract steps (must override) ----

    @abstractmethod
    def extract(self) -> list[PipelineRecord]: ...

    @abstractmethod
    def transform(self, records: list[PipelineRecord]) -> list[PipelineRecord]: ...

    @abstractmethod
    def load(self, records: list[PipelineRecord]) -> int: ...

    # ---- Concrete step with default (can override) ----

    def validate(self, records: list[PipelineRecord]) -> list[PipelineRecord]:
        """Default: pass all records. Override for custom validation."""
        return [r for r in records if r.valid]

    # ---- Hooks (optional overrides) ----

    def setup(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def on_success(self, result: PipelineResult) -> None:
        logger.info(f"[{self.name}] Completed: {result.records_loaded} records loaded.")

    def on_failure(self, error: Exception, result: PipelineResult) -> None:
        logger.error(f"[{self.name}] Failed after {result.records_extracted} extracted.")


# ---------------------------------------------------------------------------
# Concrete Pipeline 1 — CSV to Database
# ---------------------------------------------------------------------------

class CSVtoDatabasePipeline(DataPipeline):
    def __init__(self, filepath: str, table: str):
        super().__init__("CSV->Database")
        self._filepath = filepath
        self._table = table
        self._connection = None

    def setup(self) -> None:
        logger.info(f"  Opening DB connection for table '{self._table}'")
        self._connection = f"db_conn_{self._table}"

    def extract(self) -> list[PipelineRecord]:
        # Simulate reading CSV rows
        time.sleep(0.01)
        return [
            PipelineRecord(f"row_{i}", {"name": f"User{i}", "age": random.randint(10, 90), "email": f"u{i}@x.com"}, "csv")
            for i in range(1, 21)
        ]

    def validate(self, records: list[PipelineRecord]) -> list[PipelineRecord]:
        valid = []
        for r in records:
            if r.data.get("age", 0) < 18:
                r.valid = False
                r.errors.append("Age below 18")
            else:
                valid.append(r)
        logger.info(f"  Validation: {len(valid)}/{len(records)} passed")
        return valid

    def transform(self, records: list[PipelineRecord]) -> list[PipelineRecord]:
        for r in records:
            r.data["email"] = r.data["email"].lower()
            r.data["name"] = r.data["name"].title()
            r.data["inserted_at"] = datetime.now().isoformat()
        return records

    def load(self, records: list[PipelineRecord]) -> int:
        time.sleep(0.01)
        logger.info(f"  INSERT {len(records)} rows into '{self._table}' via {self._connection}")
        return len(records)

    def teardown(self) -> None:
        logger.info("  DB connection closed")
        self._connection = None


# ---------------------------------------------------------------------------
# Concrete Pipeline 2 — API to Data Warehouse
# ---------------------------------------------------------------------------

class APItoWarehousePipeline(DataPipeline):
    def __init__(self, endpoint: str, warehouse_table: str):
        super().__init__("API->Warehouse")
        self._endpoint = endpoint
        self._warehouse_table = warehouse_table

    def extract(self) -> list[PipelineRecord]:
        logger.info(f"  GET {self._endpoint}")
        time.sleep(0.02)
        return [
            PipelineRecord(f"api_{i}", {"product_id": i, "sales": random.randint(0, 500), "region": random.choice(["US", "EU", "APAC"])}, "api")
            for i in range(1, 16)
        ]

    def transform(self, records: list[PipelineRecord]) -> list[PipelineRecord]:
        for r in records:
            r.data["sales_normalized"] = round(r.data["sales"] / 500, 4)
            r.data["etl_timestamp"] = datetime.now().isoformat()
        return records

    def load(self, records: list[PipelineRecord]) -> int:
        logger.info(f"  COPY {len(records)} rows -> warehouse.{self._warehouse_table}")
        time.sleep(0.01)
        return len(records)

    def on_success(self, result: PipelineResult) -> None:
        super().on_success(result)
        logger.info(f"  Warehouse refresh triggered for {self._warehouse_table}")


# ---------------------------------------------------------------------------
# Concrete Pipeline 3 — JSON to Elasticsearch
# ---------------------------------------------------------------------------

class JSONtoElasticsearchPipeline(DataPipeline):
    def __init__(self, json_source: str, index: str):
        super().__init__("JSON->Elasticsearch")
        self._source = json_source
        self._index = index

    def extract(self) -> list[PipelineRecord]:
        logger.info(f"  Reading JSON from {self._source}")
        time.sleep(0.01)
        return [
            PipelineRecord(f"doc_{i}", {"title": f"Article {i}", "body": f"Content of article {i} " * 5, "tags": ["python", "patterns"]}, "json")
            for i in range(1, 11)
        ]

    def transform(self, records: list[PipelineRecord]) -> list[PipelineRecord]:
        for r in records:
            r.data["word_count"] = len(r.data["body"].split())
            r.data["@timestamp"] = datetime.now().isoformat()
            r.data["_id"] = r.id
        return records

    def load(self, records: list[PipelineRecord]) -> int:
        logger.info(f"  Bulk indexing {len(records)} docs -> ES index '{self._index}'")
        time.sleep(0.01)
        return len(records)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Template Method Pattern -- ETL Pipeline Demo")
    print("=" * 55)

    pipelines: list[DataPipeline] = [
        CSVtoDatabasePipeline("data/users.csv", "users"),
        APItoWarehousePipeline("https://api.example.com/sales", "fact_sales"),
        JSONtoElasticsearchPipeline("data/articles.json", "articles-v1"),
    ]

    results = []
    for pipeline in pipelines:
        print(f"\n>>> Running: {pipeline.name}")
        result = pipeline.run()
        result.display()
        results.append(result)

    print("\n>>> Summary")
    print(f"  {'Pipeline':<30} {'Extracted':>10} {'Loaded':>8} {'Duration':>10}")
    print(f"  {'-'*60}")
    for r in results:
        print(f"  {r.pipeline_name:<30} {r.records_extracted:>10} {r.records_loaded:>8} {r.duration_ms:>9.1f}ms")


if __name__ == "__main__":
    main()
