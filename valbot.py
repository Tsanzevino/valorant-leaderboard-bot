import logging.config
import discord
from discord.ext import commands
import discord.gateway
import configparser
import logging
import certifi
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver

# Initializing the config reader
config = configparser.ConfigParser()
config.read("leaderboard-bot.config")

# Initializing the logger
logging.basicConfig(filename = config['logging']['logFile'], level = config['logging']['logLevel'], filemode = config['logging']['logMode'], format = "%(asctime)s: %(levelname)s => %(message)s")

os.environ["SSL_CERT_FILE"] = certifi.where()

intents = discord.Intents.all()

client = commands.Bot(command_prefix = config['bot']['prefix'], intents=intents) 

@client.command()
async def scrape_patch_notes(ctx):
    logging.info("Received command request for Patch Notes")
    # Initialize Chrome WebDriver
    driver = webdriver.Chrome()

    # Navigate to the Valorant news page
    driver.get('https://playvalorant.com/en-us/news/game-updates/')
    
    # Wait for dynamic content to load
    driver.implicitly_wait(5)

    # Get the HTML content after the page is fully loaded
    html_content = driver.page_source

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Navigate to the most recent news article
    driver.get("https://playvalorant.com" + soup.find(find_content_card)['href'])
    
    # Wait for the new page to load
    driver.implicitly_wait(10)

    # Get the HTML content of the new page
    new_page_content = driver.page_source

    # Parse the new page HTML with BeautifulSoup
    new_page_soup = BeautifulSoup(new_page_content, 'html.parser')

    # Retrieve all text content from the div containing the article text
    div_in_href = new_page_soup.find(find_content_div)
    text_content = div_in_href.get_text()
    # Close the WebDriver
    driver.quit()

    chunks = [text_content[i:i + 2000] for i in range(0, len(text_content), 2000)]
    logging.info("Printing text: " + text_content)
    # Send each chunk as a separate message to the Discord channel
    for chunk in chunks:
        await ctx.send(chunk)
    

@client.event
async def on_ready():
    print(config['bot']['onReadyMessage'])
    logging.info(config['bot']['onReadyMessage'])

@client.command()
async def hello(ctx):
    logging.info('Command "hello" called')
    message = config['bot']['helloMessage']
    message = message.replace("<user>", ctx.author.display_name)
    logging.info("Sent Message: " + message)
    await ctx.send(message)

@client.command()
async def echo(ctx, *args):
    logging.info('Command "echo" called')
    message = ""
    for str in args:
        message = message + str + " "
    logging.info("Sent Message: " + message)
    await ctx.send(message)

@client.command()
async def boostego(ctx):
    logging.info('Command "boostego" called')
    message = "kill yourself."
    logging.info("Sent Message: " + message)
    await ctx.send(message)

@client.command()
async def patchnotes(ctx):
    logging.info('Command "patchnotes" called')
    await scrape_patch_notes(ctx.channel)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        message = config['bot']['unknownCommandMessage'] + "\n"
        if config['bot']['sendHelpOnUnknownCommand'] == "True":
            message = message + "Fake help message"
        logging.info("Sent Message: " + message)
        await ctx.send(message)
    else:
        logging.info("Command Error isn't CommandNotFound")
        raise error
    
def find_content_card(tag):
    return tag.has_attr('href') and str.__contains__(tag['href'], "patch")

def find_content_div(tag):
    if tag.has_attr('class'):
        for name in tag['class']:
            if str.__contains__(name, "NewsArticleContent-module--articleSectionWrapper"):
                return True
    return False

client.run(config['bot']['APIKey'])
logging.info("Exiting Bot")
