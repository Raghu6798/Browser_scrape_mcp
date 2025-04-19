from mcp.server.fastmcp import FastMCP
from firecrawl import FirecrawlApp
from tavily import TavilyClient
import re
import requests
from bs4 import BeautifulSoup
from rich.markdown import Markdown
from rich.console import Console
from dotenv import load_dotenv
import os
import io

load_dotenv()

mcp = FastMCP("Framework Summarizer")

app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_SEARCH_API"))

def render_markdown(markdown_text: str) -> str:
    """Render markdown text into formatted output.
    
    This function uses the rich library to render markdown content with proper formatting.
    It captures the output in a string and handles various markdown elements.
    
    Args:
        markdown_text (str): The markdown text to render.
        
    Returns:
        str: The rendered markdown content with proper formatting.
        
    Example:
        >>> content = "# Hello World\n\nThis is **bold** text."
        >>> rendered = render_markdown(content)
        >>> print(rendered)
    """
    try:
        # Create a console that writes to a string buffer
        console = Console(file=io.StringIO())
        
        # Create and render the markdown
        md = Markdown(markdown_text)
        console.print(md)
        
        # Get the rendered content from the buffer
        rendered = console.file.getvalue()
        console.file.close()
        
        return rendered
    except Exception as e:
        return f"Error rendering markdown: {str(e)}"

@mcp.tool()
def search_and_scrape(query:str):
    """Search for content using Tavily and scrape the most relevant result.
    
    This function performs a two-step process:
    1. Uses Tavily search API to find the most relevant URLs for a given query
    2. Scrapes the content from the top-ranked URL using Firecrawl
    
    Args:
        query (str): The search query to find relevant content. This query will be used
                    to search for and retrieve the most relevant webpage content.
        
    Returns:
        str: The scraped content in markdown format from the most relevant webpage.
        
    Example:
        >>> content = search_and_scrape("What is Python programming language?")
        >>> print(content)
        
    Raises:
        Exception: If the search fails or if the scraping process fails.
    """
    response = tavily_client.search(query, max_results=5)
    top_5_urls = [result['url'] for result in response.get('results', [])]
    url = top_5_urls[0]
    response = app.scrape_url(url=url, params={
	'formats': [ 'markdown' ],
})
    return response['markdown']

@mcp.tool()
def list_directory(path: str = ".") -> list:
    """List contents of a directory.
    
    This tool lists all files and directories in the specified path.
    If no path is provided, it lists the current directory.
    
    Args:
        path (str, optional): The directory path to list. Defaults to current directory (".").
        
    Returns:
        list: A list of dictionaries containing information about each item:
              - name: The name of the file/directory
              - type: Either "file" or "directory"
              - size: File size in bytes (for files only)
              - modified: Last modification timestamp
              
    Example:
        >>> contents = list_directory("/path/to/directory")
        >>> print(contents)
    """
    try:
        items = []
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            item_info = {
                "name": item,
                "type": "directory" if os.path.isdir(full_path) else "file",
                "modified": os.path.getmtime(full_path)
            }
            if item_info["type"] == "file":
                item_info["size"] = os.path.getsize(full_path)
            items.append(item_info)
        return items
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_current_directory() -> str:
    """Get the current working directory.
    
    Returns:
        str: The absolute path of the current working directory.
        
    Example:
        >>> current_dir = get_current_directory()
        >>> print(current_dir)
    """
    return os.getcwd()

