from selenium.webdriver.common.by import By
import time,requests
from selenium.webdriver.common.keys import Keys
import time, random,csv,os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

order_history_page = 'https://www.amazon.com/gp/css/order-history?ref_=nav_AccountFlyout_orders'
empty_dict = dict()
def Remove_File():
    folder_path = 'static/Img'
    files = os.listdir(folder_path)
    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

def login_Amazon(username, password_,driver):
    try:
        print("Login___________")
        driver.get(order_history_page)
        email = driver.find_element(By.ID, 'ap_email')
        email.send_keys(username)
        email.send_keys(Keys.ENTER)
        time.sleep(5)
        password = driver.find_element(By.ID, 'ap_password')
        password.send_keys(password_)
        password.send_keys(Keys.ENTER)
        random_sleep_duration = random.randint(5, 8)
        time.sleep(random_sleep_duration)
    except Exception as e:
        return {'data': e}

def get_public_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        if response.status_code == 200:
            data = response.json()
            public_ip = data.get('origin')
            return public_ip
        else:
            return "Failed to retrieve IP"
    except Exception as e:
        return str(e)




def Scraping_order(driver):
    Collect_All_Response = list()
    
    wait = WebDriverWait(driver, 5)
    try:
        Click_On_Track_package = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(),'Track package')]")))
        for click_btn in Click_On_Track_package:
            href_element = click_btn.get_attribute("href")
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(href_element)
            try:
                TrackNumber = str(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Tracking ID')]"))).text).split('Tracking ID:')[1]
                # print("Tracking Number = ", TrackNumber, "===========")
            except:
                TrackNumber = ''
            # 
            try:
                Tracking_Status = driver.find_element(By.CLASS_NAME,'pt-promise-main-slot').text
            except:
                Tracking_Status = ''
                # print("Tracking Status = ",Tracking_Status,"===========")
            try:
                Track_Location_daywise = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span/a[contains(text(),'See all updates')]"))).click()
                Tracking_Main_Container = driver.find_element(By.XPATH, "//div[@id='tracking-events-container']/div")
                Div_elements = Tracking_Main_Container.find_elements(By.TAG_NAME, 'div')
            except:
                pass
            Quanity=''
            try:
                if driver.find_element(By.CLASS_NAME,'images-quantity-label'):
                    Quanity = driver.find_element(By.CLASS_NAME,'images-quantity-label').text 
                
            except:
                Quanity = ''
            # print("Quantity: = ",Quanity)
            """
            for div in Div_elements:
                Store_All_Tracking_History_here = div.text
                print(Store_All_Tracking_History_here)

            close_button = driver.find_element(By.XPATH, "//button[@data-action='a-popover-close'][@aria-label='Close']")
            driver.execute_script("arguments[0].click();", close_button)
            """
            
            Order_Info = driver.find_element(By.XPATH,"//div/a[contains(text(), 'View order details')]")
            Order_Href = Order_Info.get_attribute('href')
            driver.get(Order_Href)

            try:
                Shipping_Address_Name = driver.find_element(By.CLASS_NAME,'displayAddressFullName').text
            except:
                Shipping_Address_Name = ''
            try:
                Shipping_Address_Street_1 = driver.find_element(By.CLASS_NAME,'displayAddressAddressLine1').text
            except:
                Shipping_Address_Street_1 = ''
            try:
                Shipping_Address_City_State_Zip_Code = driver.find_element(By.CLASS_NAME,'displayAddressCityStateOrRegionPostalCode').text
            except:
                Shipping_Address_City_State_Zip_Code = ''
            try:
                Country = driver.find_element(By.CLASS_NAME,'displayAddressCountryName').text
            except:
                Country = ''

            # print("Shipping Address Name:= ",Shipping_Address_Name)
            # print("Shipping Address Street 1:= ",Shipping_Address_Street_1)
            # print("Shipping Address City, State and Zip Code:= ",Shipping_Address_City_State_Zip_Code)
            # print("Country:= ",Country)
            try:
                Grand =  WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@class = 'a-color-base a-text-bold']")))
                for total in Grand:
                    Grand_Totals = total.text
                Grand_Total = Grand_Totals
                print("====================",Grand_Total,"===========================")
            except:
                Grand_Total = ''
            try:
                OrderDt_ID = str(driver.find_element(By.CLASS_NAME,"order-date-invoice-item").text)
            except:
                OrderDt_ID = ''
            try:
                OrderDate = OrderDt_ID.split('Ordered on')[1]
            except:
                OrderDate = ''
            try:
                OrderID = driver.find_element(By.XPATH,"//span[contains(text(),'Order#')]").text
            except:
                OrderID = ''

            print("Total Order =", Grand_Total, "===========")
            print("Order Date =", OrderDate, "===========")
            print("Order ID = ",OrderID,"===========")

            Collect_All_Response.append({"Tracking Number":TrackNumber,
                                        "Tracking Status":Tracking_Status,
                                        "Order ID":OrderID,
                                        "Order Date":OrderDate,
                                        "Order Total":Grand_Total,
                                        "Shipping Address Name":Shipping_Address_Name,
                                        "Street":Shipping_Address_Street_1,
                                        "City State Zip Code":Shipping_Address_City_State_Zip_Code,
                                        "Country":Country,
                                        "Quantity":Quanity,
                                        "Website":'Amazon.com'
                                        })
            print("\n\n\n\n")
            time.sleep(2)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        Write_Csv(Collect_All_Response) #Write Csv file
    except:
        pass
    finally:
        driver.quit()

