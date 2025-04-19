# Browser Automation Agent

A powerful browser automation tool built with MCP (Model Controlled Program) that combines web scraping capabilities with LLM-powered intelligence. This agent can search Google, navigate to webpages, and intelligently scrape content from various websites including GitHub, Stack Overflow, and documentation sites.

## Features

- **Google Search Integration**: Finds and retrieves top search results for any query
- **Intelligent Web Scraping**: Tailored scraping strategies for different website types:
  - GitHub repositories
  - Stack Overflow questions and answers
  - Documentation pages
  - Generic websites
- **AI-Powered Processing**: Uses Mistral AI for understanding and processing scraped content
- **Stealth Mode**: Implements browser fingerprint protection to avoid detection
- **Content Saving**: Automatically saves both screenshots and text content from scraped pages

## Architecture

This project uses a client-server architecture powered by MCP:

- **Server**: Handles browser automation and web scraping tasks
- **Client**: Provides the AI interface using Mistral AI and LangGraph
- **Communication**: Uses stdio for client-server communication

## Requirements

- Python 3.8+
- Playwright
- MCP (Model Controlled Program)
- Mistral AI API key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/browser-automation-agent.git
cd browser-automation-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
playwright install
```

4. Create a `.env` file in the project root and add your Mistral AI API key:

```
MISTRAL_API_KEY=your_api_key_here
```

## Usage

### Running the Server

```bash
python main.py
```

### Running the Client

```bash
python client.py
```

### Sample Interaction

Once both the server and client are running:

1. Enter your query when prompted
2. The agent will:
   - Search Google for relevant results
   - Navigate to the top result
   - Scrape content based on the website type
   - Save screenshots and content to files
   - Return processed information

## Tool Functions

### `get_top_google_url`
Searches Google and returns the top result URL for a given query.

### `browse_and_scrape`
Navigates to a URL and scrapes content based on the website type.

### `scrape_github`
Specializes in extracting README content and code blocks from GitHub repositories.

### `scrape_stackoverflow`
Extracts questions, answers, comments, and code blocks from Stack Overflow pages.

### `scrape_documentation`
Optimized for extracting documentation content and code examples.

### `scrape_generic`
Extracts paragraph text and code blocks from generic websites.

## File Structure

```
browser-automation-agent/
├── main.py            # MCP server implementation
├── client.py          # Mistral AI client implementation
├── requirements.txt   # Project dependencies
├── .env               # Environment variables (API keys)
└── README.md          # Project documentation
```

## Output Files

The agent generates two types of output files with timestamps:

- `final_page_YYYYMMDD_HHMMSS.png`: Screenshot of the final page state
- `scraped_content_YYYYMMDD_HHMMSS.txt`: Extracted text content from the page

## Customization

You can modify the following parameters in the code:

- Browser window size: Adjust `width` and `height` in `browse_and_scrape`
- Headless mode: Set `headless=True` for invisible browser operation
- Number of Google results: Change `num_results` in `get_top_google_url`

## Troubleshooting

- **Connection Issues**: Ensure both server and client are running in separate terminals
- **Playwright Errors**: Make sure browsers are installed with `playwright install`
- **API Key Errors**: Verify your Mistral API key is correctly set in the `.env` file
- **Path Errors**: Update the path to `main.py` in `client.py` if needed

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with MCP, Playwright, and Mistral AI
