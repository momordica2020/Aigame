import asyncio
import datetime
import os
import re
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult, MessageChain
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api import message_components as Comp
from astrbot.api.all import CommandResult, Image, Plain
import aiohttp
import requests
import socket
import json
import random
import hashlib
from pathlib import Path
import sqlite3
from PIL import Image


@register("aigame", "lunarsa", "AI-Game", "0.1.0")
class AIGPlugin(Star):



    def __init__(self, context: Context):
        super().__init__(context)
        self.root_path = r"data/plugins/Aigame/data/"  # 根目录
        self.config_file_path = "config.json"  # 配置文件路径
        self.config_file_path2 = "config2.json"  # 第二个配置文件路径
        self.init_finished=False


        self.session = None  # aiohttp 会话
        #self.messages = {}
        self.eventinfos = {}
        #self.data = self.get_group_infos()
        #self.data_user = self.get_user_infos()



        # what_to_eat_data_path = self.root_path + "official/food.json"
        # if not os.path.exists(what_to_eat_data_path):
        #     with open(what_to_eat_data_path, "w", encoding="utf-8") as f:
        #         f.write(json.dumps([], ensure_ascii=False, indent=2))
        # with open(what_to_eat_data_path, "r", encoding="utf-8") as f:
        #     self.what_to_eat_data :list = json.loads(
        #         open(what_to_eat_data_path, "r", encoding="utf-8").read()
        #     )

        # morning_path = self.root_path + "official/morning.json"
        # if not os.path.exists(morning_path):
        #     with open(morning_path, "w", encoding="utf-8") as f:
        #         f.write(json.dumps({}, ensure_ascii=False, indent=2))
        # with open(morning_path, "r", encoding="utf-8") as f:
        #     # self.data = json.loads(f.read())
        #     self.good_morning_data = json.loads(f.read())








        # 存储每个群组的最后消息时间
        self.messages = {}
        # 存储事件信息，用于主动向群发送消息
        self.eventinfos = {}
        # 存储用户会话历史，用于多轮对话
        #self.conversation_history = {}




        self.players = {}  # 存储玩家信息


        
        # # 初始化 OpenAI 客户端
        # self.client = OpenAI(
        #     api_key=self.model_key,  # 请替换为您的 OpenAI API 密钥
        #     base_url=self.model_api
        # )

        # 初始化数据文件
        self.config = self.load_json(self.config_file_path)
        if self.config is None or self.config.get("bot_qq",None) is None:
            #配置文件损坏
            logger.error(f"配置文件 {self.config_file_path} 不完整，无法加载。请检查文件内容。")
            return
        
        
        

        





        loop = asyncio.get_event_loop()
        loop.create_task(self.periodic_task(30))
        
        
        self.init_finished = True
        


    

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def gamecmd(self, event: AstrMessageEvent):
        '''响应特定群的对话喵'''
        uni_id = f"{event.get_group_id()}_{event.get_self_id()}"
        # logger.warning(f"uni_id = {uni_id} : {event.message_str}")
        # if(random.randint(0, 10) > 3):
        #     return
        # if(self.messages.get(uni_id) != None):
        #     if datetime.now() - self.messages[uni_id] <= timedelta(seconds=random(10, 50)):
        #         return
        #self.messages[uni_id] = datetime.datetime.now()

        # 更新群组的事件信息
        self.eventinfos[uni_id] = event

        


        # logger.info(self.has_tag(id,"测试"))
        # logger.info(str(event.get_sender_id()) == '287859992')



        if not self.need_reply(event):
            # 不需要回复
            return
        message_str = self.get_message_str_without_at(event)

        group = event.get_group_id()
        sender_id = event.get_sender_id()
        sender_name = event.get_sender_name()
        message_str = event.message_str
        messages = event.get_messages()
        imgs = []
        for msg in messages:
            if isinstance(msg, Comp.Image):
                imgs.append(msg.url)
        logger.warning(f" {group} - {sender_name} ({sender_id}) :(img={len(imgs)}) {message_str} ")



        #if 













            
        # # 测试群的指定调用
        # res = await self.call_not_official(message_str, event)
        # if res:
        #     if self.root_path in res:
        #         yield event.image_result(res)
        #     else:
        #         yield event.plain_result(res)
        #     return
    

        # # 图片发送测试
        # if(message_str and message_str.startswith("日你妈") and event.get_sender_id() == '287859992'):
        #     yield event.image_result(f"{self.root_path}gifsfox/1_1.gif")
            
        





















    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''


    async def periodic_task(self, interval):
        '''游戏总循环'''
        while True:
            logger.info(f"game loop...(interval = {interval}s)")
            self.save_json(self.config_file_path2, self.config)
            #self.data = self.get_group_infos()
            #self.data_user = self.get_user_infos()
            
            for event in self.eventinfos.values():
                if random.randint(0, 100) > 95:
                    # umo = event.unified_msg_origin
                    logger.info(f"{event.get_self_name()}====>>{event.get_group_id()}")
                                  

            await asyncio.sleep(interval)

    async def send_message(self, group:str, message: str):
        '''主动发送群消息，要先获取并保留群event'''
        event = self.eventinfos.get(group,None)
        if not event:
            logger.error(f"未找到群组 {group} 的事件信息，无法发送消息。")
            return
        message_chain = MessageChain().message(message)
        await self.context.send_message(event.unified_msg_origin, message_chain)     



    
    def get_all_files(self, directory):
        """递归获取目录下所有文件的完整路径"""
        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths



    def generate_random_from_hash(self, input_message: str, maxval: int):
        # 使用SHA256算法计算消息的哈希值
        hash_object = hashlib.sha256(input_message.encode())
        hash_value = hash_object.hexdigest()

        # 将哈希值转换为一个整数
        hash_int = int(hash_value, 16)

        random_value = hash_int % (abs(maxval) + 1)
        return random_value



    async def download_image(self, url: str) -> str:
        """异步下载图片到本地临时文件"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"下载图片失败: HTTP {response.status}")

                # 创建临时文件
                _, ext = os.path.splitext(url)
                with tempfile.NamedTemporaryFile(suffix=ext or ".jpg", delete=False) as tmp_file:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        tmp_file.write(chunk)
                    return tmp_file.name
        except Exception as e:
            logger.error(f"图片下载失败: {str(e)}")
            raise Exception("图片下载失败，请重试")


    async def get_moe(self, message: AstrMessageEvent):
        """随机动漫图片"""
        shuffle = random.sample(self.moe_urls, len(self.moe_urls))
        for url in shuffle:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            return ""
                        data = await resp.read()
                        break
            except Exception as e:
                logger.error(f"从 {url} 获取图片失败: {e}。正在尝试下一个API。")
                continue
        # 保存图片到本地
        try:
            with open(f"{self.root_path}moe.jpg", "wb") as f:
                f.write(data)
            return f"{self.root_path}moe.jpg"

        except Exception as e:
            return ""

    async def hitokoto(self, message: AstrMessageEvent):
        """来一条一言"""
        url = "https://v1.hitokoto.cn"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return ""
                data = await resp.json()
        return f"{data["hitokoto"]}——{data["from"]}"


    async def save_what_eat_data(self):
        # path = os.path.abspath(os.path.dirname(__file__))
        with open(self.root_path + "/official/food.json", "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    self.what_to_eat_data, ensure_ascii=False, indent=2
                )
            )






























    def load_json(self, file_path: str):
        """加载 JSON 文件"""
        full_path = Path(os.path.join(self.root_path, file_path))
        if not full_path.exists():
            logger.error(f"文件 {full_path.absolute()} 不存在。")
            # 如果路径以斜杠结尾，或本身是目录，直接创建
            if full_path.is_dir():
                logger.info(f"创建目录 {full_path}")
                full_path.mkdir(parents=True, exist_ok=True)
            else:
                # 否则创建父目录（文件所在的文件夹）
                logger.info(f"创建目录 {full_path.parent}")
                full_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建空文件 {full_path}")
                full_path.touch()  # 创建空文件
            return {}
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
        

    def save_json(self, file_path: str, data):
        """保存数据到 JSON 文件"""
        full_path = os.path.join(self.root_path, file_path)
        # 如果路径以斜杠结尾，或本身是目录，直接创建
        if full_path.is_dir():
            logger.info(f"创建目录 {full_path}")
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            # 否则创建父目录（文件所在的文件夹）
            logger.info(f"创建目录 {full_path.parent}")
            full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


    
    def get(self, key: str):
        """获取配置项"""
        if self.init_finished:
            return self.config.get(key, [])
        else:
            logger.warning(f"尚未初始化，不能读取{key}配置项。")
            return []

    def need_reply(self, event: AstrMessageEvent):
        """判断是否需要回复"""
        if event.get_message_type() == "private" and not self.is_admin(event):
            return False
        
        if event.get_self_id() not in self.get("bot_qq"):
            return False
        if event.get_group_id() not in self.get("bot_group"):
            return False
        if event.get_sender_id() in self.get("bot_banned_qq") or event.get_sender_id() in self.get("bot_qq"):
            return False
        for msg in event.get_messages():
            # logger.warning(i)
            if isinstance(msg, Comp.At) and str(msg.qq) == str(event.get_self_id()):
                return True
            if hasattr(msg, 'type') and msg.type == 'Image':
                # 如果消息中包含图片，认为需要回复
                return True
        for keyword in self.get("bot_banned_keyword"):
            if event.message_str.startswith(keyword):
                return False
        if event.message_str.startswith(self.get("bot_name")):
            return True
        return False
    
    def get_message_str_without_at(self, event: AstrMessageEvent):
        '''获取消息里的纯文本部分'''
        message_str = ""
        for i in event.get_messages():
            if isinstance(i, Comp.Plain):
                message_str += i.text
        bot_name = self.get("bot_name")
        if bot_name and message_str.startswith(bot_name):
            message_str = message_str[len(bot_name):].strip()
        return message_str

    def is_admin(self, event: AstrMessageEvent):
        '''判断是否为bot管理员'''
        if event.get_sender_id() in self.get("bot_admin_qq"):
            return True
        return False


    async def download_image(self, url: str) -> str:
        """异步下载图片到本地临时文件"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"下载图片失败: HTTP {response.status}")

                # 创建临时文件
                _, ext = os.path.splitext(url)
                with tempfile.NamedTemporaryFile(suffix=ext or ".jpg", delete=False) as tmp_file:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        tmp_file.write(chunk)
                    return tmp_file.name
        except Exception as e:
            logger.error(f"图片下载失败: {str(e)}")
            raise Exception("图片下载失败，请重试")
        

    async def ai_single_cmd(self, cmd: str):
        """使用火山方舟API，一次性文本调用"""
        send_msg = []
        send_msg.append({"role": "user", "content": cmd})

        try:
            # 构造API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.get("huoshan_key")}" 
            }
            payload = {
                "model": self.get("huoshan_model_text"), 
                "messages": send_msg,
                "max_tokens": 500,
                "stream": False
            }
            response = requests.post(self.get("huoshan_api_text"), headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            send_msg.append({"role": "assistant", "content": response_text})
            return response_text
        except requests.RequestException as e:
            logger.error(f"火山方舟API错误: {e}")
            return ""

        

    #@filter.event_message_type(filter.EventMessageType.ALL)
    async def handle_ai(self, event: AstrMessageEvent, input_text: str):
        """处理所有类型的消息，并根据触发条件路由到面试功能"""
        # 生成唯一 ID，格式为 group_id_self_id
        uni_id = f"{event.get_group_id()}_{event.get_self_id()}"
        # 记录消息时间
        self.messages[uni_id] = datetime.datetime.now()
        # 存储事件信息
        self.eventinfos[uni_id] = event


        # 处理以 / 开头的命令
        if input_text.startswith("/"):
            response = await self.handle_interview_command(input_text, event, uni_id)
            return response
        elif input_text:
            return await self.provide_answer_feedback(input_text, uni_id)
            


    async def handle_interview_command(self, message_str: str, event: AstrMessageEvent, uni_id: str):
        """处理 / 命令及其子命令"""
        user_id = event.get_sender_id()
        parts = message_str[1:].split(" ")
        command = parts[0] if len(parts) >= 1 else "帮助"

        prompt =  "你是一个行业面试辅助专家，任务是帮助用户准备工作面试，提供定制化的建议、模拟面试问题以及对用户回答的反馈。保持专业、简洁、鼓励的语气。如果用户未指定行业或角色，主动询问。保持对话自然，并根据用户需求调整回答。"

        # 为用户初始化会话历史（如果不存在）
        if uni_id not in self.conversation_history:
            self.conversation_history[uni_id] = [
                {
                    "role": "system",
                    "content": (
                       prompt
                    )
                }
            ]

        # 处理不同子命令
        if command == "帮助":
            return (
                "面试辅助命令列表：\n"
                "[你的回答] - 获取对你的回答的反馈。\n"
                "/面试技巧 [行业] - 获取特定行业的面试技巧。\n"
                "/面试模拟 [行业/角色] - 获取一个模拟面试问题。\n"
                "/重新开始 - 重置会话历史。"
            )
        elif command == "面试技巧":
            industry = parts[1] if len(parts) > 2 else None
            return await self.get_interview_tips(industry, uni_id)
        elif command == "面试模拟":
            industry_or_role = " ".join(parts[1:]) if len(parts) > 2 else None
            return await self.get_mock_question(industry_or_role, uni_id)
        elif command == "重新开始":
            self.conversation_history[uni_id] = [
                {
                    "role": "system",
                    "content": (
                        prompt
                    )
                }
            ]
            await self.save_interview_data()
            return "会话历史已重置！请告诉我如何帮助你准备面试。"
        else:
            user_answer = " ".join(parts[1:]) if len(parts) > 2 else None
            if not user_answer:
                 return (
                "面试辅助命令列表：\n"
                "[你的回答] - 获取对你的回答的反馈。\n"
                "/面试技巧 [行业] - 获取特定行业的面试技巧。\n"
                "/面试模拟 [行业/角色] - 获取一个模拟面试问题。\n"
                "/重新开始 - 重置会话历史。"
                )
            
            #return "未知命令。请使用 /interview help 查看可用命令。"

    async def get_interview_tips(self, industry: str, uni_id: str):
        """使用火山方舟API生成面试技巧"""
        if not industry:
            self.conversation_history[uni_id].append(
                {"role": "user", "content": "请提供通用的面试技巧。"}
            )
        else:
            self.conversation_history[uni_id].append(
                {"role": "user", "content": f"请为{industry}行业提供面试技巧。"}
            )

        try:
            # 构造API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "model": self.model_name,  # 使用豆包1.5 Pro模型
                "messages": self.conversation_history[uni_id],
                "max_tokens": 500,
                "stream": False
            }
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            self.conversation_history[uni_id].append({"role": "assistant", "content": response_text})
            await self.save_interview_data()
            return response_text
        except requests.RequestException as e:
            logger.error(f"火山方舟API错误: {e}")
            return "抱歉，生成面试技巧时发生错误，请稍后再试。"

    async def get_mock_question(self, industry_or_role: str, uni_id: str):
        """使用火山方舟API生成模拟面试问题"""
        if not industry_or_role:
            self.conversation_history[uni_id].append(
                {"role": "user", "content": "请提供一个通用的模拟面试问题。"}
            )
        else:
            self.conversation_history[uni_id].append(
                {"role": "user", "content": f"请为{industry_or_role}提供一个模拟面试问题。"}
            )

        try:
            # 构造API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "model": self.model_name,
                "messages": self.conversation_history[uni_id],
                "max_tokens": 200,
                "stream": False
            }
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            self.conversation_history[uni_id].append({"role": "assistant", "content": response_text})
            await self.save_interview_data()
            return response_text
        except requests.RequestException as e:
            logger.error(f"火山方舟API错误: {e}")
            return "抱歉，生成模拟问题时发生错误，请稍后再试。"

    async def provide_answer_feedback(self, user_answer: str, uni_id: str):
        """使用火山方舟API为用户回答提供反馈"""
        self.conversation_history[uni_id].append(
            {"role": "user", "content": f"这是我对上一个问题的回答：{user_answer}。请提供反馈。"}
        )

        try:
            # 构造API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "model": self.model_name,
                "messages": self.conversation_history[uni_id],
                "max_tokens": 500,
                "stream": False
            }
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            response_text = result["choices"][0]["message"]["content"]
            self.conversation_history[uni_id].append({"role": "assistant", "content": response_text})
            await self.save_interview_data()
            return response_text
        except requests.RequestException as e:
            logger.error(f"火山方舟API错误: {e}")
            return "抱歉，提供反馈时发生错误，请稍后再试。"