import json
import re
import logging
from typing import Dict, List, Any
from llm_service import LLMService

logger = logging.getLogger(__name__)


class IntentParser:
    def __init__(self, llm_service: LLMService, table_schema: Dict):
        self.llm = llm_service
        self.table_schema = table_schema
    
    def parse_user_query(self, user_message: str) -> Dict[str, Any]:
        try:
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(user_message)
            
            logger.info(f"解析用户问题: {user_message}")
            response = self.llm.chat_with_system(system_prompt, user_prompt, temperature=0.1)
            
            logger.info(f"大模型返回: {response}")
            return self._parse_llm_response(response)
        
        except Exception as e:
            logger.error(f"解析用户问题失败: {str(e)}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "explanation": f"解析失败: {str(e)}"
            }
    
    def _build_system_prompt(self) -> str:
        table_info = self._format_table_schema()
        
        prompt = f"""你是一个智能数据查询助手，负责理解用户的问题并生成相应的查询条件。

当前多维表格的结构如下：
{table_info}

你需要分析用户的问题，并返回以下JSON格式的结果（只返回JSON，不要包含其他文字）：
{{
    "intent": "query|statistics|update|create|delete",
    "confidence": 0.0-1.0,
    "filters": [
        {{
            "field": "字段名",
            "operator": "is|isNot|contains|doesNotContain|isEmpty|isNotEmpty|isGreater|isLess|isGreaterOrEqual|isLessOrEqual",
            "value": "值"
        }}
    ],
    "fields_to_return": ["字段1", "字段2"],
    "sort": {{
        "field": "排序字段",
        "order": "asc|desc"
    }},
    "limit": 数字,
    "response_type": "list|count|detail",
    "explanation": "对用户问题的理解说明"
}}

注意事项：
1. operator说明：
   - is: 等于
   - isNot: 不等于
   - contains: 包含
   - doesNotContain: 不包含
   - isEmpty: 为空
   - isNotEmpty: 不为空
   - isGreater: 大于
   - isLess: 小于
   - isGreaterOrEqual: 大于等于
   - isLessOrEqual: 小于等于

2. 多个筛选条件之间默认使用AND连接

3. 对于统计类问题，设置intent为"statistics"，response_type为"count"

4. 对于查询类问题，设置intent为"query"，response_type为"list"或"detail"

5. 如果用户问题不明确或无法理解，设置intent为"unknown"，confidence为0.0

6. 只返回JSON，不要包含其他说明文字或markdown标记"""
        
        return prompt
    
    def _build_user_prompt(self, user_message: str) -> str:
        return f"用户问题：{user_message}"
    
    def _format_table_schema(self) -> str:
        if not self.table_schema or "fields" not in self.table_schema:
            return "表格结构未知"
        
        schema_info = []
        for field in self.table_schema["fields"]:
            field_name = field.get("field_name", "未知字段")
            field_type = field.get("type", "未知类型")
            field_info = f"- {field_name} ({field_type})"
            
            if field.get("property"):
                if field_type in ["SingleSelect", "MultiSelect"]:
                    options = field["property"].get("options", [])
                    if isinstance(options, list):
                        option_names = [opt.get("name", "") if isinstance(opt, dict) else str(opt) for opt in options]
                        field_info += f" [选项: {', '.join(option_names)}]"
            
            schema_info.append(field_info)
        
        return "\n".join(schema_info)
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                if "intent" not in result:
                    result["intent"] = "unknown"
                if "confidence" not in result:
                    result["confidence"] = 0.5
                if "filters" not in result:
                    result["filters"] = []
                if "fields_to_return" not in result:
                    result["fields_to_return"] = []
                if "response_type" not in result:
                    result["response_type"] = "list"
                if "explanation" not in result:
                    result["explanation"] = ""
                
                return result
            else:
                logger.warning(f"未找到JSON内容: {response}")
                return {
                    "intent": "unknown",
                    "confidence": 0.0,
                    "explanation": "无法解析返回结果"
                }
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}, 原始响应: {response}")
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "explanation": f"JSON解析失败: {str(e)}"
            }
