from typing import List
from XAgent.agent.plan_generate_agent import PlanGenerateAgent
from XAgent.utils import RequiredAbilities
from XAgent.message_history import Message

class PlanRefineAgent(PlanGenerateAgent):
    """PlanRefineAgent 是 PlanGenerateAgent 的子类，负责精炼计划。

    该类利用计划精炼的所需能力来解析信息并生成精炼的计划。它包括作为所需表达式的占位符。

    属性:
        abilities: 代理所需能力的集合。对于 PlanRefineAgent，它包括计划精炼。
    """
    abilities = set([RequiredAbilities.plan_refinement])

    def parse(
        self,
        placeholders: dict = {},
        arguments: dict = None,
        functions=None,
        function_call=None,
        stop=None,
        additional_messages: List[Message] = [],
        additional_insert_index: int = -1,
        *args,
        **kwargs
    ):
        """ 解析信息以精炼现有计划。

        该方法用相应的表达式填充占位符，然后处理提示和附加消息并将其合并到最终消息中。最后，调用 PlanGenerateAgent 类的 'generate' 方法生成最终消息。

        参数:
            placeholders (dict, 可选): 用于填充部分完成的文本片段的所需表达式。
            arguments (dict, 可选): 函数的参数。
            functions (可选): 要执行的函数。
            function_call (可选): 来自用户的功能请求。
            stop (可选): 在某个特定点停止解析。
            additional_messages (List[Message], 可选): 要包含在最终消息中的附加消息。
            additional_insert_index (int, 可选): 在提示消息中插入附加消息的索引。
            *args: 可变长度的参数列表。
            **kwargs: 任意关键字参数。

        返回:
            object: 由提供的占位符、参数、函数和消息生成的精炼计划。
        """
        
        # 填充占位符，生成初始提示消息
        prompt_messages = self.fill_in_placeholders(placeholders)
        # 将附加消息插入到提示消息中的指定位置
        messages = prompt_messages[:additional_insert_index] + additional_messages + prompt_messages[additional_insert_index:]
        
        # 调用 generate 方法生成精炼计划并返回结果
        return self.generate(
            messages=messages,
            arguments=arguments,
            functions=functions,
            function_call=function_call,
            stop=stop,
            *args, **kwargs
        )