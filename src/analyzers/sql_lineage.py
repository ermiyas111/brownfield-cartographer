import logging
from typing import List, Tuple
import sqlglot
from sqlglot import exp

def extract_sql_lineage(sql_text: str, dialect: str = "postgres") -> List[Tuple[str, str]]:
    """
    Extract table-level lineage from SQL: (source, sink) edges.
    Sources: FROM/JOIN tables. Sinks: INSERT INTO/CREATE TABLE.
    Ignores CTEs. Normalizes as schema.table (default if missing).
    """
    try:
        tree = sqlglot.parse_one(sql_text, read=dialect)
    except Exception as e:
        logging.warning(f"[sql_lineage] Could not parse SQL: {e}")
        return []

    sources, sinks, ctes = set(), set(), set()
    default_schema = "public"

    # Find CTEs to ignore as sources
    for node in tree.find_all(exp.CTE):
        if node.alias:
            ctes.add(str(node.alias))

    # Find sinks (INSERT INTO, CREATE TABLE)
    for node in tree.walk():
        if isinstance(node, (exp.Insert, exp.Create)):  # exp.Insert, exp.Create
            table = node.this
            if table:
                sinks.add(_normalize_table(table, default_schema))

    # Find sources (FROM, JOIN)
    for node in tree.walk():
        if isinstance(node, (exp.From, exp.Join)):
            for table in node.find_all(exp.Table):
                tname = _normalize_table(table, default_schema)
                if tname not in ctes:
                    sources.add(tname)

    return [(src, sink) for src in sources for sink in sinks]

def _normalize_table(table_exp: exp.Table, default_schema: str) -> str:
    parts = table_exp.name.split('.')
    if len(parts) == 2:
        return f"{parts[0].lower()}.{parts[1].lower()}"
    elif len(parts) == 1:
        return f"{default_schema.lower()}.{parts[0].lower()}"
    return table_exp.name.lower()