@mcp.tool()
def change_directory(path: str) -> str:
    """Change the current working directory.
    
    Args:
        path (str): The directory path to change to.
        
    Returns:
        str: The new current working directory path.
        
    Raises:
        Exception: If the directory doesn't exist or is not accessible.
        
    Example:
        >>> new_dir = change_directory("/path/to/directory")
        >>> print(new_dir)
    """
    try:
        os.chdir(path)
        return os.getcwd()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def file_info(path: str) -> dict:
    """Get detailed information about a file or directory.
    
    Args:
        path (str): The path to the file or directory. Can be obtained from list_all_files()["files"][i]["path"].
        
    Returns:
        dict: A dictionary containing:
              - exists: Whether the path exists
              - type: "file" or "directory"
              - size: Size in bytes (for files)
              - created: Creation timestamp
              - modified: Last modification timestamp
              - accessed: Last access timestamp
              - absolute_path: Full absolute path
              
    Example:
        >>> # Get all files first
        >>> all_files = list_all_files()
        >>> # Get info for first file
        >>> info = file_info(all_files["files"][0]["path"])
        >>> print(info)
    """
    try:
        info = {
            "exists": os.path.exists(path),
            "absolute_path": os.path.abspath(path)
        }
        
        if info["exists"]:
            info.update({
                "type": "directory" if os.path.isdir(path) else "file",
                "created": os.path.getctime(path),
                "modified": os.path.getmtime(path),
                "accessed": os.path.getatime(path)
            })
            
            if info["type"] == "file":
                info["size"] = os.path.getsize(path)
                
        return info
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_directory(path: str) -> dict:
    """Create a new directory.
    
    Args:
        path (str): The path where the directory should be created.
        
    Returns:
        dict: A dictionary containing:
              - success: Boolean indicating if creation was successful
              - path: The created directory path
              - error: Error message if creation failed
              
    Example:
        >>> result = create_directory("/path/to/new/directory")
        >>> print(result)
    """
    try:
        os.makedirs(path, exist_ok=True)
        return {
            "success": True,
            "path": os.path.abspath(path)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def scrape_content(url):
    """Scrape content from a given URL and return it in markdown format.
    
    This tool uses Firecrawl to extract content from a webpage and convert it to markdown format.
    It's designed to handle various types of web content and convert them into a consistent markdown representation.
    
    Args:
        url (str): The URL of the webpage to scrape. Must be a valid HTTP/HTTPS URL.
        
    Returns:
        str: The scraped content in markdown format.
        
    Example:
        >>> content = scrape_content("https://example.com")
        >>> print(content)
        
    Raises:
        Exception: If the URL is invalid or if the scraping process fails.
    """
    headers = {"User-Agent": "Mozilla/5.0"}  # Bypass simple bot detection
    response = requests.get(url, headers=headers,timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove all <a> (links) and <script> tags
        for tag in soup(["a", "script", "style", "noscript"]):
            tag.decompose()

        # Extract clean text from <p> tags
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        
        return "\n".join(paragraphs)

    else:
        return f"Error: Unable to scrape. Status code {response.status_code}"

@mcp.tool()
def read_file_content(file_path: str, start_line: int = 1, end_line: int = None) -> dict:
    """Read and display the contents of a file with proper formatting.
    
    This tool reads a file and returns its contents with metadata. For text files,
    it can optionally return specific line ranges. For markdown files, it includes
    rendered content.
    
    Args:
        file_path (str): The path to the file to read. Can be obtained from list_all_files()["files"][i]["path"].
        start_line (int, optional): Starting line number to read. Defaults to 1.
        end_line (int, optional): Ending line number to read. If None, reads entire file.
        
    Returns:
        dict: A dictionary containing:
              - content: The file contents
              - rendered_content: Rendered markdown if applicable
              - metadata: File information (size, type, etc.)
              - error: Error message if reading fails
              
    Example:
        >>> # Get all files first
        >>> all_files = list_all_files()
        >>> # Read content of first file
        >>> result = read_file_content(all_files["files"][0]["path"])
        >>> print(result["content"])
    """
    try:
        # Get file information
        info = file_info(file_path)
        if not info["exists"]:
            return {"error": f"File not found: {file_path}"}
            
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as file:
            if end_line is None:
                content = file.read()
            else:
                lines = file.readlines()
                content = ''.join(lines[start_line-1:end_line])
        
        result = {
            "content": content,
            "metadata": info
        }
        
        # If it's a markdown file, add rendered content
        if file_path.lower().endswith(('.md', '.markdown')):
            result["rendered_content"] = render_markdown(content)
            
        return result
        
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}"}

@mcp.tool()
def preview_file(file_path: str, num_lines: int = 10) -> dict:
    """Preview the beginning of a file.
    
    This tool reads and displays the first few lines of a file, useful for
    quick file content inspection.
    
    Args:
        file_path (str): The path to the file to preview. Can be obtained from list_all_files()["files"][i]["path"].
        num_lines (int, optional): Number of lines to preview. Defaults to 10.
        
    Returns:
        dict: A dictionary containing:
              - preview: The first few lines of the file
              - total_lines: Total number of lines in the file
              - metadata: File information
              - error: Error message if reading fails
              
    Example:
        >>> # Get all files first
        >>> all_files = list_all_files()
        >>> # Preview first file
        >>> preview = preview_file(all_files["files"][0]["path"], num_lines=5)
        >>> print(preview["preview"])
    """
    try:
        # Get file information
        info = file_info(file_path)
        if not info["exists"]:
            return {"error": f"File not found: {file_path}"}
            
        # Read first few lines
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            preview = ''.join(lines[:num_lines])
            
        return {
            "preview": preview,
            "total_lines": len(lines),
            "metadata": info
        }
        
    except Exception as e:
        return {"error": f"Error previewing file: {str(e)}"}

@mcp.tool()
def list_all_files(path: str = ".", exclude_dirs: list = None) -> dict:
    """Recursively list all files in a directory and its subdirectories.
    
    This tool walks through all directories and subdirectories to find all files,
    with options to exclude specific directories and file types.
    
    Args:
        path (str, optional): The root directory to start from. Defaults to current directory (".").
        exclude_dirs (list, optional): List of directory names to exclude (e.g., ['node_modules', '.git']).
        
    Returns:
        dict: A dictionary containing:
              - files: List of dictionaries with file information:
                - path: Full path to the file
                - name: File name
                - size: File size in bytes
                - type: File type (extension)
                - modified: Last modification timestamp
              - total_files: Total number of files found
              - total_size: Total size of all files in bytes
              - error: Error message if operation fails
              
    Example:
        >>> result = list_all_files("/path/to/directory", exclude_dirs=['node_modules'])
        >>> print(result["files"])
    """
    try:
        if exclude_dirs is None:
            exclude_dirs = ['.git', 'node_modules', '__pycache__', '.venv', 'venv']
            
        files = []
        total_size = 0
        
        for root, dirs, files_in_dir in os.walk(path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files_in_dir:
                file_path = os.path.join(root, file)
                file_info = {
                    "path": file_path,
                    "name": file,
                    "size": os.path.getsize(file_path),
                    "type": os.path.splitext(file)[1],
                    "modified": os.path.getmtime(file_path)
                }
                files.append(file_info)
                total_size += file_info["size"]
        
        return {
            "files": files,
            "total_files": len(files),
            "total_size": total_size,
            "excluded_dirs": exclude_dirs
        }
        
    except Exception as e:
        return {"error": f"Error listing files: {str(e)}"}

@mcp.tool()
def find_files_by_type(path: str = ".", file_type: str = None) -> dict:
    """Find all files of a specific type in a directory and its subdirectories.
    
    Args:
        path (str, optional): The root directory to start from. Defaults to current directory (".").
        file_type (str, optional): The file extension to search for (e.g., '.py', '.js', '.md').
        
    Returns:
        dict: A dictionary containing:
              - files: List of matching files with their details
              - total_matches: Number of files found
              - file_type: The type of files searched for
              
    Example:
        >>> result = find_files_by_type("/path/to/directory", file_type=".py")
        >>> print(result["files"])
    """
    try:
        all_files = list_all_files(path)
        if "error" in all_files:
            return all_files
            
        if file_type:
            if not file_type.startswith('.'):
                file_type = '.' + file_type
                
            matching_files = [
                file for file in all_files["files"]
                if file["type"].lower() == file_type.lower()
            ]
        else:
            matching_files = all_files["files"]
            
        return {
            "files": matching_files,
            "total_matches": len(matching_files),
            "file_type": file_type
        }
        
    except Exception as e:
        return {"error": f"Error finding files: {str(e)}"}

if __name__ == "__main__":
    print("Starting MCP server...")
    print("MCP server is running.") 
    mcp.run(transport='stdio')  
