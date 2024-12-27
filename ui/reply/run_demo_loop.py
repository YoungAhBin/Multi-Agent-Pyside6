import json

from swarm import Swarm
from PySide6.QtCore import QObject, Signal

from PySide6.QtCore import QThread

class BackendThread(QThread):
    response_chunk = Signal(str)

    def __init__(self, user_input, starting_agent, context_variables=None, stream=False, debug=False):
        super().__init__()
        self.user_input = user_input
        self.starting_agent = starting_agent
        self.context_variables = context_variables or {}
        self.stream = stream
        self.debug = debug

    def process_and_print_streaming_response(self, response):
        content = ""
        last_sender = ""
    
        for chunk in response:
            if "sender" in chunk:
                last_sender = chunk["sender"]
    
            if "content" in chunk and chunk["content"] is not None:
                if not content and last_sender:
                    self.response_chunk.emit(
                        "<br>"
                        f'<span style="color: blue; font-weight: bold;">{last_sender}:</span> '
                        "<br>"
                    )
                    last_sender = ""
                self.response_chunk.emit(chunk["content"])
                content += chunk["content"]
    
            if "tool_calls" in chunk and chunk["tool_calls"] is not None:
                for tool_call in chunk["tool_calls"]:
                    f = tool_call["function"]
                    name = f["name"]
                    if not name:
                        continue
                    self.response_chunk.emit(
                        "<br>"
                        f'<span style="color: blue; font-weight: bold;">{last_sender}:</span> '
                        f'<span style="color: magenta; font-style: italic;">{name}</span>()'
			"<br>"
                    )
    
            if "delim" in chunk and chunk["delim"] == "end" and content:
                self.response_chunk.emit("<br>")
                content = ""
    
            if "response" in chunk:
                return chunk["response"]
    
    def pretty_print_messages(self,messages) -> None:
        response_text = ""
        for message in messages:
            if message["role"] != "assistant":
                continue
    
            # print agent name in blue
            response_text += f'<span style="color: blue; font-weight: bold;">{message["sender"]}:</span> '
    
            # print response, if any
            if message["content"]:
                response_text += f"{message['content']}<br>"
    
            # print tool calls in purple, if any
            tool_calls = message.get("tool_calls") or []
            if len(tool_calls) > 1:
                response_text += "<br>"  # 替代 print()
            for tool_call in tool_calls:
                f = tool_call["function"]
                name, args = f["name"], f["arguments"]
                arg_str = json.dumps(json.loads(args)).replace(":", "=")
                response_text += f'<span style="color: magenta;"><i>{name}</i></span>({arg_str[1:-1]})<br>'
    
        return response_text
    
    def run_demo_loop(
        self, user_input,starting_agent, context_variables=None, stream=False, debug=False
    ) -> None:
        client = Swarm()
    
        messages = []
        agent = starting_agent
   
        messages.append({"role": "user", "content": user_input})
    
        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables or {},
            stream=stream,
            debug=debug,
        )
    
        if stream:
            response = self.process_and_print_streaming_response(response)
        else:
            self.pretty_print_messages(response.messages)
            self.response_chunk.emit(response_text)
    
        messages.extend(response.messages)
        agent = response.agent

    def run(self):
        self.run_demo_loop(
            self.user_input,
            self.starting_agent,
            self.context_variables,
            self.stream,
            self.debug
        )
