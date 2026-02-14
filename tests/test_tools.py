"""
Araç (Tool) katmanı birim testleri.

Web arama tool'u, kod çalıştırıcı tool'u ve
MCP registry'yi test eder. Hata senaryolarını da kapsar.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.tools.code_executor import validate_code, code_executor_tool
from src.tools.mcp_tools import MCPToolRegistry


class TestValidateCode:
    """Kod güvenlik doğrulama testleri."""

    def test_safe_code_passes(self):
        """Güvenli kod doğrulamayı geçer."""
        safe_code = "print('Hello')\nx = 5 + 3\nprint(x)"
        is_safe, error = validate_code(safe_code)
        assert is_safe is True
        assert error == ""

    def test_empty_code_rejected(self):
        """Boş kod reddedilir."""
        is_safe, error = validate_code("")
        assert is_safe is False
        assert "Boş kod" in error

    def test_whitespace_only_rejected(self):
        """Sadece boşluk içeren kod reddedilir."""
        is_safe, error = validate_code("   \n\t  ")
        assert is_safe is False
        assert "Boş kod" in error

    def test_os_import_blocked(self):
        """os modülü import'u engellenir."""
        is_safe, error = validate_code("import os\nos.system('rm -rf /')")
        assert is_safe is False
        assert "os" in error

    def test_subprocess_blocked(self):
        """subprocess modülü engellenir."""
        is_safe, error = validate_code("import subprocess")
        assert is_safe is False
        assert "subprocess" in error

    def test_sys_blocked(self):
        """sys modülü engellenir."""
        is_safe, error = validate_code("import sys\nsys.exit()")
        assert is_safe is False

    def test_open_function_blocked(self):
        """open() fonksiyonu engellenir."""
        is_safe, error = validate_code("f = open('secret.txt', 'r')")
        assert is_safe is False

    def test_eval_blocked(self):
        """eval() fonksiyonu engellenir."""
        is_safe, error = validate_code("eval('os.system(\"ls\")')")
        assert is_safe is False

    def test_builtins_access_blocked(self):
        """__builtins__ erişimi engellenir."""
        is_safe, error = validate_code("x = __builtins__")
        assert is_safe is False
        assert "__builtins__" in error

    def test_math_operations_allowed(self):
        """Matematik işlemleri güvenli kabul edilir."""
        code = """
import math
result = math.sqrt(144)
print(f'Sonuç: {result}')"""
        is_safe, error = validate_code(code)
        assert is_safe is True

    def test_list_operations_allowed(self):
        """Liste işlemleri güvenli kabul edilir."""
        code = """
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(total)"""
        is_safe, error = validate_code(code)
        assert is_safe is True


class TestCodeExecutorTool:
    """Kod çalıştırıcı tool testleri."""

    def test_simple_execution(self):
        """Basit kod başarıyla çalışır."""
        result = code_executor_tool.invoke({"code": "print('test')"})
        assert "test" in result

    def test_math_calculation(self):
        """Matematik hesaplaması doğru sonuç verir."""
        result = code_executor_tool.invoke({"code": "print(2 + 3)"})
        assert "5" in result

    def test_unsafe_code_rejected(self):
        """Güvensiz kod reddedilir."""
        result = code_executor_tool.invoke({"code": "import os"})
        assert "Güvenlik" in result

    def test_syntax_error_handled(self):
        """Sözdizimi hatası yakalanır."""
        result = code_executor_tool.invoke({"code": "print('unterminated"})
        assert "Hata" in result or "Error" in result

    def test_empty_code_rejected(self):
        """Boş kod reddedilir."""
        result = code_executor_tool.invoke({"code": ""})
        assert "Güvenlik" in result or "Boş" in result


class TestWebSearchTool:
    """Web arama tool testleri."""

    @patch("src.tools.web_search.DDGS")
    def test_successful_search(self, mock_ddgs_class):
        """Başarılı arama sonuçları döndürür."""
        from src.tools.web_search import web_search_tool

        mock_instance = MagicMock()
        mock_instance.text.return_value = [
            {
                "title": "Test Title",
                "href": "https://test.com",
                "body": "Test body text",
            }
        ]
        mock_ddgs_class.return_value = mock_instance

        result = web_search_tool.invoke(
            {"query": "test search", "max_results": 1}
        )
        assert "Test Title" in result

    @patch("src.tools.web_search.DDGS")
    def test_empty_results(self, mock_ddgs_class):
        """Boş arama sonucu düzgün mesaj verir."""
        from src.tools.web_search import web_search_tool

        mock_instance = MagicMock()
        mock_instance.text.return_value = []
        mock_ddgs_class.return_value = mock_instance

        result = web_search_tool.invoke({"query": "xyznonexistent"})
        assert "bulunamadı" in result


class TestMCPToolRegistry:
    """MCP Tool Registry testleri."""

    def test_register_tool(self):
        """Tool başarıyla kaydedilir."""
        registry = MCPToolRegistry()
        registry.register(
            name="test_tool",
            description="Test tool",
            input_schema={"type": "object"},
            function=lambda: "test",
        )
        tools = registry.list_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"

    def test_list_tools(self):
        """Tool listesi doğru formatla döner."""
        registry = MCPToolRegistry()
        registry.register(
            name="tool1",
            description="First tool",
            input_schema={"type": "object"},
            function=lambda: "1",
        )
        registry.register(
            name="tool2",
            description="Second tool",
            input_schema={"type": "object"},
            function=lambda: "2",
        )
        tools = registry.list_tools()
        assert len(tools) == 2
        # Fonksiyon bilgisi dışarıya verilmemeli
        for tool in tools:
            assert "function" not in tool

    def test_call_existing_tool(self):
        """Kayıtlı tool başarıyla çağrılır."""
        registry = MCPToolRegistry()
        registry.register(
            name="adder",
            description="Adds numbers",
            input_schema={"type": "object"},
            function=lambda a, b: a + b,
        )
        result = registry.call_tool("adder", {"a": 3, "b": 5})
        assert result["isError"] is False
        assert "8" in result["content"][0]["text"]

    def test_call_nonexistent_tool(self):
        """Kayıtsız tool çağrısı hata döner."""
        registry = MCPToolRegistry()
        result = registry.call_tool("ghost_tool", {})
        assert result["isError"] is True
        assert "bulunamadı" in result["content"][0]["text"]

    def test_call_tool_with_error(self):
        """Tool hata fırlatırsa MCP hata yanıtı döner."""
        registry = MCPToolRegistry()
        registry.register(
            name="broken",
            description="Always fails",
            input_schema={"type": "object"},
            function=lambda: 1 / 0,
        )
        result = registry.call_tool("broken", {})
        assert result["isError"] is True
