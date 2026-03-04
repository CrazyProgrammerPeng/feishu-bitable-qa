import json
import logging
from typing import Dict, Any
from llm_service import LLMService

logger = logging.getLogger(__name__)


class ResultFormatter:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        
        self.field_icons = {
            "姓名": "👤",
            "名字": "👤",
            "名称": "📝",
            "标题": "📌",
            "部门": "🏢",
            "职位": "💼",
            "年龄": "🎂",
            "性别": "⚧",
            "电话": "📞",
            "手机": "📱",
            "邮箱": "📧",
            "地址": "📍",
            "日期": "📅",
            "时间": "⏰",
            "状态": "📊",
            "类型": "🏷️",
            "备注": "📝",
            "描述": "📄",
            "金额": "💰",
            "数量": "🔢",
            "编号": "🔢",
            "ID": "🆔",
        }
    
    def format_result(self, query_result: Dict, query_params: Dict, user_message: str) -> str:
        if query_result.get("code") != 0:
            error_msg = query_result.get("msg", "未知错误")
            logger.error(f"查询失败: {error_msg}")
            return f"❌ 查询失败：{error_msg}"
        
        response_type = query_params.get("response_type", "list")
        
        if response_type == "list":
            return self._format_list_result(query_result, query_params)
        elif response_type == "count":
            return self._format_count_result(query_result, query_params)
        elif response_type == "detail":
            return self._format_detail_result(query_result, query_params)
        else:
            return self._format_with_llm(query_result, query_params, user_message)
    
    def _format_list_result(self, query_result: Dict, query_params: Dict) -> str:
        data = query_result.get("data", {})
        items = data.get("items", [])
        
        if not items:
            explanation = query_params.get("explanation", "")
            return f"📭 没有找到符合条件的记录\n\n💡 {explanation}"
        
        total = data.get("total", len(items))
        result_text = f"✅ 查询成功，共找到 {total} 条记录\n"
        result_text += "━" * 20 + "\n\n"
        
        for idx, item in enumerate(items[:10], 1):
            fields = item.get("fields", {})
            result_text += f"📋 记录 {idx}\n"
            result_text += "┄" * 16 + "\n"
            
            for field_name, value in fields.items():
                formatted_value = self._format_field_value(value)
                icon = self._get_field_icon(field_name)
                result_text += f"{icon} {field_name}：{formatted_value}\n"
            
            result_text += "\n"
        
        if len(items) > 10:
            result_text += f"📄 还有 {len(items) - 10} 条记录未显示...\n"
        
        return result_text
    
    def _format_count_result(self, query_result: Dict, query_params: Dict) -> str:
        data = query_result.get("data", {})
        total = data.get("total", 0)
        explanation = query_params.get("explanation", "")
        
        result_text = "📊 统计结果\n"
        result_text += "━" * 20 + "\n\n"
        result_text += f"📈 符合条件的记录共有 {total} 条\n\n"
        
        if explanation:
            result_text += f"💡 {explanation}"
        
        return result_text
    
    def _format_detail_result(self, query_result: Dict, query_params: Dict) -> str:
        data = query_result.get("data", {})
        items = data.get("items", [])
        
        if not items:
            explanation = query_params.get("explanation", "")
            return f"📭 没有找到符合条件的记录\n\n💡 {explanation}"
        
        fields = items[0].get("fields", {})
        result_text = "📋 详细信息\n"
        result_text += "━" * 20 + "\n\n"
        
        for field_name, value in fields.items():
            formatted_value = self._format_field_value(value)
            icon = self._get_field_icon(field_name)
            result_text += f"{icon} {field_name}：{formatted_value}\n"
        
        return result_text
    
    def _format_with_llm(self, query_result: Dict, query_params: Dict, user_message: str) -> str:
        try:
            data = query_result.get("data", {})
            items = data.get("items", [])
            
            clean_items = []
            for item in items:
                clean_item = {}
                for field_name, value in item.get("fields", {}).items():
                    clean_item[field_name] = self._format_field_value(value)
                clean_items.append(clean_item)
            
            prompt = f"""用户问题：{user_message}

查询结果：
{json.dumps(clean_items, ensure_ascii=False, indent=2)}

请根据用户的问题，用自然语言总结查询结果，要求：
1. 直接回答用户的问题
2. 语言简洁明了，使用中文
3. 突出重要信息
4. 不要提及技术细节
5. 如果结果为空，说明没有找到相关信息
6. 使用适当的emoji图标美化输出"""
            
            return self.llm.chat([{"role": "user", "content": prompt}], temperature=0.5)
        
        except Exception as e:
            logger.error(f"使用大模型格式化结果失败: {str(e)}")
            return self._format_list_result(query_result, query_params)
    
    def _format_field_value(self, value: Any) -> str:
        if value is None:
            return "无"
        
        if isinstance(value, bool):
            return "✅ 是" if value else "❌ 否"
        
        if isinstance(value, list):
            if len(value) == 0:
                return "无"
            
            if isinstance(value[0], dict) and "text" in value[0]:
                texts = [item.get("text", "") for item in value if isinstance(item, dict)]
                return "".join(texts) if texts else "无"
            
            if all(isinstance(item, (str, int, float)) for item in value):
                return "、".join(str(item) for item in value)
            
            return json.dumps(value, ensure_ascii=False)
        
        if isinstance(value, dict):
            if "text" in value:
                return value.get("text", "无")
            if "link" in value:
                return f"🔗 {value.get('link', '')}"
            return json.dumps(value, ensure_ascii=False)
        
        return str(value)
    
    def _get_field_icon(self, field_name: str) -> str:
        for key, icon in self.field_icons.items():
            if key in field_name:
                return icon
        return "•"
