import requests
import logging
from typing import Dict
import config
from llm_service import LLMService
from intent_parser import IntentParser
from bitable_executor import BitableExecutor
from result_formatter import ResultFormatter

logger = logging.getLogger(__name__)


class IntelligentQA:
    def __init__(self):
        self.llm = LLMService()
        self.access_token = None
        self.executor = BitableExecutor(
            app_token=config.DEFAULT_APP_TOKEN,
            table_id=config.DEFAULT_TABLE_ID,
            access_token_getter=self._get_feishu_token
        )
        
        self.table_schema = self.executor.get_table_schema()
        
        self.intent_parser = IntentParser(self.llm, self.table_schema)
        self.formatter = ResultFormatter(self.llm)
        
        logger.info("智能问答系统初始化完成")
    
    def process_question(self, user_message: str) -> str:
        try:
            logger.info(f"处理用户问题: {user_message}")
            
            query_params = self.intent_parser.parse_user_query(user_message)
            logger.info(f"解析结果: intent={query_params.get('intent')}, confidence={query_params.get('confidence')}")
            
            confidence = query_params.get("confidence", 0)
            if confidence < 0.5:
                explanation = query_params.get("explanation", "")
                return f"🤔 抱歉，我不太理解您的问题。\n\n{explanation}\n\n请您换一种方式提问，或输入'帮助'查看使用说明。"
            
            query_result = self.executor.execute_query(query_params)
            
            return self.formatter.format_result(query_result, query_params, user_message)
        
        except Exception as e:
            logger.error(f"处理问题异常: {str(e)}", exc_info=True)
            return f"❌ 处理您的问题时出现错误：{str(e)}\n\n请稍后重试或联系管理员。"
    
    def _get_feishu_token(self) -> str:
        if self.access_token:
            return self.access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": config.FEISHU_APP_ID,
            "app_secret": config.FEISHU_APP_SECRET
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("tenant_access_token")
                logger.info("获取飞书访问令牌成功")
                return self.access_token
            else:
                logger.error(f"获取飞书访问令牌失败: {result}")
                raise Exception(f"获取飞书访问令牌失败: {result.get('msg')}")
        
        except Exception as e:
            logger.error(f"获取飞书访问令牌异常: {str(e)}")
            raise
    
    def get_help_message(self) -> str:
        return """🤖 我是智能问答机器人，可以帮您查询和管理多维表格数据。

📝 我可以帮您：
━━━━━━━━━━━━━━━━━━━━
🔍 查询类：
• 查询所有记录
• 查询[字段]为[值]的记录
• 查询包含[关键词]的记录

📊 统计类：
• 统计记录数量
• 统计符合条件的记录数

💡 示例：
• 查询所有员工
• 查询部门为技术部的员工
• 统计技术部的人数
• 查询姓名包含张的员工

❓ 输入'帮助'查看此信息

💡 提示：直接用自然语言描述您的问题即可，我会智能理解并为您查询数据。"""
