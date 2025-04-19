import asyncio
from googlesearch import search
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Browser_automation")


@mcp.tool()
async def get_top_google_url(query, num_results=5):
    """Get top Google result URL using googlesearch."""
    print(f"[INFO] Searching Google for: {query}")
    urls = list(search(query, num_results=num_results))
    if not urls:
        print("[ERROR] No results found.")
        return None
    print(f"[INFO] Top result: {urls[0]}")
    return urls[0]


@mcp.tool()
async def browse_and_scrape(url, headless=False, width=1200, height=800):
    """Navigate to the URL and scrape content including code and text."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={'width': width, 'height': height},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)

        print(f"[INFO] Navigating to: {url}")
        await page.goto(url, timeout=60000)

        # Accept cookies if there's a consent button
        try:
            await page.locator("button:has-text('Accept'), button:has-text('I agree')").first.click(timeout=5000)
            print("[INFO] Accepted cookies.")
        except:
            print("[INFO] No cookie consent popup found.")

        # Determine website type and scrape accordingly
        if 'github.com' in url:
            print("[INFO] GitHub page detected. Scraping repository content.")
            content = await scrape_github(page)
        elif 'stackoverflow.com' in url:
            print("[INFO] Stack Overflow detected. Scraping question, answers, and code blocks.")
            content = await scrape_stackoverflow(page)
        elif 'docs.' in url or 'readthedocs' in url:
            print("[INFO] Documentation page detected. Scraping documentation content.")
            content = await scrape_documentation(page)
        else:
            print("[INFO] Generic page detected. Scraping paragraphs and code blocks.")
            content = await scrape_generic(page)

        # Dynamic file naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save content and screenshot
        await page.screenshot(path=f"final_page_{timestamp}.png")
        print(f"[INFO] Screenshot saved as 'final_page_{timestamp}.png'.")
        
        # Save scraped content
        with open(f"scraped_content_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[INFO] Scraped content saved to 'scraped_content_{timestamp}.txt'.")

        await browser.close()


@mcp.tool()
async def scrape_github(page):
    """Scrapes GitHub content like README and code blocks."""
    try:
        readme = await page.locator("article.markdown-body").inner_text()
    except Exception as e:
        print(f"[ERROR] Failed to scrape README: {e}")
        readme = "No README found."

    code_blocks = await page.locator("pre").all_inner_texts()
    return f"README Content:\n{readme}\n\nCode Blocks:\n" + "\n".join(code_blocks)


@mcp.tool()
async def scrape_stackoverflow(page):
    """Scrapes Stack Overflow question title, answers, comments, and code blocks."""
    try:
        question_title = await page.locator("h1").inner_text()
    except Exception as e:
        print(f"[ERROR] Failed to scrape question title: {e}")
        question_title = "No title found."
    
    try:
        answers = await page.locator("div.answer").all_inner_texts()
    except Exception as e:
        print(f"[ERROR] Failed to scrape answers: {e}")
        answers = []

    try:
        comments = await page.locator("div.comment").all_inner_texts()
    except Exception as e:
        print(f"[ERROR] Failed to scrape comments: {e}")
        comments = []
    
    code_blocks = await page.locator("pre, code").all_inner_texts()
    
    return f"Question Title: {question_title}\n\nAnswers:\n" + "\n".join(answers) + "\n\nComments:\n" + "\n".join(comments) + "\n\nCode Blocks:\n" + "\n".join(code_blocks)


@mcp.tool()
async def scrape_documentation(page):
    """Scrapes content from documentation pages, including code blocks."""
    try:
        doc_content = await page.locator("div.documentation").inner_text()  # Assuming docs are in <div class='documentation'>
    except Exception as e:
        print(f"[ERROR] Failed to scrape documentation: {e}")
        doc_content = "No documentation content found."
    
    code_blocks = await page.locator("pre").all_inner_texts()  # Scraping any code blocks
    return f"Documentation Content:\n{doc_content}\n\nCode Blocks:\n" + "\n".join(code_blocks)


@mcp.tool()
async def scrape_generic(page):
    """Scrapes generic <p> tags and code blocks from the page."""
    try:
        paragraphs = await page.locator("p").all()
        article_text = "\n\n".join([await p.inner_text() for p in paragraphs if await p.inner_text() != ""])
    except Exception as e:
        print(f"[ERROR] Failed to scrape paragraphs: {e}")
        article_text = "No paragraph content found."

    code_blocks = await page.locator("pre, code").all_inner_texts()  # Scraping code blocks from generic pages
    return article_text + "\n\nCode Blocks:\n" + "\n".join(code_blocks)


@mcp.tool()
async def main():
    query = input("Enter your query: ")
    top_url = await get_top_google_url(query)
    if top_url:
        await browse_and_scrape(top_url, headless=False)


if __name__ == "__main__":
    print("mcp server running : ")
    mcp.run(transport='stdio')