def Write_Csv(Collect_All_Response):
    with open('order_data.csv', 'a', newline='') as csvfile:
        fieldnames = ['Tracking Number', 'Tracking Status', 'Order ID', 'Order Date', 'Order Total', 'Shipping Address Name','Street',
                        'City State Zip Code','Country', 'Quantity','Website']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for rec in Collect_All_Response:
                order_data = {
                    'Tracking Number': rec.get('Tracking Number', ''),
                    'Tracking Status': rec.get('Tracking Status', ''),
                    'Order ID': rec.get('Order ID', ''),
                    'Order Date': rec.get('Order Date', ''),
                    'Order Total': rec.get('Order Total', ''),
                    'Shipping Address Name': rec.get('Shipping Address Name', ''),
                    'Street': rec.get('Street', ''),
                    'City State Zip Code': rec.get('City State Zip Code', ''),
                    'Country': rec.get('Country', ''),
                    'Quantity': rec.get('Quantity', ''),
                    'Website': rec.get('Website', ''),

                    }

                writer.writerow(order_data)
        print("Data has been saved to order_data.csv")



def Amazon_scrapper(driver):

    current_page = 1
    Collect_All_Response = list()
    wait = WebDriverWait(driver, 5)
 
    print("Calling Amazon Scrapper function........................")

    try:
        Pagination = driver.find_element(By.CLASS_NAME, "a-pagination")
        Page_li = Pagination.find_elements(By.TAG_NAME, "li")
        for page in Page_li:
            page_number = str(page.text).split('page ')
            if 'Next→' not in page_number:
                data = page_number
        Page_Length = data[0]
        for page_v in range(int(Page_Length)):
            driver.find_element(By.XPATH,"//a[contains(text(), 'Next')]").click()
            print("Srapping all page......")
   
            try:
                Click_On_Track_package = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(),'Track package')]")))
                for click_btn in Click_On_Track_package:
                    href_element = click_btn.get_attribute("href")
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(href_element)
                    try:
                        TrackNumber = str(WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Tracking ID')]"))).text).split('Tracking ID:')[1]
                        # print("Tracking Number = ", TrackNumber, "===========")
                    except:
                        TrackNumber = ''
                    # 
                    try:
                        Tracking_Status = driver.find_element(By.CLASS_NAME,'pt-promise-main-slot').text
                    except:
                        Tracking_Status = ''
                        # print("Tracking Status = ",Tracking_Status,"===========")
                    try:
                        Track_Location_daywise = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span/a[contains(text(),'See all updates')]"))).click()
                        Tracking_Main_Container = driver.find_element(By.XPATH, "//div[@id='tracking-events-container']/div")
                        Div_elements = Tracking_Main_Container.find_elements(By.TAG_NAME, 'div')
                    except:
                        pass
                    Quanity=''
                    try:
                        if driver.find_element(By.CLASS_NAME,'images-quantity-label'):
                            Quanity = driver.find_element(By.CLASS_NAME,'images-quantity-label').text 
                        
                    except:
                        Quanity = ''
                    # print("Quantity: = ",Quanity)
                    """
                    for div in Div_elements:
                        Store_All_Tracking_History_here = div.text
                        print(Store_All_Tracking_History_here)

                    close_button = driver.find_element(By.XPATH, "//button[@data-action='a-popover-close'][@aria-label='Close']")
                    driver.execute_script("arguments[0].click();", close_button)
                    """
                    
                    Order_Info = driver.find_element(By.XPATH,"//div/a[contains(text(), 'View order details')]")
                    Order_Href = Order_Info.get_attribute('href')
                    driver.get(Order_Href)

                    try:
                        Shipping_Address_Name = driver.find_element(By.CLASS_NAME,'displayAddressFullName').text
                    except:
                        Shipping_Address_Name = ''
                    try:
                        Shipping_Address_Street_1 = driver.find_element(By.CLASS_NAME,'displayAddressAddressLine1').text
                    except:
                        Shipping_Address_Street_1 = ''
                    try:
                        Shipping_Address_City_State_Zip_Code = driver.find_element(By.CLASS_NAME,'displayAddressCityStateOrRegionPostalCode').text
                    except:
                        Shipping_Address_City_State_Zip_Code = ''
                    try:
                        Country = driver.find_element(By.CLASS_NAME,'displayAddressCountryName').text
                    except:
                        Country = ''

                    # print("Shipping Address Name:= ",Shipping_Address_Name)
                    # print("Shipping Address Street 1:= ",Shipping_Address_Street_1)
                    # print("Shipping Address City, State and Zip Code:= ",Shipping_Address_City_State_Zip_Code)
                    # print("Country:= ",Country)
                    
                    try:
                        Grand =  WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//span[@class = 'a-color-base a-text-bold']")))
                        for total in Grand:
                            Grand_Totals = total.text
                        Grand_Total = Grand_Totals
                        print("====================",Grand_Total,"===========================")
                    except:
                        Grand_Total = ''
                    try:
                        OrderDt_ID = str(driver.find_element(By.CLASS_NAME,"order-date-invoice-item").text)
                    except:
                        OrderDt_ID = ''
                    try:
                        OrderDate = OrderDt_ID.split('Ordered on')[1]
                    except:
                        OrderDate = ''
                    try:
                        OrderID = driver.find_element(By.XPATH,"//span[contains(text(),'Order#')]").text
                    except:
                        OrderID = ''

                    print("Total Order =", Grand_Total, "===========")
                    print("Order Date =", OrderDate, "===========")
                    print("Order ID = ",OrderID,"===========")

                    Collect_All_Response.append({"Tracking Number":TrackNumber,
                                                "Tracking Status":Tracking_Status,
                                                "Order ID":OrderID,
                                                "Order Date":OrderDate,
                                                "Order Total":Grand_Total,
                                                "Shipping Address Name":Shipping_Address_Name,
                                                "Street":Shipping_Address_Street_1,
                                                "City State Zip Code":Shipping_Address_City_State_Zip_Code,
                                                "Country":Country,
                                                "Quantity":Quanity,
                                                "Website":'Amazon.com'
                                                })
                    print("\n\n\n\n")
                    time.sleep(2)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

        
                Write_Csv(Collect_All_Response) #Write Csv file
            
            except:
                pass
            print("Counting===========",current_page,"============")
            empty_dict['current_page'] = current_page
            empty_dict['Page Length'] = Page_Length
            current_page +=1
            
            time.sleep(3)
    except Exception as e:
        print(f"Error: {str(e)}")
        return current_page

    finally:
        driver.quit()