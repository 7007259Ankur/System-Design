"""
Builder Design Pattern - Advanced Implementation
Real-world scenario: SQL Query Builder
Build complex SELECT/INSERT/UPDATE/DELETE queries step by step.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------

@dataclass
class Query:
    sql: str = ""
    params: list = field(default_factory=list)
    query_type: str = ""

    def __str__(self) -> str:
        return f"SQL: {self.sql}\nParams: {self.params}"


# ---------------------------------------------------------------------------
# Builder Interface
# ---------------------------------------------------------------------------

class QueryBuilder(ABC):
    @abstractmethod
    def reset(self) -> QueryBuilder: ...
    @abstractmethod
    def build(self) -> Query: ...


# ---------------------------------------------------------------------------
# Concrete Builder — SELECT
# ---------------------------------------------------------------------------

class SelectQueryBuilder(QueryBuilder):
    def __init__(self):
        self.reset()

    def reset(self) -> SelectQueryBuilder:
        self._table = ""
        self._columns: list[str] = ["*"]
        self._joins: list[str] = []
        self._conditions: list[str] = []
        self._params: list = []
        self._group_by: list[str] = []
        self._having: list[str] = []
        self._order_by: list[str] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._distinct = False
        return self

    def from_table(self, table: str) -> SelectQueryBuilder:
        self._table = table
        return self

    def select(self, *columns: str) -> SelectQueryBuilder:
        self._columns = list(columns)
        return self

    def distinct(self) -> SelectQueryBuilder:
        self._distinct = True
        return self

    def join(self, table: str, on: str, join_type: str = "INNER") -> SelectQueryBuilder:
        self._joins.append(f"{join_type} JOIN {table} ON {on}")
        return self

    def where(self, condition: str, *params) -> SelectQueryBuilder:
        self._conditions.append(condition)
        self._params.extend(params)
        return self

    def group_by(self, *columns: str) -> SelectQueryBuilder:
        self._group_by.extend(columns)
        return self

    def having(self, condition: str) -> SelectQueryBuilder:
        self._having.append(condition)
        return self

    def order_by(self, column: str, direction: str = "ASC") -> SelectQueryBuilder:
        self._order_by.append(f"{column} {direction}")
        return self

    def limit(self, n: int) -> SelectQueryBuilder:
        self._limit = n
        return self

    def offset(self, n: int) -> SelectQueryBuilder:
        self._offset = n
        return self

    def build(self) -> Query:
        distinct = "DISTINCT " if self._distinct else ""
        sql = f"SELECT {distinct}{', '.join(self._columns)} FROM {self._table}"
        if self._joins:
            sql += " " + " ".join(self._joins)
        if self._conditions:
            sql += " WHERE " + " AND ".join(self._conditions)
        if self._group_by:
            sql += " GROUP BY " + ", ".join(self._group_by)
        if self._having:
            sql += " HAVING " + " AND ".join(self._having)
        if self._order_by:
            sql += " ORDER BY " + ", ".join(self._order_by)
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
        if self._offset is not None:
            sql += f" OFFSET {self._offset}"
        return Query(sql=sql, params=self._params, query_type="SELECT")


# ---------------------------------------------------------------------------
# Concrete Builder — INSERT
# ---------------------------------------------------------------------------

class InsertQueryBuilder(QueryBuilder):
    def __init__(self):
        self.reset()

    def reset(self) -> InsertQueryBuilder:
        self._table = ""
        self._data: dict = {}
        self._on_conflict: str = ""
        return self

    def into(self, table: str) -> InsertQueryBuilder:
        self._table = table
        return self

    def values(self, **kwargs) -> InsertQueryBuilder:
        self._data.update(kwargs)
        return self

    def on_conflict(self, action: str) -> InsertQueryBuilder:
        self._on_conflict = action
        return self

    def build(self) -> Query:
        cols = ", ".join(self._data.keys())
        placeholders = ", ".join(["%s"] * len(self._data))
        sql = f"INSERT INTO {self._table} ({cols}) VALUES ({placeholders})"
        if self._on_conflict:
            sql += f" ON CONFLICT {self._on_conflict}"
        return Query(sql=sql, params=list(self._data.values()), query_type="INSERT")


# ---------------------------------------------------------------------------
# Concrete Builder — UPDATE
# ---------------------------------------------------------------------------

class UpdateQueryBuilder(QueryBuilder):
    def __init__(self):
        self.reset()

    def reset(self) -> UpdateQueryBuilder:
        self._table = ""
        self._set: dict = {}
        self._conditions: list[str] = []
        self._params: list = []
        return self

    def table(self, table: str) -> UpdateQueryBuilder:
        self._table = table
        return self

    def set(self, **kwargs) -> UpdateQueryBuilder:
        self._set.update(kwargs)
        return self

    def where(self, condition: str, *params) -> UpdateQueryBuilder:
        self._conditions.append(condition)
        self._params.extend(params)
        return self

    def build(self) -> Query:
        set_clause = ", ".join(f"{k} = %s" for k in self._set)
        params = list(self._set.values()) + self._params
        sql = f"UPDATE {self._table} SET {set_clause}"
        if self._conditions:
            sql += " WHERE " + " AND ".join(self._conditions)
        return Query(sql=sql, params=params, query_type="UPDATE")


# ---------------------------------------------------------------------------
# Director — provides preset query templates
# ---------------------------------------------------------------------------

class QueryDirector:
    """Builds common query patterns using builders."""

    @staticmethod
    def paginated_list(builder: SelectQueryBuilder, table: str,
                       page: int, page_size: int) -> Query:
        return (builder.reset()
                .from_table(table)
                .order_by("created_at", "DESC")
                .limit(page_size)
                .offset((page - 1) * page_size)
                .build())

    @staticmethod
    def search_users(builder: SelectQueryBuilder, search_term: str) -> Query:
        return (builder.reset()
                .from_table("users")
                .select("id", "name", "email", "created_at")
                .join("user_profiles", "users.id = user_profiles.user_id", "LEFT")
                .where("users.name ILIKE %s OR users.email ILIKE %s",
                       f"%{search_term}%", f"%{search_term}%")
                .where("users.is_active = %s", True)
                .order_by("users.name")
                .limit(50)
                .build())

    @staticmethod
    def sales_report(builder: SelectQueryBuilder, year: int) -> Query:
        return (builder.reset()
                .from_table("orders")
                .select("DATE_TRUNC('month', created_at) AS month",
                        "COUNT(*) AS order_count",
                        "SUM(total) AS revenue")
                .join("order_items", "orders.id = order_items.order_id")
                .where("EXTRACT(YEAR FROM orders.created_at) = %s", year)
                .where("orders.status = %s", "completed")
                .group_by("DATE_TRUNC('month', created_at)")
                .having("SUM(total) > 1000")
                .order_by("month")
                .build())


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def main():
    print("=" * 55)
    print("  Builder Pattern — SQL Query Builder Demo")
    print("=" * 55)

    select_builder = SelectQueryBuilder()
    insert_builder = InsertQueryBuilder()
    update_builder = UpdateQueryBuilder()
    director = QueryDirector()

    print("\n>>> Paginated list")
    q = director.paginated_list(select_builder, "products", page=3, page_size=20)
    print(q)

    print("\n>>> User search")
    q = director.search_users(select_builder, "john")
    print(q)

    print("\n>>> Sales report")
    q = director.sales_report(select_builder, 2025)
    print(q)

    print("\n>>> Custom SELECT with joins")
    q = (select_builder.reset()
         .from_table("orders o")
         .select("o.id", "u.name", "o.total", "o.status")
         .distinct()
         .join("users u", "o.user_id = u.id")
         .join("payments p", "o.id = p.order_id", "LEFT")
         .where("o.status IN (%s, %s)", "pending", "processing")
         .where("o.total > %s", 100)
         .order_by("o.created_at", "DESC")
         .limit(10)
         .build())
    print(q)

    print("\n>>> INSERT with conflict handling")
    q = (insert_builder.reset()
         .into("users")
         .values(name="Alice", email="alice@example.com", role="admin")
         .on_conflict("(email) DO UPDATE SET name = EXCLUDED.name")
         .build())
    print(q)

    print("\n>>> UPDATE")
    q = (update_builder.reset()
         .table("users")
         .set(is_active=False, updated_at="NOW()")
         .where("last_login < %s", "2024-01-01")
         .where("role != %s", "admin")
         .build())
    print(q)


if __name__ == "__main__":
    main()
