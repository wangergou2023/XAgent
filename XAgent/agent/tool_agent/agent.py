import json
import json5
import jsonschema
from typing import List
from colorama import Fore
from tenacity import retry, stop_after_attempt

from XAgent.agent.base_agent import BaseAgent
from XAgent.utils import RequiredAbilities
from XAgent.message_history import Message
from XAgent.logs import logger
from XAgent.data_structure.node import ToolNode
from XAgent.ai_functions import function_manager, objgenerator
from XAgent.config import CONFIG

class ToolAgent(BaseAgent):
    """
    这个类用于表示ToolAgent对象，它继承自BaseAgent。它主要关注工具树及其功能相关的操作。

    属性:
        abilities (set): 用于存储当前ToolAgent能力的集合。默认情况下设置为
        `RequiredAbilities.tool_tree_search`。
    """
    abilities = set([RequiredAbilities.tool_tree_search])

    @retry(stop=stop_after_attempt(CONFIG.max_retry_times), reraise=True)
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
        """
        这个函数使用`generate()`函数基于输入参数生成消息列表和令牌列表，根据具体条件修改它，并返回结果。
        
        参数:
            placeholders (dict, 可选): 存储占位符及其映射的字典对象。
            arguments (dict, 可选): 存储参数详情的字典对象。
            functions: 可插入`openai`类型函数字段的允许函数列表。
            function_call: 表示当前处理的函数调用的字典。
            stop: 循环的终止条件。
            additional_messages (list, 可选): 要附加到现有消息列表的附加消息列表。
            additional_insert_index (int, 可选): 插入附加消息的索引位置。
            *args: 父类`generate()`函数的可变长度参数列表。
            **kwargs: 父类`generate()`函数的任意关键字参数。
            
        返回:
            tuple: 包含解析消息的字典和令牌列表的元组。
            
        异常:
            AssertionError: 如果在可能的函数列表中找不到指定的函数架构。
            Exception: 如果工具调用参数的验证失败。
        """
        
        # 填充占位符，生成初始提示消息
        prompt_messages = self.fill_in_placeholders(placeholders)
        # 将附加消息插入到提示消息中的指定位置
        messages = prompt_messages[:additional_insert_index] + additional_messages + prompt_messages[additional_insert_index:]
        # 将消息转换为原始格式
        messages = [message.raw() for message in messages]
        
        # 临时禁用 openai 的参数
        if self.config.default_request_type == 'openai':
            arguments = None
            functions = list(filter(lambda x: x['name'] not in ['subtask_submit', 'subtask_handle'], functions))
            if CONFIG.enable_ask_human_for_help:
                functions += [function_manager.get_function_schema('ask_human_for_help')]
            messages[0]['content'] += '\n--- 可用工具 ---\n你可以在 "subtask_handle.tool_call" 函数字段中使用工具。\n请记住 "subtask_handle.tool_call.tool_input" 字段应始终为 JSON 格式，如下所述：\n{}'.format(json.dumps(functions, indent=2))
            
            def change_tool_call_description(message: dict, reverse: bool = False):
                des_pairs = [
                    ('Use tools to handle the subtask', 'Use "subtask_handle" to make a normal tool call to handle the subtask'),
                    ('5.1  Please remember to generate the function call field after the "criticism" field.\n  5.2  Please check all content is in json format carefully.', '5.1. Please remember to generate the "tool_call" field after the "criticism" field.\n  5.2. Please remember to generate comma if the "tool_call" field is after the "criticism" field.\n  5.3. Please check whether the **"tool_call"** field is in the function call json carefully.'),
                    ('After decide the action, use "subtask_handle" functions to apply action.', 'After decide the action, call functions to apply action.')
                ]
                
                for pair in des_pairs:
                    message['content'] = message['content'].replace(pair[0], pair[1]) if reverse else message['content'].replace(pair[1], pair[0])
                    
                return message
            
            messages[0] = change_tool_call_description(messages[0])
            functions = [function_manager.get_function_schema('subtask_submit'),
                         function_manager.get_function_schema('subtask_handle')]

        message, tokens = self.generate(
            messages=messages,
            arguments=arguments,
            functions=functions,
            function_call=function_call,
            stop=stop,
            *args, **kwargs
        )

        function_call_args: dict = message['function_call']['arguments']

        # 对于工具调用，我们需要验证工具调用参数是否存在
        if self.config.default_request_type == 'openai' and 'tool_call' in function_call_args:
            tool_schema = function_manager.get_function_schema(function_call_args['tool_call']["tool_name"])

            assert tool_schema is not None, f"函数 {function_call_args['tool_call']['tool_name']} 未找到！可能的架构验证错误！"
            
            tool_call_args = function_call_args['tool_call']['tool_input'] if 'tool_input' in function_call_args['tool_call'] else ''
            
            def validate():
                nonlocal tool_schema, tool_call_args
                if isinstance(tool_call_args, str):
                    tool_call_args = {} if tool_call_args == '' else json5.loads(tool_call_args)
                jsonschema.validate(instance=tool_call_args, schema=tool_schema['parameters'])
            
            try:
                validate()
            except Exception as e:  
                messages[0] = change_tool_call_description(messages[0], reverse=True)
                tool_call_args = objgenerator.dynamic_json_fixes(
                    broken_json=tool_call_args,
                    function_schema=tool_schema,
                    messages=messages,
                    error_message=str(e)
                )["choices"][0]["message"]["function_call"]["arguments"]
                validate()
            
            function_call_args['tool_call']['tool_input'] = tool_call_args
            
            message['function_call'] = function_call_args.pop('tool_call')
            message['function_call']['name'] = message['function_call'].pop('tool_name')
            message['function_call']['arguments'] = message['function_call'].pop('tool_input')
            message['arguments'] = function_call_args
                
        return message, tokens
    
    def message_to_tool_node(self, message) -> ToolNode:
        """
        此方法将给定的消息字典转换为 ToolNode 对象。
        
        参数:
            message (dict): 包含内容、函数调用和参数的消息数据字典。

        返回:
            ToolNode: 由提供的消息生成的 ToolNode 对象。
            
        警告:
            如果输入消息中缺少 `function_call` 字段，将记录警告消息。
        """
        
        # 假设消息格式
        # {
        #   "content": "内容是无用的",
        #   "function_call": {
        #       "name": "xxx",
        #       "arguments": "xxx"
        #  },
        #  "arguments": {
        #      "xxx": "xxx",
        #      "xxx": "xxx"   
        #  },
        # }
        
        new_node = ToolNode()
        if "content" in message.keys():
            print(message["content"])
            new_node.data["content"] = message["content"]
        if 'arguments' in message.keys():
            new_node.data['thoughts']['properties'] = message["arguments"]
        if "function_call" in message.keys():
            new_node.data["command"]["properties"]["name"] = message["function_call"]["name"]
            new_node.data["command"]["properties"]["args"] = message["function_call"]["arguments"]
        else:
            logger.typewriter_log("message_to_tool_node warning: no function_call in message", Fore.RED)

        return new_node