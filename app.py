from flask import Flask, request, render_template, jsonify, session, redirect, url_for,send_from_directory
from amazon_scrpr import Amazon_scrapper, login_Amazon, get_public_ip,Remove_File,Scraping_order
from selenium import webdriver
from selenium.webdriver.common.by import By
import time,requests,os
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['STATIC_FOLDER'] = 'static'
# Define the driver globally
driver = None

# Create a proxy object
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL

@app.route("/")
def hello_world():
    return render_template('index.html')

from flask import send_file

@app.route('/download-csv', methods=['GET'])
def download_csv():
    # path = '/home/jehrlich2/Flask_Amazon/order_data.csv'
    path = 'order_data.csv'
    return send_file(path, as_attachment=True)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session['logged_in'] = True
        session['user_name'] = email
        session['user_pass'] = password
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_name = session.get('user_name')
    user_pass = session.get('user_pass')
    return render_template('dashboard.html', user_name=user_name, user_pass=user_pass, status=True)


@app.route("/start_scraper", methods=['POST', 'GET'])
def start_scraper():
    
    if request.method == 'POST':
        Remove_File()
        
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        image_url = ''

        ShowImage = False  # Default value
        # Get_OTP = ''
        status = False
        
        # Initialize the driver if it's not already created

        global driver
        if driver is None:
            options = Options()
            # options.add_argument('--headless')  # Add this line to run headless
            options.add_argument(f'--proxy-server={get_public_ip()}')
            driver = webdriver.Firefox(options=options)
            
       
        try:
            data = login_Amazon(username=email, password_=password, driver=driver)
            wait = WebDriverWait(driver, 80)
           
            # __________________________________________________Download Capcha Image____________________________
            try:
                
                if driver.find_element(By.XPATH,"//img[@alt='captcha']"):
                    image_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//img[@src]")))
                    image_url = image_element.get_attribute("src")
                    response = requests.get(image_url)
                    print("_____________________+++__",str(image_url),"____________________+++___--__________________________________")
                    if response.status_code == 200:


                        session['captcha_image_url'] = image_url
              
                        file_extension = 'jpg'
                        static_img_dir = os.path.join(os.getcwd(), 'static', 'Img')
                        os.makedirs(static_img_dir, exist_ok=True)
                        file_path = os.path.join(static_img_dir, f'downloaded_image.{file_extension}')
                        with open(file_path, "wb") as image_file:
                        # with open("downloaded_image." + file_extension, "wb") as image_file:
                            image_file.write(response.content)
                        ShowImage = True
                        print("Image downloaded successfully.")
                        time.sleep(1)
                        # image_urls = url_for('static', filename='Img/downloaded_image.jpg')
                        image_urls = url_for('static', filename='Img/downloaded_image.jpg', _external=True)
                        return jsonify({"ShowImage": ShowImage, "image_url": image_urls, "message": "Data received successfully"})
                 
                    else:
                        print("Failed to download the image.")
                    
            except:
                pass
                # __________________________________________________Download Capcha Image End____________________________
            time.sleep(3)
            try:
                if driver.find_element(By.XPATH,"//span[contains(text(),'Solve this puzzle to protect your account')]"):
                    print("Capcha........................")
                    ShowImage = True
                    # return render_template('dashboard.html', ShowImage=ShowImage)
                    return jsonify({"ShowImage": ShowImage, "message": "Data received successfully"})
                
            except:
                pass
            try:
                if driver.find_element(By.XPATH,"//h4[contains(text(),'Enter the characters you see')]"):
                    print("yess captcha with password...................")
                    ShowImage = True
                    # return render_template('dashboard.html', ShowImage=ShowImage)
                    return jsonify({"ShowImage": ShowImage, "message": "Data received successfully"})
            except:
                pass

            
            try:
                print("try part...........")
                # This part for Indian Amazon account_________
                if driver.find_element(By.XPATH,"//span[text()='Enter verification code']"):
                    print("Going to otp...........................")
                    Get_OTP = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Enter verification code']")))
                    if Get_OTP:
                        status = True
                        ShowImage = False
                        print("otp true")
                        return jsonify({"status": status,"ShowImage":ShowImage, "message": "Data received successfully"})
            except:
                pass

            try:
                # This part for client Amazon account_________
                if driver.find_element(By.XPATH,"//*[@id='auth-mfa-otpcode']"):
                    print("Going to OTP section.......................")
                    Get_OTP = driver.find_element(By.XPATH,"//*[@id='auth-mfa-otpcode']")
                    if Get_OTP:
                        ShowImage = False
                        status = True
                        return jsonify({"status": status,"ShowImage":ShowImage, "message": "Data received successfully"})
            except:
                pass
            print("++++++++++++++++++++++++++++++++Working+++++++++++++++++++++++++++++++++++++++++++")
            
            try: 
                if driver.find_element(By.XPATH,"//h1[contains(text(),'Your Orders')]"):
                    print(".........................................................Start Scrapping........................................................")
                    time.sleep(3)
                    try:
                        if driver.find_element(By.XPATH,"//a[contains(text(), 'Next')]"):
                            print("Scrapping one page product............")
                            Amazon_scrapper(driver)
                    except:
                        pass
                    Scraping_order(driver)

                    
                    return jsonify({"message": "Scraping process initiated.","Order_Scrapped":True})
            except:
                pass

            
        
            try: 
                if driver.find_element(By.XPATH,"//h4[contains(text(),'There was a problem')]"):
                    ShowImage = False
                    return jsonify({"message": "Scraping process initiated."})
            except:
                pass

            return jsonify({"ShowImage": ShowImage, "image_url": image_url, "message": "Data received successfully"})

            # jsonify({"ShowImage": ShowImage, "message": "Data received successfully"})

        except Exception as e:
            print("______________________", e, "_______________________________")
            return jsonify({"status": False,"ShowImage": ShowImage, "message": "Data received successfully"})
        
   
        
    return jsonify({"status": False, "message": "Default response"})




