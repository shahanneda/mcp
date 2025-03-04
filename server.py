import random
from mcp.server.fastmcp import FastMCP, Image
import sys
import os
import subprocess
import logging
from lumaai import LumaAI
import asyncio
import requests
import time
import tempfile
import uuid

# Set up logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("wallpaper")

# Create an MCP server with dependencies
mcp = FastMCP("LumaLabs", dependencies=["lumaai", "requests"])

# Create a temporary directory for storing generated wallpapers
WALLPAPER_DIR = os.path.join(tempfile.gettempdir(), "mcp_wallpapers")
os.makedirs(WALLPAPER_DIR, exist_ok=True)
logger.info(f"Using temporary directory for wallpapers: {WALLPAPER_DIR}")

# Helper functions
async def _generate_image_helper(prompt: str) -> tuple[bytes | None, str | None, str]:
    """Helper function to generate an image from a prompt.
    
    Args:
        prompt: Text description of the image to generate
    
    Returns:
        Tuple of (image_data, image_format, error_message)
        If successful, error_message will be empty
    """
    # Initialize Luma client directly in the tool
    api_key = os.environ.get("LUMAAI_API_KEY")
    if not api_key:
        logger.error("LUMAAI_API_KEY environment variable not set")
        return None, None, "Error: LUMAAI_API_KEY not set"
    
    # Create Luma client
    try:
        client = LumaAI(auth_token=api_key)
        
        # Start the generation
        logger.info(f"Starting image generation with prompt: {prompt}")
        generation = client.generations.image.create(prompt=prompt)
        
        # Poll until completion
        completed = False
        max_attempts = 30  # Prevent infinite loops
        attempts = 0
        
        while not completed and attempts < max_attempts:
            generation = client.generations.get(id=generation.id)
            if generation.state == "completed":
                completed = True
            elif generation.state == "failed":
                error_msg = f"Generation failed: {generation.failure_reason}"
                logger.error(error_msg)
                return None, None, error_msg
            
            logger.info("Waiting for image generation to complete...")
            attempts += 1
            await asyncio.sleep(2)  # Use asyncio.sleep in async function
        
        if not completed:
            error_msg = "Image generation timed out"
            logger.error(error_msg)
            return None, None, error_msg
        
        # Download the image
        image_url = generation.assets.image
        logger.info(f"Image generated successfully, downloading from: {image_url}")
        
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            # Return image data and format
            return response.content, "png", ""
        else:
            error_msg = f"Failed to download image: HTTP {response.status_code}"
            logger.error(error_msg)
            return None, None, error_msg
            
    except Exception as e:
        error_message = f"Error generating image: {str(e)}"
        logger.error(error_message)
        return None, None, error_message

def _set_wallpaper_helper(image_path: str) -> tuple[bool, str]:
    """Helper function to set the wallpaper from a file path.
    
    Args:
        image_path: Full path to the image file
    
    Returns:
        Tuple of (success, message)
    """
    logger.info(f"Setting wallpaper from path: {image_path}")
    
    # Check if the file exists
    if not os.path.exists(image_path):
        error_msg = f"Image file not found: {image_path}"
        logger.error(error_msg)
        return False, error_msg
    
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
        
        logger.info(f"Wallpaper successfully set to {image_path}")
        return True, f"Wallpaper set to {os.path.basename(image_path)}"
    except subprocess.CalledProcessError as e:
        error_msg = f"Error setting wallpaper: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

async def _save_image_to_file(image_data: bytes, prompt: str) -> str:
    """Save image data to a file in the temporary directory.
    
    Args:
        image_data: The binary image data
        prompt: The original prompt (used for filename)
    
    Returns:
        The full path to the saved image file
    """
    # Create a filename based on the prompt and a UUID
    safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt)[:30]
    filename = f"{safe_prompt}_{uuid.uuid4().hex[:8]}.png"
    file_path = os.path.join(WALLPAPER_DIR, filename)
    
    # Save the image data to the file
    with open(file_path, "wb") as f:
        f.write(image_data)
    
    logger.info(f"Saved generated image to {file_path}")
    return file_path


@mcp.tool()
async def generate_image(prompt: str) -> Image:
    """Generate an image using Luma Labs AI.
    
    Args:
        prompt: Text description of the image to generate
    
    Returns:
        The generated image
    """
    image_data, image_format, error_message = await _generate_image_helper(prompt)
    
    if error_message:
        return Image(data=error_message.encode(), format="text")
    
    return Image(data=image_data, format=image_format)

@mcp.tool()
async def generate_wallpaper(prompt: str) -> str:
    """Generate a wallpaper image from a prompt and save it to a temporary directory.
    
    Args:
        prompt: Text description of the wallpaper to generate
    
    Returns:
        The path to the generated wallpaper image or an error message
    """
    logger.info(f"generate_wallpaper called with prompt: {prompt}")
    
    image_data, image_format, error_message = await _generate_image_helper(prompt)
    
    if error_message or image_data is None:
        return f"Error generating wallpaper: {error_message}"
    
    # Save the image to a file
    file_path = await _save_image_to_file(image_data, prompt)
    
    return f"Wallpaper generated and saved to: {file_path}"

@mcp.tool()
def set_image_from_path(image_path: str) -> str:
    """Set the wallpaper using an image file from a specific path.
    
    Args:
        image_path: Full path to the image file to use as wallpaper
    
    Returns:
        A message indicating whether the wallpaper was set successfully
    """
    logger.info(f"set_image_from_path called with image_path: {image_path}")
    
    success, message = _set_wallpaper_helper(image_path)
    return message

@mcp.tool()
async def generate_and_set_wallpaper(prompt: str) -> str:
    """Generate a wallpaper from a prompt and set it as the wallpaper of the computer.
    
    Args:
        prompt: Text description of the wallpaper to generate
    
    Returns:
        A message indicating whether the wallpaper was generated and set successfully
    """
    logger.info(f"generate_and_set_wallpaper called with prompt: {prompt}")
    
    # Generate the image
    image_data, image_format, error_message = await _generate_image_helper(prompt)
    
    if error_message or image_data is None:
        return f"Error generating wallpaper: {error_message}"
    
    # Save the image to a file
    file_path = await _save_image_to_file(image_data, prompt)
    
    # Set the wallpaper
    success, message = _set_wallpaper_helper(file_path)
    
    if success:
        return f"Wallpaper generated from prompt '{prompt}' and set successfully"
    else:
        return f"Wallpaper generated but failed to set: {message}"

if __name__ == "__main__":
    # Log server startup
    logger.info("MCP Wallpaper Server starting...")
    
    # Run the server
    mcp.run()
    