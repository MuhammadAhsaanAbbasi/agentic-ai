from crewai_tools import (FileReadTool, ScrapeWebsiteTool, PDFSearchTool, SerperDevTool)

search_tool = SerperDevTool()
scrape_website_tool = ScrapeWebsiteTool()
read_file_tool = FileReadTool(file_paths=['./data/cv.pdf'])
semantic_search_resumme = PDFSearchTool(pdf='./data/cv.pdf')