import base64
import json
from playwright.sync_api import sync_playwright, Page
from azure.communication.email import EmailClient

def take_screenshot(page: Page, url: str, filename: str):

    # Go to Clarity dashboard
    page.goto(url)
    page.wait_for_timeout(1000 * 10)
    
    # And take screenshot
    page.screenshot(path=filename)

def take_screenshots(config):

    with sync_playwright() as p:

        # Connect to existing chrome browser to use cached Google credentials
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        default_context = browser.contexts[0]
        page = default_context.new_page() # default_context.pages[0]

        # Navigate to URLs and save screenshot
        for p in config["Pages"]:
            take_screenshot(page, p["Url"], p["Filename"])

def get_base64_image(filename: str) -> str:

    with open(filename, "rb") as image_file:
        bytes = image_file.read()
        data_base64 = base64.b64encode(bytes)   # encode to base64 (bytes)
        data_base64 = data_base64.decode()      # convert bytes to string
        return data_base64

def send_screenshots(
        connection_string: str,
        sender_address: str,
        recipient_address: str):

    try:
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": sender_address,
            "recipients": {
                "to": [{"address": recipient_address}]
            },
            "content": {
                "subject": "Clarity Report",
                "plainText": "Clarity Report via email.",
                "html": """
				<html>
					<body>
						<h1>Clarity Report via email.</h1>
						<img src="cid:my_inline_image_1" alt="my_inline_image_1" />
						<img src="cid:my_inline_image_2" alt="my_inline_image_2" />
						<img src="cid:my_inline_image_3" alt="my_inline_image_3" />
						<img src="cid:my_inline_image_4 alt="my_inline_image_4" />
					</body>
				</html>"""
            },
            "attachments": [
			{
				"name": "my_inline_image_1",
				"contentId": "my_inline_image_1",
				"contentType": "image/png",
				"contentInBase64": get_base64_image("DrewRobsonConsulting.png")
			},
			{
				"name": "my_inline_image_2",
				"contentId": "my_inline_image_2",
				"contentType": "image/png",
				"contentInBase64": get_base64_image("DrewRobsonConsultingBlog.png")
			},
			{
				"name": "my_inline_image_3",
				"contentId": "my_inline_image_3",
				"contentType": "image/png",
				"contentInBase64": get_base64_image("pumldev.png")
			},
			{
				"name": "my_inline_image_4",
				"contentId": "my_inline_image_4",
				"contentType": "image/png",
				"contentInBase64": get_base64_image("Squareman.png")
			}]
        }

        poller = client.begin_send(message)
        result = poller.result()
        print("Message sent: ", result)

    except Exception as ex:
        print(ex)

with open('config.json') as f:
    config = json.load(f)

take_screenshots(config)
send_screenshots(
    config["Endpoint"],
    config["From"],
    config["To"])