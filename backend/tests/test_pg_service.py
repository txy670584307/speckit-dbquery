"""pg_service JDBC URL 解析单元测试"""
import pytest
from backend.services.pg_service import parse_jdbc_url, JdbcUrl


class TestParseJdbcUrl:
    """JDBC URL 解析测试"""

    def test_standard_url(self):
        """标准 JDBC URL 解析"""
        url = "jdbc:postgresql://localhost:5432/mydb?user=admin&password=secret"
        result = parse_jdbc_url(url)
        assert isinstance(result, JdbcUrl)
        assert result.host == "localhost"
        assert result.port == 5432
        assert result.database == "mydb"
        assert result.user == "admin"
        assert result.password == "secret"

    def test_no_password(self):
        """无密码的 JDBC URL"""
        url = "jdbc:postgresql://host:5432/db?user=guest"
        result = parse_jdbc_url(url)
        assert result.host == "host"
        assert result.user == "guest"
        assert result.password == ""

    def test_ip_address(self):
        """IP 地址作为 host"""
        url = "jdbc:postgresql://192.168.1.100:5432/test?user=u&password=p"
        result = parse_jdbc_url(url)
        assert result.host == "192.168.1.100"
        assert result.database == "test"

    def test_non_standard_port(self):
        """非标准端口"""
        url = "jdbc:postgresql://db.example.com:5433/prod?user=user&password=pass"
        result = parse_jdbc_url(url)
        assert result.port == 5433

    def test_complex_password(self):
        """密码含特殊字符"""
        url = "jdbc:postgresql://localhost:5432/db?user=user&password=p@ss#123"
        result = parse_jdbc_url(url)
        assert result.password == "p@ss#123"

    def test_invalid_url_no_jdbc(self):
        """非 JDBC URL 抛出错误"""
        with pytest.raises(ValueError, match="无效的 JDBC URL"):
            parse_jdbc_url("postgresql://localhost:5432/db?user=u&password=p")

    def test_invalid_url_mysql(self):
        """MySQL URL 抛出错误"""
        with pytest.raises(ValueError, match="无效的 JDBC URL"):
            parse_jdbc_url("jdbc:mysql://localhost:3306/db?user=u&password=p")

    def test_invalid_format(self):
        """格式错误的 URL 抛出错误"""
        with pytest.raises(ValueError):
            parse_jdbc_url("not-a-url")
