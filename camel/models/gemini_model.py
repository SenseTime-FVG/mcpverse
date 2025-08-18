# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
import os
import copy
from typing import Any, Dict, List, Optional, Type, Union

from openai import AsyncStream, Stream
from pydantic import BaseModel

from camel.configs import Gemini_API_PARAMS, GeminiConfig
from camel.messages import OpenAIMessage
from camel.models.openai_compatible_model import OpenAICompatibleModel
from camel.types import (
    ChatCompletion,
    ChatCompletionChunk,
    ModelType,
)
from camel.utils import (
    BaseTokenCounter,
    api_keys_required,
    get_current_agent_session_id,
    update_langfuse_trace,
)

if os.environ.get("LANGFUSE_ENABLED", "False").lower() == "true":
    try:
        from langfuse.decorators import observe
    except ImportError:
        from camel.utils import observe
else:
    from camel.utils import observe


class GeminiModel(OpenAICompatibleModel):
    r"""Gemini API in a unified OpenAICompatibleModel interface.

    Args:
        model_type (Union[ModelType, str]): Model for which a backend is
            created, one of Gemini series.
        model_config_dict (Optional[Dict[str, Any]], optional): A dictionary
            that will be fed into:obj:`openai.ChatCompletion.create()`. If
            :obj:`None`, :obj:`GeminiConfig().as_dict()` will be used.
            (default: :obj:`None`)
        api_key (Optional[str], optional): The API key for authenticating with
            the Gemini service. (default: :obj:`None`)
        url (Optional[str], optional): The url to the Gemini service.
            (default: :obj:`https://generativelanguage.googleapis.com/v1beta/
            openai/`)
        token_counter (Optional[BaseTokenCounter], optional): Token counter to
            use for the model. If not provided, :obj:`OpenAITokenCounter(
            ModelType.GPT_4O_MINI)` will be used.
            (default: :obj:`None`)
        timeout (Optional[float], optional): The timeout value in seconds for
            API calls. If not provided, will fall back to the MODEL_TIMEOUT
            environment variable or default to 180 seconds.
            (default: :obj:`None`)
        max_retries (int, optional): Maximum number of retries for API calls.
            (default: :obj:`3`)
        **kwargs (Any): Additional arguments to pass to the client
            initialization.
    """

    @api_keys_required(
        [
            ("api_key", 'GEMINI_API_KEY'),
        ]
    )
    def __init__(
        self,
        model_type: Union[ModelType, str],
        model_config_dict: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        token_counter: Optional[BaseTokenCounter] = None,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> None:
        if model_config_dict is None:
            model_config_dict = GeminiConfig().as_dict()
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        url = url or os.environ.get(
            "GEMINI_API_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        timeout = timeout or float(os.environ.get("MODEL_TIMEOUT", 180))
        super().__init__(
            model_type=model_type,
            model_config_dict=model_config_dict,
            api_key=api_key,
            url=url,
            token_counter=token_counter,
            timeout=timeout,
            max_retries=max_retries,
            **kwargs,
        )

    def _process_messages(self, messages) -> List[OpenAIMessage]:
        r"""Process the messages for Gemini API to ensure no empty content,
        which is not accepted by Gemini.
        """
        processed_messages = []
        for msg in messages:
            msg_copy = msg.copy()
            if 'content' in msg_copy and msg_copy['content'] == '':
                msg_copy['content'] = 'null'
            processed_messages.append(msg_copy)
        return processed_messages

    @observe()
    def _run(
        self,
        messages: List[OpenAIMessage],
        response_format: Optional[Type[BaseModel]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Union[ChatCompletion, Stream[ChatCompletionChunk]]:
        r"""Runs inference of Gemini chat completion.

        Args:
            messages (List[OpenAIMessage]): Message list with the chat history
                in OpenAI API format.
            response_format (Optional[Type[BaseModel]]): The format of the
                response.
            tools (Optional[List[Dict[str, Any]]]): The schema of the tools to
                use for the request.

        Returns:
            Union[ChatCompletion, Stream[ChatCompletionChunk]]:
                `ChatCompletion` in the non-stream mode, or
                `Stream[ChatCompletionChunk]` in the stream mode.
        """

        # Update Langfuse trace with current agent session and metadata
        agent_session_id = get_current_agent_session_id()
        if agent_session_id:
            update_langfuse_trace(
                session_id=agent_session_id,
                metadata={
                    "agent_id": agent_session_id,
                    "model_type": str(self.model_type),
                },
                tags=["CAMEL-AI", str(self.model_type)],
            )

        response_format = response_format or self.model_config_dict.get(
            "response_format", None
        )
        messages = self._process_messages(messages)
        if response_format:
            if tools:
                raise ValueError(
                    "Gemini does not support function calling with "
                    "response format."
                )
            result: Union[ChatCompletion, Stream[ChatCompletionChunk]] = (
                self._request_parse(messages, response_format)
            )
        else:
            result = self._request_chat_completion(messages, tools)

        return result

    @observe()
    async def _arun(
        self,
        messages: List[OpenAIMessage],
        response_format: Optional[Type[BaseModel]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]:
        r"""Runs inference of OpenAI chat completion in async mode.

        Args:
            messages (List[OpenAIMessage]): Message list with the chat history
                in OpenAI API format.
            response_format (Optional[Type[BaseModel]]): The format of the
                response.
            tools (Optional[List[Dict[str, Any]]]): The schema of the tools to
                use for the request.

        Returns:
            Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]:
                `ChatCompletion` in the non-stream mode, or
                `AsyncStream[ChatCompletionChunk]` in the stream mode.
        """

        # Update Langfuse trace with current agent session and metadata
        agent_session_id = get_current_agent_session_id()
        if agent_session_id:
            update_langfuse_trace(
                session_id=agent_session_id,
                metadata={
                    "agent_id": agent_session_id,
                    "model_type": str(self.model_type),
                },
                tags=["CAMEL-AI", str(self.model_type)],
            )

        response_format = response_format or self.model_config_dict.get(
            "response_format", None
        )
        messages = self._process_messages(messages)
        if response_format:
            if tools:
                raise ValueError(
                    "Gemini does not support function calling with "
                    "response format."
                )
            result: Union[
                ChatCompletion, AsyncStream[ChatCompletionChunk]
            ] = await self._arequest_parse(messages, response_format)
        else:
            result = await self._arequest_chat_completion(messages, tools)

        return result


    def ensure_top_level_tool_type(self, tools_list: list) -> list:
        """
        确保每个工具定义都包含顶层的 'type': 'function'。
        这是API的基本要求。
        """
        for tool in tools_list:
            # 如果 'type' 字段不存在，或者不正确，就添加/修正它
            if tool.get("type") != "function":
                tool["type"] = "function"
        return tools_list


    def fix_all_nested_schema_errors(self, tools_list: list) -> list:
        """
        通过递归，修正工具定义中所有层级的、不符合API规范的 'type' 字段。

        Args:
            tools_list: 原始的工具定义列表。

        Returns:
            修正后的工具定义列表。
        """

        def _recursive_corrector(node):
            """一个可以递归修正 schema 节点的辅助函数"""
            
            # 如果是列表，则对列表中的每个元素进行递归
            if isinstance(node, list):
                return [_recursive_corrector(item) for item in node]

            # 如果不是字典，说明已经到了最底层，直接返回
            if not isinstance(node, dict):
                return node

            # --- 核心修正逻辑 ---
            # 1. 修正当前节点的 'type' 字段（如果它是一个列表）
            if 'type' in node and isinstance(node.get('type'), list):
                non_null_type = next((t for t in node['type'] if t != 'null'), None)
                if non_null_type:
                    node['type'] = non_null_type
                    # 注意：递归函数很难处理 'required' 字段，因为它需要父级上下文。
                    # 但修正 'type' 已经能解决你当前最主要的报错问题。

            # 2. 无论当前节点是否被修正，都继续递归检查它的所有子节点
            new_node = {}
            for key, value in node.items():
                new_node[key] = _recursive_corrector(value)
            
            return new_node


        # 使用深拷贝以避免修改原始对象
        import copy
        corrected_tools = copy.deepcopy(tools_list)

        for tool in corrected_tools:
            if 'function' in tool and 'parameters' in tool.get('function', {}):
                # 对每个工具的参数 schema 进行递归修正
                tool['function']['parameters'] = _recursive_corrector(tool['function']['parameters'])

        return corrected_tools



    def correct_tool_definition(self, tools_list: list) -> list:
        """
        修正工具定义中不符合API规范的 'type' 和 'required' 字段。

        Args:
            tools_list: 原始的工具定义列表。

        Returns:
            修正后的工具定义列表。
        """
        # 使用深拷贝以避免修改原始对象，如果需要的话
        # import copy
        # corrected_tools = copy.deepcopy(tools_list)
        corrected_tools = tools_list # 直接修改原始列表

        for tool in corrected_tools:
            if "function" not in tool or "parameters" not in tool["function"]:
                continue

            params = tool["function"]["parameters"]
            if "properties" not in params:
                continue

            properties = params["properties"]
            nullable_params = set()

            # 1. 修正参数类型，将 ['type', 'null'] 修正为 'type'
            for param_name, details in properties.items():
                if isinstance(details.get("type"), list):
                    # 找到列表中非 'null' 的类型
                    non_null_type = next((t for t in details["type"] if t != 'null'), None)
                    if non_null_type:
                        details["type"] = non_null_type
                        nullable_params.add(param_name)

            # 2. 从 'required' 列表中移除可选（即可为null）的参数
            if "required" in params and isinstance(params["required"], list):
                # 创建新的 required 列表，只包含不在 nullable_params 集合中的参数
                params["required"] = [p for p in params["required"] if p not in nullable_params]

        return corrected_tools


    def fix_tool_schema_refs_v2(self, tools_list: list) -> list:

        def _find_definition_by_path(root_schema: dict, path: str):

            if not path.startswith('#/'):
                return None
            parts = path.split('/')[1:]
            current_node = root_schema
            try:
                for part in parts:
                    current_node = current_node[part]
                return copy.deepcopy(current_node)
            except (KeyError, TypeError):
                return None

        
        def _resolve_refs_recursive_v2(current_node, root_schema: dict):
            if isinstance(current_node, dict):
                if '$ref' in current_node and isinstance(current_node['$ref'], str):

                    ref_path = current_node['$ref']

                    other_properties = {k: v for k, v in current_node.items() if k != '$ref'}


                    definition = _find_definition_by_path(root_schema, ref_path)

                    if definition is not None and isinstance(definition, dict):

                        definition.update(other_properties)

                        return _resolve_refs_recursive_v2(definition, root_schema)
                    else:
                        return current_node
                
                new_dict = {}
                for key, value in current_node.items():
                    new_dict[key] = _resolve_refs_recursive_v2(value, root_schema)
                return new_dict

            elif isinstance(current_node, list):
                return [_resolve_refs_recursive_v2(item, root_schema) for item in current_node]
            else:
                return current_node

        corrected_tools = copy.deepcopy(tools_list)
        for tool in corrected_tools:
            if 'function' in tool and 'parameters' in tool.get('function', {}):
                params_schema = tool['function']['parameters']
                resolved_schema = _resolve_refs_recursive_v2(params_schema, params_schema)
                tool['function']['parameters'] = resolved_schema
        return corrected_tools


    def fix_tool_schemas(self, tools: list) -> list:
        import copy 
        fixed_tools = copy.deepcopy(tools)

        
        for tool in fixed_tools:
            function_def = tool.get('function', {})
            parameters = function_def.get('parameters', {})
            properties = parameters.get('properties', {})
            
            tool_name = function_def.get('name', '未命名工具')

            # 遍历 'properties' 中的每一个参数定义
            for param_name, param_schema in properties.items():
                # 检查核心条件：参数定义是一个字典，且包含 'format' 但不包含 'type'
                if isinstance(param_schema, dict) and 'format' in param_schema and 'type' not in param_schema:
                    param_schema['type'] = 'string'

        return fixed_tools


    def _request_chat_completion(
        self,
        messages: List[OpenAIMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Union[ChatCompletion, Stream[ChatCompletionChunk]]:
        import copy

        request_config = copy.deepcopy(self.model_config_dict)
        # Remove strict and anyOf from each tool's function parameters since
        # Gemini does not support them
        if tools:
            for tool in tools:
                function_dict = tool.get('function', {})
                function_dict.pop("strict", None)

                # Process parameters to remove anyOf
                if 'parameters' in function_dict:
                    params = function_dict['parameters']
                    if 'properties' in params:
                        for prop_name, prop_value in params[
                            'properties'
                        ].items():
                            if 'anyOf' in prop_value:
                                # Replace anyOf with the first type in the list
                                first_type = prop_value['anyOf'][0]
                                params['properties'][prop_name] = first_type
                                # Preserve description if it exists
                                if 'description' in prop_value:
                                    params['properties'][prop_name][
                                        'description'
                                    ] = prop_value['description']

            tools = self.fix_all_nested_schema_errors(tools)   
            tools = self.fix_tool_schema_refs_v2(tools)    
            tools = self.ensure_top_level_tool_type(tools)
            request_config["tools"] = tools

    
        output = self._client.chat.completions.create(
            messages=messages,
            model=self.model_type,
            **request_config,
        )

        return output


    async def _arequest_chat_completion(
        self,
        messages: List[OpenAIMessage],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Union[ChatCompletion, AsyncStream[ChatCompletionChunk]]:
        import copy

        request_config = copy.deepcopy(self.model_config_dict)
        # Remove strict and anyOf from each tool's function parameters since
        # Gemini does not support them
        if tools:
            for tool in tools:
                function_dict = tool.get('function', {})
                function_dict.pop("strict", None)

                # Process parameters to remove anyOf
                if 'parameters' in function_dict:
                    params = function_dict['parameters']
                    if 'properties' in params:
                        for prop_name, prop_value in params[
                            'properties'
                        ].items():
                            if 'anyOf' in prop_value:
                                # Replace anyOf with the first type in the list
                                first_type = prop_value['anyOf'][0]
                                params['properties'][prop_name] = first_type
                                # Preserve description if it exists
                                if 'description' in prop_value:
                                    params['properties'][prop_name][
                                        'description'
                                    ] = prop_value['description']

            tools = self.fix_all_nested_schema_errors(tools)    
            tools = self.fix_tool_schema_refs_v2(tools)     
            tools = self.ensure_top_level_tool_type(tools)

            request_config["tools"] = tools

        output  = await self._async_client.chat.completions.create(
            messages=messages,
            model=self.model_type,
            **request_config,
        )

        return output

    def check_model_config(self):
        r"""Check whether the model configuration contains any
        unexpected arguments to Gemini API.

        Raises:
            ValueError: If the model configuration dictionary contains any
                unexpected arguments to Gemini API.
        """
        for param in self.model_config_dict:
            if param not in Gemini_API_PARAMS:
                raise ValueError(
                    f"Unexpected argument `{param}` is "
                    "input into Gemini model backend."
                )
