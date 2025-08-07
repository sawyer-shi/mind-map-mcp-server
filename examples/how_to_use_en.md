# Mind Map MCP Server - Usage Guide

## Quick Start

### Using Docker (Recommended)

This is the simplest way to get started, just like installing an app on your phone!

1. **Make sure Docker is installed**
   - Download Docker Desktop from: https://www.docker.com/products/docker-desktop
   - Install and start Docker

2. **Start the service**
   ```bash
   docker-compose up -d
   ```

That's it! The service will start at http://localhost:8091.

## How to Use

### Basic Usage

The mind map service converts your text into beautiful mind map images. Just provide text in Markdown format, and you'll get a PNG image.

**Input Example:**
```markdown
# My Project Plan

## Phase 1: Research
- Market analysis
- Competitor research
- User interviews

## Phase 2: Development
- Design mockups
- Code implementation
- Testing

## Phase 3: Launch
- Marketing campaign
- User onboarding
- Performance monitoring
```

**Output:** A beautiful mind map PNG image showing your complete project structure!

### Using in Different Clients

#### Using in Dify
1. Add MCP service in Dify
2. Configure service address: http://localhost:8091/mcp
3. Use mind map functionality directly in chat

#### Using in CherryStudio
1. Add MCP Server configuration
2. Enter service address and port
3. Start creating mind maps

#### Using with Claude Desktop
Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mind-map-server": {
      "url": "http://localhost:8091/mcp"
    }
  }
}
```

## Advanced Features

### Custom Configuration

You can customize the service by creating a `.env` file:

```bash
# Copy the template
cp env.template .env

# Edit configuration
STREAMABLE_PORT=8091
HOST=0.0.0.0
DEBUG=false
```

### Multiple Transport Protocols

The service supports two transport protocols:

1. **stdio** - For local tools and command-line applications
2. **streamable-http** - For web applications (recommended)

### Local Installation

If you prefer not to use Docker:

```bash
# Auto-install and start
python start_server.py

# Or manual installation
pip install -r requirements.txt
npm install -g @markmap/cli
playwright install chromium
python mind_map_server.py
```

## Troubleshooting

### Common Issues

**Q: Service startup failed?**
A: Check if port 8091 is occupied, you can modify the port configuration in docker-compose.yml

**Q: Chinese characters display abnormally in generated images?**
A: The service has built-in Chinese font support. If there are still issues, please check Docker container logs

**Q: Connection timeout?**
A: Confirm the service has started and firewall is not blocking port 8091

**Q: Unsatisfied with image quality?**
A: You can adjust image size and quality through API parameters

### Getting Help

1. **Check logs**
   ```bash
   docker-compose logs -f
   ```

2. **Restart service**
   ```bash
   docker-compose restart
   ```

3. **Reset configuration**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## API Usage

### REST API Interface
The service provides REST API interface for direct calls:
```bash
curl -X POST http://localhost:8091/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "create_mind_map", "params": {"content": "# My Ideas\n## Sub Ideas"}}'
```

## Technical Details

### Architecture Design
1. **Markdown Parsing** - Process user input text
2. **HTML Conversion** - Use markmap-cli to create interactive HTML mind maps
3. **PNG Generation** - Use Playwright to capture HTML as PNG images
4. **MCP Protocol** - Standard MCP server implementation

### Supported Features
- 鉁?Markdown to PNG conversion
- 鉁?Chinese and English support
- 鉁?High-quality image output
- 鉁?Docker one-click deployment
- 鉁?Multiple transport protocols
- 鉁?Custom configuration support

### File Locations
- **Generated images**: `output/` directory
- **Temporary files**: `temp/` directory (auto-cleaned)
- **Configuration**: `.env` file
- **Logs**: `logs/` directory

## Examples

This directory contains several example files:

- `sample_mindmap.md` / `sample_mindmap_en.md` - Basic mind map examples
- `company_structure.md` / `company_structure_en.md` - Company organization chart examples
- `how_to_use.md` / `how_to_use_en.md` - Detailed usage instructions

You can use these examples to test the service and understand the Markdown format requirements.

## Support

For more help and support:
- Check the main README.md file
- Review example files in this directory
- Check Docker container logs for troubleshooting
- Ensure all dependencies are properly installed
