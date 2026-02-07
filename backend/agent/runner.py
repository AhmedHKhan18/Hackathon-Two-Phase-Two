"""AI Agent Runner for executing conversations with tool support.

This module handles the execution of the Gemini agent with MCP tools,
processing user messages and returning agent responses.
"""

import json
from typing import List, Dict, Any, Optional

from .config import get_agent_config
from .prompts import SYSTEM_PROMPT
from mcp.server import get_mcp_server


class AgentRunner:
    """Runs the AI agent with MCP tool support.

    Handles message processing, tool execution, and response generation.
    """

    def __init__(self):
        """Initialize the agent runner."""
        # Lazy import google.genai to avoid hanging during module load
        # (the package does network calls on import that fail inside k8s)
        from google import genai

        self.config = get_agent_config()
        self.mcp_server = get_mcp_server()

        # Validate API key
        if not self.config.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")

        # Configure Gemini client
        self.client = genai.Client(api_key=self.config.api_key)

    def _convert_tools_to_gemini_format(self, openai_tools: List[Dict]) -> list:
        """Convert OpenAI-format tools to Gemini format.

        Args:
            openai_tools: List of tools in OpenAI format

        Returns:
            List of Gemini Tool objects
        """
        from google.genai import types

        function_declarations = []

        for tool in openai_tools:
            if tool["type"] == "function":
                func = tool["function"]
                parameters = func.get("parameters", {})

                # Build properties dict for Gemini
                properties = {}
                required = parameters.get("required", [])

                if "properties" in parameters:
                    for prop_name, prop_schema in parameters["properties"].items():
                        prop_type = prop_schema.get("type", "string").upper()
                        if prop_type == "INTEGER":
                            prop_type = "NUMBER"
                        properties[prop_name] = types.Schema(
                            type=prop_type,
                            description=prop_schema.get("description", "")
                        )

                function_declarations.append(
                    types.FunctionDeclaration(
                        name=func["name"],
                        description=func["description"],
                        parameters=types.Schema(
                            type="OBJECT",
                            properties=properties,
                            required=required
                        ) if properties else None
                    )
                )

        if function_declarations:
            return [types.Tool(function_declarations=function_declarations)]
        return []

    def run(
        self,
        user_message: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Execute the agent with a user message.

        Args:
            user_message: The user's message to process
            user_id: The authenticated user's ID for tool calls
            conversation_history: Optional list of prior messages

        Returns:
            Dict containing:
                - response: The agent's text response
                - tool_calls: List of tools called and their results
        """
        from google.genai import types

        # Get tools in Gemini format
        openai_tools = self.mcp_server.get_tools()
        gemini_tools = self._convert_tools_to_gemini_format(openai_tools)

        # Build conversation contents
        contents = []

        # Add conversation history
        if conversation_history:
            for msg in conversation_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if content:
                    # Map roles: assistant -> model, user stays user
                    gemini_role = "model" if role == "assistant" else "user"
                    contents.append(
                        types.Content(
                            role=gemini_role,
                            parts=[types.Part.from_text(text=content)]
                        )
                    )

        # Add current user message
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            )
        )

        # Track tool calls for response
        tool_calls_made = []

        # Run the conversation loop (handle tool calls)
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Generate response
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=gemini_tools if gemini_tools else None,
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens
                )
            )

            # Check for function calls in the response
            function_calls = []
            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        function_calls.append(part.function_call)

            if function_calls:
                # Add the model's response to contents
                contents.append(response.candidates[0].content)

                # Execute each function call and build responses
                function_response_parts = []

                for fc in function_calls:
                    function_name = fc.name
                    arguments = dict(fc.args) if fc.args else {}

                    # Inject user_id into all tool calls for security
                    arguments["user_id"] = user_id

                    # Execute the tool
                    result = self.mcp_server.execute_tool(function_name, arguments)

                    # Track the tool call
                    tool_calls_made.append({
                        "tool_name": function_name,
                        "arguments": {k: v for k, v in arguments.items() if k != "user_id"},
                        "result": result
                    })

                    # Build function response part
                    function_response_parts.append(
                        types.Part.from_function_response(
                            name=function_name,
                            response={"result": result}
                        )
                    )

                # Add function responses to contents
                contents.append(
                    types.Content(
                        role="user",
                        parts=function_response_parts
                    )
                )
            else:
                # No more function calls, we have the final response
                break

        # Extract final text response
        final_response = ""
        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if part.text:
                    final_response += part.text

        return {
            "response": final_response,
            "tool_calls": tool_calls_made
        }


# Global runner instance
_runner: Optional[AgentRunner] = None


def get_agent_runner() -> AgentRunner:
    """Get or create the global agent runner instance.

    Returns:
        AgentRunner instance
    """
    global _runner
    if _runner is None:
        _runner = AgentRunner()
    return _runner


def run_agent(
    user_message: str,
    user_id: str,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """Convenience function to run the agent.

    Args:
        user_message: The user's message to process
        user_id: The authenticated user's ID
        conversation_history: Optional list of prior messages

    Returns:
        Dict with response and tool_calls
    """
    runner = get_agent_runner()
    return runner.run(user_message, user_id, conversation_history)
