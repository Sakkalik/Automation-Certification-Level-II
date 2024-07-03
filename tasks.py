from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
import shutil

from time import sleep

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    """Open website and close cookies window"""
    open_robot_order_website()
    close_annoying_modal()
    """Download csv, fill orders and make receipts"""
    get_orders()
    """Put all receipts into one ZIP file and delete individual files"""
    archive_receipts()
 



def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order/")

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def download_csv_file():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def fill_the_form(order):
    """Fills in the order data and click the 'Order' button"""
    page = browser.page()
    """Select head"""
    page.select_option("#head", index=int(order["Head"]))
    """Choose body"""
    if int(order["Body"]) == 1:
        page.click("#id-body-1")
    elif int(order["Body"]) == 2:
        page.click("#id-body-2")
    elif int(order["Body"]) == 3:
        page.click("#id-body-3")
    elif int(order["Body"]) == 4:
        page.click("#id-body-4")
    elif int(order["Body"]) == 5:
        page.click("#id-body-5")
    elif int(order["Body"]) == 6:
        page.click("#id-body-6")
    else:
        return "error body selection"
    """Fill leg number"""
    page.fill("input[placeholder='Enter the part number for the legs']", value=str(order["Legs"]))
    page.fill("#address", order["Address"])

    sleep(1)

    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            """Make receipt"""
            pdf_path = store_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = screenshot_robot(int(order["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)

            """Order another bot"""
            page.click("#order-another")
            close_annoying_modal()

            break
 

def get_orders():
    """Get orders from the csv file into a variable"""
    csvfile = Tables()
    orders = csvfile.read_table_from_csv("orders.csv", header=True)
    for row in orders:
        fill_the_form(row)

def store_receipt_as_pdf(order_number):
    """Export the receipt to a pdf file and return the file path"""
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf_path = "output/receipts/{0}.pdf".format(order_number)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    return pdf_path

def screenshot_robot(order_number):
    """Takes a screenshot of the robot"""
    page = browser.page()

    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator("#robot-preview-image").screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the robot screenshot to the receipt PDF file"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot, 
                                   source_path=pdf_file, 
                                   output_path=pdf_file)
    
def archive_receipts():
    """Archives all the receipt pdfs into a single zip archive"""
    zip = Archive()
    zip.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")


    
