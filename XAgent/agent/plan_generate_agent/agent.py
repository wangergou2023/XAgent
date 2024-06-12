from typing import List
from XAgent.agent.base_agent import BaseAgent
from XAgent.utils import RequiredAbilities
from XAgent.ai_functions import function_manager, objgenerator
from XAgent.message_history import Message

class PlanGenerateAgent(BaseAgent):
    """
    该类负责计划生成。它是BaseAgent的子类。

    属性:
        abilities: 一个集合，表示该代理所需的能力。
    """
    abilities = set([RequiredAbilities.plan_generation])

    def parse(
        self,
        placeholders: dict = {},
        arguments: dict = None,
        functions=None,
        function_call=None,
        stop=None,
        additional_messages: List[Message] = [],
        *args,
        **kwargs
    ):
        """
        该方法用于解析占位符、参数、函数调用和附加消息以生成计划。

        参数:
            placeholders (dict, 可选): 包含要填充到消息中的占位符的字典。
            arguments (dict, 可选): 包含要在函数中使用的参数的字典。
            functions: 计划生成过程中要使用的函数。
            function_call: 表示函数调用的对象。
            stop: 如果指定，则停止计划生成过程的条件。
            additional_messages (List[Message], 可选): 要添加到初始提示消息中的附加消息列表。
            *args: 可变长度的参数列表。
            **kwargs: 任意关键字参数。

        返回:
            该方法返回由“generate”方法生成的计划结果。
        """
        # 填充占位符，生成初始提示消息
        prompt_messages = self.fill_in_placeholders(placeholders)
        # 将附加消息添加到初始提示消息中
        messages = prompt_messages + additional_messages

        # 调用generate方法生成计划并返回结果
        return self.generate(
            messages=messages,
            arguments=arguments,
            functions=functions,
            function_call=function_call,
            stop=stop,
            *args, **kwargs
        )