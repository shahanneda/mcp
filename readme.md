# LumaLabs Wallpaper Generator

Allows MCP clients to generate wallpaper images and set them as your desktop wallpaper on MacOS.

## Features

### Tools

- **generate_image**
  - **Description**: Generate an image using Luma Labs AI.
  - **Input**: `prompt` (string) - Text description of the image to generate.
  - **Output**: Returns the generated image.

- **generate_wallpaper**
  - **Description**: Generate a wallpaper image and save it to a temporary directory.
  - **Input**: `prompt` (string) - Text description of the wallpaper to generate.
  - **Output**: Returns the path to the generated wallpaper image.

- **set_image_from_path**
  - **Description**: Set the wallpaper using an image file from a specific path.
  - **Input**: `image_path` (string) - Full path to the image file to use as wallpaper.
  - **Output**: A message indicating whether the wallpaper was set successfully.

- **generate_and_set_wallpaper**
  - **Description**: Generate a wallpaper from a prompt and set it as your desktop wallpaper.
  - **Input**: `prompt` (string) - Text description of the wallpaper to generate.
  - **Output**: A message indicating whether the wallpaper was generated and set successfully.

## Getting Started

### Prerequisites
- macOS (for wallpaper setting functionality)
- Luma Labs API key

### Getting a Luma Labs API Key

1. Visit [Luma Labs Dream Machine API](https://lumalabs.ai/dream-machine/api)
4. Generate a new API key
5. Copy your API key for use with this server

### Installation

1. Install the required packages:

```bash
pip install "mcp[cli]" lumaai requests
```

2. Clone this repository or download the server.py file:

```bash
git clone <repository-url>
cd <repository-directory>
```

### Configuration
To run in development:
```bash
 LUMAAI_API_KEY=luma-02205263-af26-4e07-97f8-bf7daa0db86d-ec57c7f7-27ee-4628-a3f0-8c4ac80735f6 mcp dev server.py --with lumaai^
```

### Integration with Claude Desktop
To use this server with Claude Desktop, add the following to your Claude Desktop configuration file:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
    "wallpaper": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with",
        "lumaai",
        "--with",
        "requests",
        "mcp",
        "run",
        "/path/to//server.py"
      ],
      "env": {
        "LUMAAI_API_KEY": "luma-02205263-af26-4e07-97f8-bf7daa0db86d-ec57c7f7-27ee-4628-a3f0-8c4ac80735f6"
      }
    }
}
```

Replace `/path/to/server.py` with the absolute path to your server.py file.

### Testing with MCP Inspector

You can test the server using the MCP Inspector:

```bash
mcp dev server.py
```

## Limitations

- The wallpaper setting functionality currently only works on macOS
- Image generation may take up to a minute to complete
- Generated images are temporarily stored in your system's temp directory

## License

This MCP server is licensed under the MIT License.
