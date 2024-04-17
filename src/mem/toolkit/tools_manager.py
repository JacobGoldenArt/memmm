from mem.toolkit.tools import get_location_tool, get_weather_tool


class ToolsManager:
    def __init__(self):
        """
        Manages different tools available for the application, allowing for dynamic registration and usage of tools.
        """
        self.toolkit = {}
        self.register_tool(
            "get_weather",
            get_weather_tool,
            {
                "description": "Get the current weather in a given location",
                "parameters": {
                    "is_forecast": {
                        "type": "boolean",
                        "description": "true: returns seven day forecast, false: returns today's weather.",
                        "default": False,
                    },
                    "latitude": {
                        "type": "string",
                        "description": "The latitude of the location",
                    },
                    "longitude": {
                        "type": "string",
                        "description": "The longitude of the location",
                    },
                },
                "required": ["latitude", "longitude"],
            },
        )
        self.register_tool(
            "get_location",
            get_location_tool,
            {
                "description": "Get the location of the user based on their IP address",
                "parameters": {},
            },
        )

    def register_tool(self, name, function, metadata=None):
        """
        Registers a tool with associated metadata for use within the application.
        Args:
            name: A unique name for the tool.
            function: The function associated with the tool.
            metadata: Optional metadata describing the tool, including parameters and descriptions.
        """
        self.toolkit[name] = {"function": function, "metadata": metadata or {}}

    def available_tools(self):
        """
        Returns a list of all registered tools with their metadata.
        Useful for dynamic interfaces or API responses where tool capabilities need to be described.
        """
        return [
            {
                "name": name,
                "description": tool["metadata"].get(
                    "description", "No description available"
                ),
                "parameters": tool["metadata"].get("parameters", {}),
                "required": tool["metadata"].get("required", []),
            }
            for name, tool in self.toolkit.items()
        ]

    def execute_tool(self, tool_name, **kwargs):
        """
        Executes a registered tool by name with given arguments.
        Args:
            tool_name: The name of the tool to be executed.
            **kwargs: Keyword arguments to pass to the tool function.
        Throws:
            ValueError: If the tool is not registered.
        """
        if tool_name in self.toolkit:
            tool = self.toolkit[tool_name]["function"]
            return tool(**kwargs)
        else:
            raise ValueError(f"Tool {tool_name} is not registered.")
