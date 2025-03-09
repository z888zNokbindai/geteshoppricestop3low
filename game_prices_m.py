import requests
from bs4 import BeautifulSoup
import sys
import time
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Function to read URLs from a .txt file
def read_urls_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            urls = [line.strip() for line in file.readlines() if line.strip()]
        return urls
    except IOError as e:
        print(f"Error reading the file {filename}: {e}")
        return []

# Headers to mimic a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_game_price_data(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
        
        # Raise an exception if the request was not successful
        response.raise_for_status()

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "lxml")

        # Extract game title
        title_tag = soup.find("h1", class_="mt8 lc3 lcm2")
        game_title = title_tag.text.strip() if title_tag else "Unknown Title"

        # Extract game image
        picture_tag = soup.find("picture", class_="game-hero-image")
        game_image_url = None

        if picture_tag:
            img_tag = picture_tag.find("img")
            if img_tag and img_tag.get("src"):
                game_image_url = img_tag["src"]

        # Find all table rows with the class 'pointer' (price data)
        rows = soup.find_all("tr", class_="pointer")

        # Initialize a list to store price data
        price_data = []

        # Iterate over the rows and extract country and price information
        for row in rows:
            country = row.find_all("td")[1].text.strip()
            price = row.find("td", class_="price-value").text.strip()
            price_data.append((country, price))

        # Sort the price data based on the price value
        price_data.sort(key=lambda x: float(x[1].replace('฿', '').replace(',', '')))

        # Get the top 3 prices
        top_3_prices = price_data[:3]

        # Return game title, image, and top 3 prices
        return game_title, game_image_url, top_3_prices, url
    
    except requests.exceptions.RequestException as e:
        print(f"Error during request to {url}: {e}")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
    
    return None, None, None, None

def generate_html():
    try:
        # Get the current time for the latest update
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create an HTML file to store the results
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="refresh" content="15">
            <title>Game Price Scraper</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; padding: 20px; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                .game-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; justify-content: center; padding: 0 10px; }}
                .game {{ background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .game h2 {{ font-size: 1.2em; color: #16a085; text-align: center; margin: 10px 0; }}
                .prices {{ margin-top: 10px; }}
                .price {{ margin: 5px 0; font-size: 1em; text-align: center; }}
                .price span {{ font-weight: bold; color: #e74c3c; }}
                .price-button {{ margin-top: 10px; text-align: center; }}
                .price-button a {{ padding: 10px 20px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; }}
                .price-button a:hover {{ background-color: #2980b9; }}
                img.game-image {{ display: block; margin: 0 auto; width: 100%; max-width: 240px; height: auto; }}
                .update-time {{ text-align: center; margin-top: 20px; font-size: 1.2em; color: #8e44ad; }}
                @media screen and (max-width: 1200px) {{
                    .game {{ padding: 15px; }}
                }}
                @media screen and (max-width: 800px) {{
                    .game h2 {{ font-size: 1.1em; }}
                    .price-button a {{ font-size: 0.9em; }}
                }}
            </style>
        </head>
        <body>
            <h1>Game Prices</h1>
            <div class="game-container">
        """

        # Read URLs from file (ensure it always reloads on each refresh)
        urls = read_urls_from_file("urls.txt")

        # Loop through each URL and extract data
        for url in urls:
            game_title, game_image_url, top_3_prices, game_url = get_game_price_data(url)

            if game_title and top_3_prices:
                html_content += f"<div class='game'>\n"
                
                if game_image_url:
                    html_content += f"<img class='game-image' src='{game_image_url}' alt='{game_title}'>\n"
                
                html_content += f"<h2>{game_title}</h2>\n"
                html_content += "<div class='prices'>\n"
                for rank, (country, price) in enumerate(top_3_prices, start=1):
                    html_content += f"<div class='price'>#{rank} {country}: <span>{price}</span></div>\n"
                html_content += "</div>\n"
                
                # Add a button to go to the URL
                html_content += f"<div class='price-button'><a href='{game_url}' target='_blank'>Go to Game Page</a></div>\n"
                
                html_content += "</div>\n"
            else:
                html_content += f"<div class='game'><h2>Could not fetch data for URL: {url}</h2></div>\n"

        html_content += f"</div>\n<div class='update-time'>Last Update: {current_time}</div></body></html>"

        # Write the HTML content to a file
        with open("game_prices.html", "w", encoding="utf-8") as file:
            file.write(html_content)

        print(f"HTML file has been created successfully: game_prices.html (Last Update: {current_time})")

    except IOError as e:
        print(f"Error writing to file: {e}")
    except Exception as e:
        print(f"Unexpected error occurred while generating HTML: {e}")

# Continuously regenerate HTML every 15 seconds
while True:
    generate_html()
    time.sleep(15)
