"""SQL Validator 单元测试"""
import pytest
from backend.services.sql_validator import validate_and_fix


class TestValidateAndFix:
    """validate_and_fix 函数测试"""

    def test_valid_select(self):
        """正常 SELECT 语句通过验证"""
        result = validate_and_fix("SELECT * FROM users")
        assert result.valid is True
        assert result.sql is not None

    def test_limit_auto_append(self):
        """无 LIMIT 的 SELECT 自动追加 LIMIT 1000"""
        result = validate_and_fix("SELECT * FROM users")
        assert result.valid is True
        assert result.sql.upper().endswith("LIMIT 1000")

    def test_select_with_limit_kept(self):
        """已有 LIMIT 的 SELECT 不追加"""
        result = validate_and_fix("SELECT * FROM users LIMIT 5")
        assert result.valid is True
        assert "LIMIT 1000" not in result.sql.upper()

    def test_select_with_limit_lowercase(self):
        """小写 limit 也能识别"""
        result = validate_and_fix("select * from users limit 5")
        assert result.valid is True

    def test_reject_delete(self):
        """DELETE 语句被拒绝"""
        result = validate_and_fix("DELETE FROM users")
        assert result.valid is False
        assert "仅支持 SELECT" in result.error

    def test_reject_insert(self):
        """INSERT 语句被拒绝"""
        result = validate_and_fix("INSERT INTO users (id) VALUES (1)")
        assert result.valid is False
        assert "仅支持 SELECT" in result.error

    def test_reject_update(self):
        """UPDATE 语句被拒绝"""
        result = validate_and_fix("UPDATE users SET name='test' WHERE id=1")
        assert result.valid is False
        assert "仅支持 SELECT" in result.error

    def test_reject_drop(self):
        """DROP 语句被拒绝"""
        result = validate_and_fix("DROP TABLE users")
        assert result.valid is False
        assert "仅支持 SELECT" in result.error

    def test_reject_create(self):
        """CREATE 语句被拒绝"""
        result = validate_and_fix("CREATE TABLE test (id int)")
        assert result.valid is False
        assert "仅支持 SELECT" in result.error

    def test_reject_alter(self):
        """ALTER 语句被拒绝"""
        result = validate_and_fix("ALTER TABLE users ADD COLUMN age int")
        assert result.valid is False
        assert "仅支持 SELECT" in result.error

    def test_reject_truncate(self):
        """TRUNCATE 语句被拒绝"""
        result = validate_and_fix("TRUNCATE TABLE users")
        assert result.valid is False
        assert "仅支持 SELECT" in result.error

    def test_syntax_error_typo(self):
        """拼写错误返回语法错误提示"""
        result = validate_and_fix("SELECCT * FORM users")
        assert result.valid is False
        assert "语法错误" in result.error

    def test_syntax_error_gibberish(self):
        """乱码返回语法错误提示"""
        result = validate_and_fix("dsfjkldsf jkldsf")
        assert result.valid is False
        assert "语法错误" in result.error

    def test_empty_sql(self):
        """空 SQL 被拒绝"""
        result = validate_and_fix("")
        assert result.valid is False
        assert "不能为空" in result.error

    def test_whitespace_only(self):
        """纯空白被拒绝"""
        result = validate_and_fix("   ")
        assert result.valid is False
        assert "不能为空" in result.error

    def test_complex_select(self):
        """复杂 SELECT（JOIN + GROUP BY + ORDER BY）通过验证"""
        sql = """
            SELECT u.name, COUNT(o.id) as cnt
            FROM users u
            JOIN orders o ON u.id = o.user_id
            WHERE o.status = 'completed'
            GROUP BY u.name
            ORDER BY cnt DESC
        """
        result = validate_and_fix(sql)
        assert result.valid is True

    def test_select_with_semicolon(self):
        """带分号的 SELECT 被正常处理"""
        result = validate_and_fix("SELECT 1;")
        assert result.valid is True

    def test_case_insensitive_keyword(self):
        """关键字大小写不敏感"""
        result = validate_and_fix("select id, name from users")
        assert result.valid is True

    def test_mixed_case_select(self):
        """混合大小写 SELECT 通过"""
        result = validate_and_fix("Select * From users")
        assert result.valid is True

    def test_select_with_cte(self):
        """CTE（WITH）查询通过验证"""
        result = validate_and_fix("""
            WITH active AS (SELECT * FROM users WHERE is_active = true)
            SELECT * FROM active
        """)
        assert result.valid is True

    def test_merge_statement_rejected(self):
        """MERGE 语句被拒绝"""
        result = validate_and_fix("MERGE INTO users USING ...")
        assert result.valid is False

    def test_replace_statement_rejected(self):
        """REPLACE 语句被拒绝"""
        result = validate_and_fix("REPLACE INTO users VALUES (1)")
        assert result.valid is False
