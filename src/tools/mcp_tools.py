"""
MCP (Model Context Protocol) tool entegrasyonu - BONUS.

MCP standardına uygun basit bir tool server/client yapısı sağlar.
Bu modül, projenin bonus gereksinimlerini karşılamak için
MCP tabanlı tool çağırma mekanizması uygular.

MCP, model-agnostik bir protokoldür ve farklı LLM'lerin
aynı tool setini kullanabilmesini sağlar.
"""

import json
from typing import Any, Callable
from src.monitoring.logger import get_logger

logger = get_logger(__name__)


class MCPToolRegistry:
    """
    MCP uyumlu tool registry.

    Tool'ları merkezi bir kayıt defterinde tutar ve
    MCP protokolüne uygun şekilde çağrılmasını sağlar.

    MCP standardına göre her tool'un şu bilgileri vardır:
    - name: Tool'un benzersiz adı
    - description: Ne yaptığının açıklaması
    - input_schema: Beklenen girdi formatı
    - function: Çalıştırılacak fonksiyon
    """

    def __init__(self):
        """Registry'yi başlatır."""
        self._tools: dict[str, dict[str, Any]] = {}
        logger.info("MCP Tool Registry oluşturuldu")

    def register(
        self,
        name: str,
        description: str,
        input_schema: dict,
        function: Callable,
    ) -> None:
        """
        Yeni bir tool kayıt eder.

        Args:
            name: Tool'un benzersiz adı.
            description: Tool'un açıklaması.
            input_schema: JSON Schema formatında girdi tanımı.
            function: Çağrılacak Python fonksiyonu.
        """
        self._tools[name] = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "function": function,
        }
        logger.info(
            "MCP tool kaydedildi",
            extra={"tool_name": name},
        )

    def list_tools(self) -> list[dict[str, Any]]:
        """
        Kayıtlı tool'ların listesini döndürür (fonksiyon hariç).

        MCP listTools yanıtı formatında döndürür.

        Returns:
            list: Tool tanımlarının listesi.
        """
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["input_schema"],
            }
            for tool in self._tools.values()
        ]

    def call_tool(self, name: str, arguments: dict) -> dict[str, Any]:
        """
        Bir tool'u MCP protokolüne uygun şekilde çağırır.

        Args:
            name: Çağrılacak tool'un adı.
            arguments: Tool'a geçilecek argümanlar.

        Returns:
            dict: MCP yanıt formatında sonuç.
                  {"content": [...], "isError": bool}
        """
        if name not in self._tools:
            logger.error(
                "MCP tool bulunamadı",
                extra={"tool_name": name},
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Hata: '{name}' adlı tool bulunamadı. "
                        f"Mevcut tool'lar: {list(self._tools.keys())}",
                    }
                ],
                "isError": True,
            }

        try:
            logger.info(
                "MCP tool çağrılıyor",
                extra={"tool_name": name, "arguments": arguments},
            )

            tool_func = self._tools[name]["function"]
            result = tool_func(**arguments)

            logger.info(
                "MCP tool başarıyla çalıştı",
                extra={"tool_name": name},
            )

            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result),
                    }
                ],
                "isError": False,
            }

        except Exception as e:
            logger.error(
                "MCP tool çalıştırma hatası",
                extra={"tool_name": name, "error": str(e)},
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Tool çalıştırma hatası: {str(e)}",
                    }
                ],
                "isError": True,
            }


def create_mcp_registry() -> MCPToolRegistry:
    """
    Projedeki tool'ları MCP registry'ye kaydeder.

    Web arama ve kod çalıştırma tool'larını MCP formatında
    kayıt eder ve hazır bir registry döndürür.

    Returns:
        MCPToolRegistry: Tool'ları kayıtlı MCP registry.
    """
    registry = MCPToolRegistry()

    # Web arama tool'unu kaydet
    from src.tools.web_search import web_search_tool

    registry.register(
        name="web_search",
        description="DuckDuckGo üzerinden web araması yapar",
        input_schema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Aranacak sorgu metni",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maksimum sonuç sayısı",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
        function=web_search_tool.invoke,
    )

    # Kod çalıştırma tool'unu kaydet
    from src.tools.code_executor import code_executor_tool

    registry.register(
        name="code_executor",
        description="Python kodunu güvenli ortamda çalıştırır",
        input_schema={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Çalıştırılacak Python kodu",
                },
            },
            "required": ["code"],
        },
        function=code_executor_tool.invoke,
    )

    logger.info(
        "MCP registry hazır",
        extra={"tool_count": len(registry.list_tools())},
    )

    return registry
