import requests
import logging
from typing import Dict, List
import config

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.ZHIPU_API_KEY
        self.api_url = config.ZHIPU_API_URL
        
        if not self.api_key:
            raise ValueError("智普API Key未配置，请设置ZHIPU_API_KEY环境变量或在config.py中配置")
    
    def chat(self, messages: List[Dict], temperature: float = 0.3, model: str = "glm-4.5-air") -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            logger.info(f"调用智普API，模型: {model}")
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"智普API返回格式异常: {result}")
                raise Exception("智普API返回格式异常")
        
        except requests.exceptions.Timeout:
            logger.error("智普API调用超时")
            raise Exception("大模型服务调用超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            logger.error(f"智普API调用失败: {str(e)}")
            raise Exception(f"大模型服务调用失败: {str(e)}")
        except Exception as e:
            logger.error(f"处理智普API响应失败: {str(e)}")
            raise Exception(f"处理大模型响应失败: {str(e)}")
    
    def chat_with_system(self, system_prompt: str, user_message: str, temperature: float = 0.3) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return self.chat(messages, temperature)
