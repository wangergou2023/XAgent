from typing import List
from XAgent.agent.base_agent import BaseAgent
from XAgent.utils import RequiredAbilities
from XAgent.message_history import Message

class ReflectAgent(BaseAgent):
    """ReflectAgent 类继承了 BaseAgent 类。它主要具有反思的能力，
    这意味着它可以反思聊天或对话，并根据收到的消息生成响应。

    属性:
        abilities (set): 代理所需的能力，在这种情况下是反思能力。
    """

    abilities = set([RequiredAbilities.reflection])

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
        该函数用于解析各种参数，并使用这些解析后的参数调用生成函数。

        参数:
            placeholders (dict, 可选): 代理响应的占位符。
            arguments (dict, 可选): 影响代理响应的参数。
            functions (functions, 可选): 引导代理响应的函数。
            function_call (FunctionType, 可选): 生成代理响应的函数调用。
            stop (bool, 可选): 停止响应生成的标志。
            additional_messages (list, 可选): 要包含在响应中的附加消息。

        返回:
            object: 代理生成的响应。
        """
        # 填充占位符，生成初始提示消息
        prompt_messages = self.fill_in_placeholders(placeholders)
        # 将附加消息添加到初始提示消息中
        messages = prompt_messages + additional_messages

        # 调用 generate 方法生成响应并返回结果
        return self.generate(
            messages=messages,
            arguments=arguments,
            functions=functions,
            function_call=function_call,
            stop=stop,
            *args, **kwargs
        )