@app.route("/submit_captcha", methods=['POST'])
def submit_captcha():
    if request.method == 'POST':
        Remove_File()
        data = request.get_json()
        captcha = data.get("captcha")
        password = data.get('UserPass')
        print("_____________________", captcha, "______________________",password)

        global driver
        if driver:

            try:
                if driver.find_element(By.XPATH,"//h1[contains(text(),'Your Orders')]"):
                    return jsonify({"message": "Captcha submitted successfully", "Correct_Captcha": True})
            except:
                pass

            try:
                wait = WebDriverWait(driver, 5)
                try:
                    if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))):
                        Fill_Password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
                        Fill_Password.send_keys(password)
                        

                        if WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='auth-captcha-guess']"))):
                            Fill_Capcha = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@id='auth-captcha-guess']")))
                            print(captcha,"__________",password)
                            Fill_Capcha.send_keys(captcha)
                            
                            SubmitBtn_click = driver.find_element(By.XPATH,"//input[@id='signInSubmit']").click()
                    else:
                        print("Going to else part__________________________________")

                except:
                    pass
                try:
                    time.sleep(1)
                    
                    if driver.find_element(By.XPATH,"//input[@name='cvf_captcha_input']"):
                        Fill_Capcha = driver.find_element(By.XPATH,"//input[@name='cvf_captcha_input']")
                        print(captcha,"++++++++++++",password)
                        Fill_Capcha.send_keys(captcha)

                        SubmitBtn_click = driver.find_element(By.XPATH,"//input[@name='cvf_captcha_captcha_action']").click()
                    else:
                        print("Going to else part__________________________________")
                except:
                    pass
                try: 
                    if driver.find_element(By.XPATH,"//h4[contains(text(),'There was a problem')]"):
                        wrong_captcha = True
                        
                        Fill_Password = driver.find_element(By.XPATH,"//input[@id='ap_password']")
                        time.sleep(1)
                        Fill_Password.send_keys(password)
                        SignIn_Click = driver.find_element(By.ID,"signInSubmit").click()
                        time.sleep(1)
                        print("There was a problem showing.......")
                 
                        # return jsonify({"message": "Scraping process initiated."})
                        return jsonify({"message": "Captcha submitted successfully", "wrong_captcha": wrong_captcha})
                    return jsonify({"message": "Captcha submitted successfully", "wrong_captcha": False})
              
                except:
                    pass

                try: 
                    if driver.find_element(By.XPATH,"//span[text()='Enter verification code']"):
                        print("Going to otp after Capcha solving...........................")
                        Get_OTP = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Enter verification code']")))
                        if Get_OTP:
                            status = True
                            ShowImage = False
                            print("otp true")
                            return jsonify({"status": status,"ShowImage":ShowImage, "message": "Data received successfully"})
                        return jsonify({"ShowImage": False, "message": "Captcha submitted successfully"})
                    else:
                        print("Going to else part__________________________________")
            
                except:
                    pass

                try:
                    if driver.find_element(By.XPATH,"//span[contains(text(),'Solve this puzzle to protect your account')]"):
                        print("Capcha on submit page........................")
                        wrong_captcha = True
                       
                        # return render_template('dashboard.html', ShowImage=ShowImage)
                        return jsonify({"message": "Captcha submitted successfully", "wrong_captcha": wrong_captcha})
                    return jsonify({"message": "Captcha submitted successfully", "wrong_captcha": False})
                    
                except:
                    pass
            
            except Exception as e:
                return jsonify({"error": str(e)})
 
    return jsonify({"error": "Invalid request"})




