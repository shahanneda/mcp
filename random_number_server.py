import random
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Random Number Generator")

@mcp.tool()
def generate_random_number(min_value: int = 1, max_value: int = 100) -> int:
    """Generate a random integer between min_value and max_value (inclusive).
    
    Args:
        min_value: The minimum possible value (default: 1)
        max_value: The maximum possible value (default: 100)
    
    Returns:
        A random integer
    """
    return random.randint(min_value, max_value)

@mcp.tool()
def generate_random_float(min_value: float = 0.0, max_value: float = 1.0) -> float:
    """Generate a random float between min_value and max_value.
    
    Args:
        min_value: The minimum possible value (default: 0.0)
        max_value: The maximum possible value (default: 1.0)
    
    Returns:
        A random float
    """
    return random.uniform(min_value, max_value)

if __name__ == "__main__":
    # Run the server
    mcp.run() 