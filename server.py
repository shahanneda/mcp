import random
from mcp.server.fastmcp import FastMCP, Image
import sys
import os
import subprocess
import logging
from lumaai import LumaAI

client = LumaAI()

# Set up logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("wallpaper")

# Create an MCP server with dependencies
mcp = FastMCP("LumaLabs", dependencies=["lumaai"])

# Initialize the Luma API client
@mcp.on_startup
def initialize_luma(ctx):
    # Get API key from environment variable
    api_key = os.environ.get("LUMA_API_KEY")
    if not api_key:
        ctx.error("LUMA_API_KEY environment variable not set")
        return
    
    # Store the client in the context
    ctx.luma_client = LumaAI(api_key=api_key)

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
    logger.info(f"generate_random_float called with min_value={min_value}, max_value={max_value}")
    return random.uniform(min_value, max_value)

@mcp.tool()
async def generate_image(prompt: str, ctx) -> Image:
    """Generate an image using Luma Labs AI.
    
    Args:
        prompt: Text description of the image to generate
    
    Returns:
        The generated image
    """
    # Access the client from the lifespan context
    luma_client = ctx.request_context.lifespan_context.get("luma_client")
    
    if not luma_client:
        return "Error: Luma API client not initialized. Make sure LUMA_API_KEY is set."
    
    # Generate the image
    try:
        image_data = await luma_client.generate_image(prompt)
        # Return as an MCP Image
        return Image(data=image_data, format="png")
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return f"Error generating image: {str(e)}"

@mcp.tool()
def set_wallpaper(image_name: str = "example1") -> str:
    """Set the wallpaper of the current user to one of the example images.
    
    Args:
        image_name: The name of the image to use (example1, example2, or example3)
                   without the .jpg extension
    
    Returns:
        A message indicating the wallpaper was set
    """
    # Log function call
    logger.info(f"set_wallpaper called with image_name={image_name}")
    
    # Map the image name to the full path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Current directory: {current_dir}")
    
    # Handle different input formats (with or without extension)
    if not image_name.endswith('.jpg'):
        image_name = f"{image_name}.jpg"
    
    # Validate the image exists
    valid_images = ["example1.jpg", "example2.jpg", "example3.jpg"]
    if image_name not in valid_images:
        logger.warning(f"Invalid image name: {image_name}")
        return f"Error: {image_name} is not a valid option. Choose from: example1, example2, or example3"
    
    image_path = os.path.join(current_dir, image_name)
    logger.info(f"Full image path: {image_path}")
    
    print("testing!", file=sys.stderr)
    # Set the wallpaper using osascript (AppleScript)
    script = f'''
    tell application "System Events" to tell every desktop to set picture to "{image_path}"
    '''
    
    try:
        logger.info(f"Executing AppleScript to set wallpaper to {image_path}")
        subprocess.run(["osascript", "-e", script], check=True)
        
        logger.info("Restarting Dock to apply changes")
        # Restart the Dock to ensure the wallpaper change takes effect
        subprocess.check_call("killall Dock", shell=True)
        
        logger.info(f"Wallpaper successfully set to {image_name}")
        return f"Wallpaper set to {image_name}"
    except subprocess.CalledProcessError as e:
        error_msg = f"Error setting wallpaper: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Log server startup
    logger.info("MCP Wallpaper Server starting...")
    
    # Run the server
    mcp.run()
    
    # Note: The following code will never be reached because mcp.run() blocks
    # until the server is terminated 