@app.route("/submit_otp", methods=['POST'])
def submit_otp():
    if request.method == 'POST':
        data = request.get_json()
        otp = data.get("otp")
        print("_____________________", otp, "______________________")

        global driver
        if driver:
            options = Options()
            # options.add_argument('--headless')  # Add this line to run headless
            options.add_argument(f'--proxy-server={get_public_ip()}')

            try:
                print("2134567865432456432456432145643245675432456754324532456543245643245")
                wait = WebDriverWait(driver, 5)
                try:
                    if wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='input-box-otp']"))):
                        Get_OTP = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='input-box-otp']")))
                        time.sleep(1)
                        Get_OTP.send_keys(otp)
                        Click_button = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='cvf-submit-otp-button']/span/input")))
                        Click_button.click()
                        time.sleep(2)
                        # If OTP submission was successful, call the Amazon_scrapper function
                        # Amazon_scrapper(driver)
                        # print("OTP submitted successfully","_____________")
                        
                        # if Get_OTP:
                        try:
                            if driver.find_element(By.XPATH,"//h1[contains(text(),'Your Orders')]"):
                                
                                Scraping_order(driver)
                                print("yessssssssssssssssssssssssssssssssssssssssssss")
                                return jsonify({"message": "Scraping process initiated.","status": True,"Scrap_Success":True})
                            
                                    
                                # If OTP submission was successful, call the Amazon_scrapper function
                                # Amazon_scrapper(driver)
                                # return jsonify({"message": "OTP submitted successfully", "status": True})
                            else:
                                return jsonify({"message": "Invalid OTP", "status": False})
                
                        except:
                            pass

                        try:
                            if driver.find_element(By.XPATH,"//a[contains(text(), 'Next')]"):
                                Scraping_order(driver)
                                Amazon_scrapper(driver)
                                print("Scrapping one page product............")
                                return jsonify({"message": "Scraping process initiated.","status": True,"Scrap_Success":True})
                                
                        except:
                            pass
 
                    return jsonify({"message": "OTP is not submitted","status":False})
                except:
                    pass

                try:
                    if wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='auth-mfa-otpcode']"))):
                        Get_OTP = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='auth-mfa-otpcode']")))
                        time.sleep(1)
                        Get_OTP.send_keys(otp)
                        checkbox_click = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='auth-mfa-remember-device']"))).click()
                        Click_button = wait.until(EC.presence_of_element_located((By.ID, "auth-signin-button"))).click()
                        time.sleep(2)
                        
                        # if Get_OTP:
                        if driver.find_element(By.XPATH,"//h1[contains(text(),'Your Orders')]"):
                            Amazon_scrapper(driver)
                            print("yessssssssssssssssssssssssssssssssssssssssssss")
                            return jsonify({"message": "Scraping process initiated.","status": True})
                        else:
                            return jsonify({"message": "Invalid OTP", "status": False})
 
                        # print("OTP submitted successfully","+++++++++++++++")
                        # # If OTP submission was successful, call the Amazon_scrapper function
                        # Amazon_scrapper(driv
                        
                        # return jsonify({"message": "OTP submitted successfully","status":status})
                    return jsonify({"message": "OTP submitted successfully","status":False})
                except:
                    pass

            except Exception as e:
                return jsonify({"message": str(e), "status": False})

    return jsonify({"message": "Invalid request", "status": False})


@app.route('/handle_invalid_captcha', methods=['GET'])
def handle_invalid_captcha():
    try:
        if driver.find_element(By.XPATH, "//img[@alt='captcha']"):
            image_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//img[@src]")))
            image_url = image_element.get_attribute("src")
            response = requests.get(image_url)
            if response.status_code == 200:

                file_extension = 'jpg'
                static_img_dir = os.path.join(os.getcwd(), 'static', 'Img')
                os.makedirs(static_img_dir, exist_ok=True)
                file_path = os.path.join(static_img_dir, f'downloaded_image2.{file_extension}')
                with open(file_path, "wb") as image_file:
                    image_file.write(response.content)
                ShowImage = True
                time.sleep(1)
                # image_urls_new = url_for('static', filename='Img/downloaded_image2.jpg')
                image_urls_new = url_for('static', filename='Img/downloaded_image2.jpg', _external=True)
                print("Image downloaded successfully using capcha time")
                return jsonify({"image_url": image_urls_new, "message": "Image processing complete", "wrong_captcha": False})
            else:
                return jsonify({"error": "Failed to download the image", "wrong_captcha": True})
    except Exception as e:
        return jsonify({"error": str(e), "wrong_captcha": True})

    return jsonify({"error": "Invalid request", "wrong_captcha": True})



@app.route('/')
def display_pagination():
    driver = None
    page_number = Amazon_scrapper(driver)
    return render_template('pagination.html', page_number=page_number)



script_file = "app.py"
script_process = None

@app.route('/stop_scraper', methods=['POST'])
def stop_scraper():
    global script_process, driver
    if driver:
        try:
            print("Driver Quit Inside of Script...")
            driver.close()
            driver.quit()  # Close the Selenium driver
            driver = None  # Set the driver to None to indicate it's stopped

            # Terminate the Selenium driver process
            if script_process is not None and script_process.poll() is None:
                script_process.terminate()
                script_process = None

            return jsonify({"stopped": True, "message": "Script stopped"})
        except Exception as e:
            return jsonify({"stopped": False, "error": str(e)})
    else:
        return jsonify({"stopped": True, "message": "No script process running"})



if __name__ == '__main__':
    app.run(debug=True)
