import re
import copy
import json5
from typing import List

from .prompt import SYSTEM_PROMPT

from XAgent.logs import logger
from XAgent.message_history import Message
from XAgent.agent.base_agent import BaseAgent

class DispatcherAgent(BaseAgent):
    """
    DispatcherAgent是BaseAgent的子类，其主要功能是根据任务需求将任务分配给不同的代理处理程序。

    属性:
    ------------
    config : object
        代理的配置设置。
    prompt_messages : List[Message]
        代理要分派的提示消息列表。
    """
    def __init__(self, config, prompt_messages: List[Message] = None):
        """
        初始化DispatcherAgent实例。

        参数:
        -------
        config : object
            代理的配置设置。
        prompt_messages : list, 可选
            代理要分派的提示消息列表，默认为None。
            如果未提供，则使用default_prompt_messages。
        """
        self.config = config
        self.prompt_messages = (
            self.default_prompt_messages if prompt_messages is None else prompt_messages
        )

    @property
    def default_prompt_messages(self):
        """
        返回默认的系统提示消息，以Message对象列表的形式。

        返回:
        -----------
        list[Message] : 
            包含默认提示消息的列表。
        """
        return [Message(role="system", content=SYSTEM_PROMPT)]

    def find_all_placeholders(self, prompt):
        """
        查找提示中所有的占位符。

        参数:
        --------
        prompt : str
            需要查找占位符的字符串。

        返回:
        --------
        list[str] : 
            提示中所有找到的占位符列表。
        """
        return re.findall(r"{{(.*?)}}", prompt)

    def construct_input_messages(
        self,
        task: str,
        example_input: str,
        example_system_prompt: str,
        example_user_prompt: str,
        retrieved_procedure: str,
    ):
        """
        通过用提供的数据替换prompt_messages中的占位符来构建输入消息。

        参数:
        ---------
        task : str
            要完成的任务。
        example_input : str
            任务的示例输入。
        example_system_prompt : str
            任务的示例系统提示。
        example_user_prompt : str
            任务的示例用户提示。
        retrieved_procedure : str
            任务的检索过程。

        返回:
        ---------
        list[Message] :
            包含构建的输入消息的列表，占位符已替换为提供的数据。
        """
        prompt_messages = copy.deepcopy(self.prompt_messages)
        # TODO: 使其更健壮。这里假设只有第一条消息是系统提示
        #       并且我们只更新第一条消息中的占位符。
        prompt_messages[0].content = (
            prompt_messages[0]
            .content.replace("{{example_system_prompt}}", example_system_prompt)
            .replace("{{example_user_prompt}}", example_user_prompt)
            .replace("{{retrieved_procedure}}", retrieved_procedure)
            .replace("{{task}}", task)
        )
        return prompt_messages  # + [Message(role="user", content=task)] 

    def extract_prompts_from_response(self, message):
        """
        从调度器的响应消息中提取额外的提示。

        参数:
        --------
        message : str 
           来自调度器的响应消息。

        返回:
        ---------
        str : 
            从消息中提取的额外提示；如果未找到，返回""。
        """
        try:
            additional_prompt = re.findall(r"ADDITIONAL USER PROMPT:?\n```(.*)```", message['content'], re.DOTALL)[0].strip()
        except IndexError as e:
            logger.error(
                f"未能从调度器的响应中提取提示:\n{message['content']}"
            )
            logger.error("回退到使用默认提示。")
            additional_prompt = ""
        return additional_prompt

    def retrieved_procedure(self, query: str) -> str:
        # TODO: 这个函数应该通过工具服务器实现

        """
        从外部站点检索与给定查询相关的过程。

        参数:
        --------
        query : str
            要检索相关过程的查询。

        返回:
        ---------
        str : 
            检索到的相关过程；如果检索失败，返回字符串“None”。
        """
        
        url = "https://open-procedures.replit.app/search/"
        try:
            import requests
            import json

            relevant_procedures = requests.get(url, params={'query': query}).json()[
                "procedures"
            ][0]
        except:
            # 对某些人来说，这失败是因为一个超级安全的SSL原因。
            # 由于这不是严格必要的，我们可以在日后再处理这个问题。应该以某种方式记录这个问题。
            relevant_procedures = "None"

        return relevant_procedures

    def parse(
        self,
        task: str,
        example_input: str,
        example_system_prompt: str,
        example_user_prompt: str,
        stop=None,
        **args,
    ) -> List[Message]:
        # TODO: 在生成提示时是否应考虑附加消息？
        # 当前计划生成和细化代理相同，因为我们在生成提示时不考虑附加消息。

        """
        解析任务和相关数据以生成提示消息。

        参数:
        ---------
        task : str
            要处理的任务。
        example_input : str
            与任务相关的示例输入。
        example_system_prompt : str
            与任务相关的示例系统提示。
        example_user_prompt : str
            与任务相关的示例用户提示。
        stop : str, 可选
            消息生成的停止条件，默认为None。

        返回:
        ---------
        Tuple[List[Message], List[str]] : 
            包含提示消息和令牌的元组。
        """
        message,tokens = self.generate(
            messages=self.construct_input_messages(
                task,
                example_input,
                example_system_prompt,
                example_user_prompt,
                ""  
            ),
            stop=stop,
            **args,
        )

        additional_prompt = message['arguments']['additional_prompt']

        prompt_messages = []
        if additional_prompt != "":
            example_user_prompt += "\n\n附加说明\n" + additional_prompt
        prompt_messages.append(Message(role="system", content=example_system_prompt))
        prompt_messages.append(Message(role="user", content=example_user_prompt))

        return prompt_messages, tokens