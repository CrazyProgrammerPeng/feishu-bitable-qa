import requests
import logging
from typing import Dict, List, Any
import config

logger = logging.getLogger(__name__)


class BitableExecutor:
    def __init__(self, app_token: str, table_id: str, access_token_getter):
        self.app_token = app_token
        self.table_id = table_id
        self.get_access_token = access_token_getter
        self.base_url = "https://open.feishu.cn/open-apis/bitable/v1"
    
    def execute_query(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        intent = query_params.get("intent", "unknown")
        
        if intent == "query":
            return self._execute_list_query(query_params)
        elif intent == "statistics":
            return self._execute_statistics_query(query_params)
        elif intent == "unknown":
            return {
                "code": -1,
                "msg": "无法理解的查询意图"
            }
        else:
            return {
                "code": -1,
                "msg": f"不支持的查询类型: {intent}"
            }
    
    def get_table_schema(self) -> Dict[str, Any]:
        try:
            access_token = self.get_access_token()
            url = f"{self.base_url}/apps/{self.app_token}/tables/{self.table_id}/fields"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            logger.info("获取表格结构")
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                return {"fields": result.get("data", {}).get("items", [])}
            else:
                logger.error(f"获取表格结构失败: {result}")
                return {"fields": []}
        
        except Exception as e:
            logger.error(f"获取表格结构异常: {str(e)}")
            return {"fields": []}
    
    def _execute_list_query(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            access_token = self.get_access_token()
            url = f"{self.base_url}/apps/{self.app_token}/tables/{self.table_id}/records/search"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            request_body = {}
            
            filters = query_params.get("filters", [])
            if filters:
                request_body["filter"] = self._build_filter(filters)
            
            fields_to_return = query_params.get("fields_to_return", [])
            if fields_to_return:
                request_body["field_names"] = fields_to_return
            
            sort = query_params.get("sort")
            if sort:
                request_body["sort"] = self._build_sort(sort)
            
            limit = query_params.get("limit", 20)
            request_body["page_size"] = min(limit, 500)
            
            logger.info(f"执行查询: {request_body}")
            response = requests.post(url, headers=headers, json=request_body, timeout=30)
            result = response.json()
            
            logger.info(f"查询结果: code={result.get('code')}, msg={result.get('msg')}")
            return result
        
        except requests.exceptions.Timeout:
            logger.error("查询超时")
            return {"code": -1, "msg": "查询超时"}
        except Exception as e:
            logger.error(f"查询异常: {str(e)}")
            return {"code": -1, "msg": str(e)}
    
    def _execute_statistics_query(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            list_result = self._execute_list_query(query_params)
            
            if list_result.get("code") != 0:
                return list_result
            
            items = list_result.get("data", {}).get("items", [])
            
            return {
                "code": 0,
                "data": {
                    "total": len(items),
                    "items": items
                },
                "msg": "success"
            }
        
        except Exception as e:
            logger.error(f"统计查询异常: {str(e)}")
            return {"code": -1, "msg": str(e)}
    
    def _build_filter(self, filters: List[Dict]) -> Dict:
        if not filters:
            return {}
        
        conditions = []
        for f in filters:
            field = f.get("field")
            operator = f.get("operator", "is")
            value = f.get("value")
            
            if not field or value is None:
                continue
            
            condition = {
                "field_name": field,
                "operator": operator,
                "value": [value] if not isinstance(value, list) else value
            }
            conditions.append(condition)
        
        if not conditions:
            return {}
        
        return {
            "conjunction": "and",
            "conditions": conditions
        }
    
    def _build_sort(self, sort_params: Dict) -> List[Dict]:
        if not sort_params:
            return []
        
        field = sort_params.get("field")
        order = sort_params.get("order", "asc")
        
        if not field:
            return []
        
        return [{
            "field_name": field,
            "desc": order == "desc"
        }]
