
import asyncio
import csv
import difflib
from playwright.async_api import async_playwright

async def extract_visible_text(url):
    """Extract visible text content from a page (cleaned)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)
        text = await page.inner_text("body")
        await browser.close()

        # clean and deduplicate lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        unique_lines = []
        for line in lines:
            if line not in unique_lines:
                unique_lines.append(line)
        return unique_lines

def generate_clean_diff(text1, text2, output_csv="readable_diff.csv"):
    differ = difflib.Differ()
    diff = list(differ.compare(text1, text2))

    rows = []
    skip_next = False

    for i, line in enumerate(diff):
        if skip_next:
            skip_next = False
            continue

        if line.startswith("  "):  
            continue
        elif line.startswith("- "):
            # Look for a corresponding + line nearby
            if i + 1 < len(diff) and diff[i + 1].startswith("+ "):
                rows.append(["", line[2:], diff[i + 1][2:], " Modified"])
                skip_next = True
            else:
                rows.append(["", line[2:], "", " Removed"])
        elif line.startswith("+ "):
            rows.append(["", "", line[2:], " Added"])

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Section", "URL1 Text", "URL2 Text", "Difference"])
        writer.writerows(rows)

    print(f" Saved readable diff to {output_csv}")

async def main():
    url1 = "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/invoke_model.html"
    url2 = "https://boto3.amazonaws.com/v1/documentation/api/1.34.86/reference/services/bedrock-runtime/client/invoke_model.html"

    print("Extracting clean text from both URLs ...")
    text1 = await extract_visible_text(url1)
    text2 = await extract_visible_text(url2)

    print("Comparing content ...")
    generate_clean_diff(text1, text2)

if __name__ == "__main__":
    asyncio.run(main())


    
 
      


