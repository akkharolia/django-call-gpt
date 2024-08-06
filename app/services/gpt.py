import json
import time
import traceback
from app.services import *
from app.services import gpt_functions 
from app.common import openai_client, get_db
from app.services.functions_manifest import tools
from app.services.gpt_prompt import WELCOME_MSG, SYS_PROMPT
from app.services.event_emitter import EventEmitter

available_functions = {}
for tool in tools:
    function_name = tool['function']['name']
    available_functions[function_name] = getattr(gpt_functions, function_name, None)

class GPTService(EventEmitter):
    def __init__(self, ws):
        super().__init__()
        self.ws = ws
        self.openai = openai_client()
        self.user_context = [
           { 'role': 'system', 'content': SYS_PROMPT },
           { 'role': 'assistant', 'content': WELCOME_MSG }
        ]
        self.partial_response_index = 0
        self.call_sid = ''

    def set_call_sid(self, call_sid):
        self.user_context.append({'role': 'user', 'content': f'twilio callSid: {call_sid}'})
        self.call_sid = call_sid

    def validate_function_args(self, args):
        try:
            return json.loads(args)
        except json.JSONDecodeError:
            print(f'Warning: Double function arguments returned by OpenAI: {args}')
            if args.find('{') != args.rfind('{'):
                return json.loads(args[args.find('{'):args.find('}') + 1])

    def update_user_context(self, name, role, text):
        if name != 'user':
            self.user_context.append({ 'role': role, 'name': name, 'content': text })
        else:
            self.user_context.append({ 'role': role, 'content': text })
    
    def collect_tool_information(self, deltas):
        tool_calls = deltas.tool_calls or []
        if tool_calls:
            if tool_calls[0].function.name:
                # if tool_calls[0].function.name in ['appointment_booking', 'end_call']:
                #     time.sleep(15)
                #     self.ws.disconnect()
                    
                self.function_name = tool_calls[0].function.name
            if tool_calls[0].function.arguments:
                self.function_args += tool_calls[0].function.arguments

    def completion(self, text, interaction_count, role='user', name='user', call_sid=''):
        try:
            self.update_user_context(name, role, text)
            get_db().Conversation.insert_one({ 'role': role, 'content': text, 'call_sid': call_sid })
            stream = self.openai.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=self.user_context,
                tools=tools,
                stream=True,
                max_tokens=250
            )
            
            self.complete_response = ''
            self.partial_response = ''
            self.function_name = ''
            self.function_args = ''
            self.finish_reason = ''
            
            for chunk in stream:
                content = chunk.choices[0].delta.content
                deltas = chunk.choices[0].delta
                self.finish_reason = chunk.choices[0].finish_reason
                if deltas.tool_calls:
                    self.collect_tool_information(deltas)

                if self.finish_reason == 'tool_calls':
                    function_to_call = available_functions.get(self.function_name)
                    if function_to_call:
                        tool_data = next((tool for tool in tools if tool.get('function', {}).get('name') == self.function_name), None)
                        say = tool_data['function'].get('say')
                        if say:
                            self.emit('gptreply', 
                                      {'partial_response_index': None, 'partial_response': say},
                                      interaction_count)
                        
                        function_response = function_to_call(self.function_args)
                        print('function_response \t', function_response)
                        self.update_user_context(self.function_name, 'function', function_response)
                        self.completion(function_response, interaction_count, 'function', self.function_name)
                else:
                    content = content if content else ''
                    self.complete_response += content
                    self.partial_response += content
                    if content.strip().endswith('•') or self.finish_reason == 'stop':
                        self.gpt_reply = {
                            'partial_response_index': self.partial_response_index,
                            'partial_response': self.partial_response
                        }
                        self.emit('gptreply', self.gpt_reply, interaction_count)
                        print('gptreply >>>> emit')
                        self.partial_response_index += 1
                        self.partial_response = ''
            
            self.user_context.append({ 'role': 'assistant', 'content': self.complete_response })
            get_db().Conversation.insert_one({ 'role': 'assistant', 'content': self.complete_response, 'call_id': self.call_sid })
            print(f'GPT -> user context length: {len(self.user_context)}')
        except Exception as e:
            print(traceback.format_exc())
