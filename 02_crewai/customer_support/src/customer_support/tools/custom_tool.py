from crewai_tools import SerperDevTool, \
                         ScrapeWebsiteTool, \
                         WebsiteSearchTool

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

docs_scrape_tool = ScrapeWebsiteTool(
    website_url="https://docs.crewai.com/"
)