"""
LLM客户端封装
支持DeepSeek API / Ollama / 任何OpenAI兼容API
自动从项目根目录的.env文件读取配置
"""
import os
import json
from openai import OpenAI
from typing import List, Dict, Optional, Callable


def _find_env_file():
    """从项目根目录查找.env文件"""
    search_paths = [
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # 从llm_client.py往上
        os.getcwd(),                                                   # 当前工作目录
    ]
    for base in search_paths:
        env_path = os.path.join(base, '.env')
        if os.path.exists(env_path):
            return env_path
    return None


def _load_env_file(env_path: str):
    """手动解析.env文件，不依赖python-dotenv"""
    if not env_path or not os.path.exists(env_path):
        return
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()
                if key and not os.environ.get(key):
                    os.environ[key] = value


class LLMClient:
    """LLM调用客户端"""
    
    def __init__(self, 
                 model: str = None,
                 base_url: str = None,
                 api_key: str = None,
                 temperature: float = 0.3,
                 max_retries: int = 2):
        """初始化，自动从.env加载配置"""
        # 首次导入时加载.env
        if not os.environ.get("LLM_API_KEY"):
            env_path = _find_env_file()
            _load_env_file(env_path)
        
        self.model = model or os.getenv("LLM_MODEL", "deepseek-chat")
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
        api_key = api_key or os.getenv("LLM_API_KEY", "")
        
        if not api_key:
            raise ValueError(
                "API Key未配置！请在项目根目录的.env文件中设置LLM_API_KEY\n"
                f"已检查路径: {_find_env_file()}"
            )
        
        self.temperature = temperature
        self.max_retries = max_retries
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.base_url,
            timeout=60
        )
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             temperature: Optional[float] = None,
             stream: bool = False,
             on_chunk: Optional[Callable[[str], None]] = None) -> Optional[str]:
        """调用LLM"""
        temp = temperature if temperature is not None else self.temperature
        
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    stream=stream,
                )
                
                if stream:
                    collected = []
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            collected.append(content)
                            if on_chunk:
                                on_chunk(content)
                    return "".join(collected)
                else:
                    return response.choices[0].message.content
                    
            except Exception as e:
                print(f"  [LLM] 第{attempt+1}次调用失败: {e}")
                if attempt < self.max_retries:
                    print(f"  [LLM] 准备重试...")
                else:
                    print(f"  [LLM] 已达最大重试次数，返回None")
                    return None
    
    def chat_with_json(self,
                       messages: List[Dict[str, str]],
                       fallback: dict = None) -> Optional[dict]:
        """调用LLM并解析JSON响应"""
        result = self.chat(messages, temperature=0.1, stream=False)
        if not result:
            return fallback
        
        try:
            start = result.index('{')
            end = result.rindex('}') + 1
            json_str = result[start:end]
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError) as e:
            print(f"  [LLM] JSON解析失败: {e}")
            print(f"  [LLM] 原始输出预览: {result[:200]}...")
            return fallback if fallback else {"error": "JSON解析失败", "raw": result[:500]}


if __name__ == '__main__':
    client = LLMClient()
    print(f"[测试] 连接 {client.base_url}")
    print(f"[测试] 模型 {client.model}")
    
    test_messages = [
        {"role": "system", "content": "一句话回答。"},
        {"role": "user", "content": "你好，赛博判官"}
    ]
    
    print("[测试] 正在调用API...")
    result = client.chat(test_messages, stream=True)
    if result:
        print(f"\n[测试] 响应成功，共{len(result)}字符")
    else:
        print("[测试] 调用失败，检查API Key和网络")
