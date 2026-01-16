"""MCP Server for exposing task operations to the AI agent.

This module creates an MCP server that exposes task management tools
for the OpenAI Agent to use during conversation handling.
"""

from typing import Callable, Dict, Any
from .tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    TOOL_DEFINITIONS
)


class MCPServer:
    """MCP Server that manages tool registration and execution.

    This server acts as an intermediary between the AI agent and the
    task management functions, handling tool discovery and execution.
    """

    def __init__(self, name: str = "todo-mcp-server"):
        """Initialize the MCP server.

        Args:
            name: The server name for identification
        """
        self.name = name
        self.version = "1.0.0"
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register the default task management tools."""
        for tool_def in TOOL_DEFINITIONS:
            self.register_tool(
                name=tool_def["name"],
                description=tool_def["description"],
                function=tool_def["function"],
                parameters=tool_def["parameters"]
            )

    def register_tool(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: dict
    ) -> None:
        """Register a tool with the MCP server.

        Args:
            name: Tool name for identification
            description: Human-readable description for the agent
            function: The callable to execute when tool is invoked
            parameters: JSON schema for tool parameters
        """
        self._tools[name] = {
            "name": name,
            "description": description,
            "function": function,
            "parameters": parameters
        }

    def get_tools(self) -> list:
        """Get list of registered tools for agent configuration.

        Returns:
            List of tool definitions for OpenAI function calling format
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            for tool in self._tools.values()
        ]

    def get_tool_names(self) -> list:
        """Get list of registered tool names.

        Returns:
            List of tool name strings
        """
        return list(self._tools.keys())

    def execute_tool(self, name: str, arguments: dict) -> dict:
        """Execute a registered tool with the given arguments.

        Args:
            name: The tool name to execute
            arguments: Dictionary of arguments to pass to the tool

        Returns:
            The tool's result dictionary

        Raises:
            ValueError: If the tool name is not registered
        """
        if name not in self._tools:
            return {
                "status": "error",
                "error": f"Unknown tool: {name}"
            }

        tool = self._tools[name]
        try:
            result = tool["function"](**arguments)
            return result
        except TypeError as e:
            return {
                "status": "error",
                "error": f"Invalid arguments for {name}: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Tool execution failed: {str(e)}"
            }


# Global server instance
mcp_server = MCPServer()


def get_mcp_server() -> MCPServer:
    """Get the global MCP server instance.

    Returns:
        The singleton MCPServer instance
    """
    return mcp_server
