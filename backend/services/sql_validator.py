import sqlglot
import sqlglot.expressions as exp


class SqlValidationResult:
    def __init__(self, valid: bool, sql: str, error: str | None = None):
        self.valid = valid
        self.sql = sql
        self.error = error


def validate_and_fix(sql: str) -> SqlValidationResult:
    """Validate SQL: must be SELECT only, auto-append LIMIT 1000 if missing."""
    if not sql or not sql.strip():
        return SqlValidationResult(False, sql, "SQL 语句不能为空")

    try:
        parsed = sqlglot.parse_one(sql, read="postgres")
    except sqlglot.errors.ParseError as e:
        return SqlValidationResult(False, sql, f"SQL 语法错误: {e}")

    # Check statement type — only SELECT allowed
    if not isinstance(parsed, exp.Select):
        # Check if original SQL contains known DML keywords → genuine non-SELECT
        upper_sql = sql.upper().strip()
        dml_keywords = ("DELETE ", "INSERT ", "UPDATE ", "DROP ", "ALTER ", "CREATE ", "TRUNCATE ", "MERGE ", "REPLACE ")
        if any(upper_sql.startswith(kw) for kw in dml_keywords):
            return SqlValidationResult(False, sql, "仅支持 SELECT 查询")
        # Otherwise it's a syntax error that sqlglot silently parsed as non-Select
        return SqlValidationResult(False, sql, "SQL 语法错误，请检查语句")

    # Check LIMIT — append if missing
    if parsed.find(exp.Limit) is None:
        parsed = parsed.limit(1000, dialect="postgres")
        fixed_sql = parsed.sql(dialect="postgres")
        return SqlValidationResult(True, fixed_sql, None)

    return SqlValidationResult(True, sql, None)
