import json
import logging
import requests
import time
from collections import defaultdict
from threading import Lock
from flask import Flask, request, jsonify
import config
from intelligent_qa import IntelligentQA

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
qa_system = None

processed_messages = {}
processed_messages_lock = Lock()
MESSAGE_CACHE_TTL = 300

def is_message_processed(message_id: str) -> bool:
    current_time = time.time()
    
    with processed_messages_lock:
        expired_keys = [
            msg_id for msg_id, timestamp in processed_messages.items()
            if current_time - timestamp > MESSAGE_CACHE_TTL
        ]
        for key in expired_keys:
            del processed_messages[key]
        
        if message_id in processed_messages:
            return True
        
        processed_messages[message_id] = current_time
        return False

def init_qa_system():
    global qa_system
    try:
        qa_system = IntelligentQA()
        logger.info("问答系统初始化成功")
    except Exception as e:
        logger.error(f"问答系统初始化失败: {str(e)}")
        raise

def get_tenant_access_token() -> str:
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
            return result.get("tenant_access_token")
        else:
            logger.error(f"获取访问令牌失败: {result}")
            return None
    except Exception as e:
        logger.error(f"获取访问令牌异常: {str(e)}")
        return None

def send_message(chat_id: str, text: str):
    access_token = get_tenant_access_token()
    if not access_token:
        logger.error("无法发送消息：获取访问令牌失败")
        return
    
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            logger.info(f"消息发送成功: chat_id={chat_id}")
        else:
            logger.error(f"消息发送失败: {result}")
    except Exception as e:
        logger.error(f"消息发送异常: {str(e)}")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        
        if data.get("type") == "url_verification":
            challenge = data.get("challenge", "")
            logger.info(f"URL验证请求: challenge={challenge}")
            return jsonify({"challenge": challenge})
        
        header = data.get("header", {})
        event_type = header.get("event_type")
        
        if event_type == "im.message.receive_v1":
            event = data.get("event", {})
            message = event.get("message", {})
            message_id = message.get("message_id", "")
            
            if is_message_processed(message_id):
                logger.warning(f"消息已处理，跳过: message_id={message_id}")
                return jsonify({"code": 0})
            
            content_str = message.get("content", "{}")
            
            try:
                content = json.loads(content_str)
            except json.JSONDecodeError:
                content = {}
            
            user_message = content.get("text", "")
            chat_id = message.get("chat_id", "")
            
            if not user_message:
                logger.warning("收到空消息")
                return jsonify({"code": 0})
            
            logger.info(f"收到用户消息: message_id={message_id}, chat_id={chat_id}, message={user_message}")
            
            if user_message.strip() in ["帮助", "help", "?", "？"]:
                reply_text = qa_system.get_help_message()
            else:
                reply_text = qa_system.process_question(user_message)
            
            send_message(chat_id, reply_text)
        
        return jsonify({"code": 0})
    
    except Exception as e:
        logger.error(f"处理webhook异常: {str(e)}", exc_info=True)
        return jsonify({"code": -1, "msg": str(e)})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "feishu-bitable-qa"
    })

@app.route('/test', methods=['POST'])
def test():
    try:
        data = request.json
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"error": "请提供message参数"})
        
        result = qa_system.process_question(user_message)
        return jsonify({
            "message": user_message,
            "result": result
        })
    except Exception as e:
        logger.error(f"测试接口异常: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("启动飞书多维表格智能问答服务...")
    
    config.validate_config()
    logger.info("配置验证通过")
    
    init_qa_system()
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
