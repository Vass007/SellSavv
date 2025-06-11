import pandas as pd
import time
from selenium import webdriver
# from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor



def get_driver(url, check_element, n_tries, custom_function=None, driver=None, code=None):
    if driver is None:  # Check with existing driver
        print("Creating New driver..")
        chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    success = False
    n_try = 1
    for _ in range(n_tries):
        print(f"Attempt #{n_try}:")
        try:
            driver.get(url)
            time.sleep(3)
            driver.find_element(By.ID, check_element)

            # Run custom_function if provided
            if custom_function:
                driver = custom_function(driver,code)

            n_try += 1
            success = True
            print("Driver passed...")
            break
        except Exception as e:
            n_try += 1
            print(f"Driver failed: {e}")
            

    if success:
        return driver
    else:
        return None
    
def pincode_flow(driver,code):
    account_list_button = driver.find_element(By.ID, "nav-global-location-popover-link")
    account_list_button.click()
    time.sleep(3)

    pin_code_field = driver.find_element(By.ID, "GLUXZipUpdateInput")
    pin_code_field.send_keys(code)
    time.sleep(1)
    apply_button = driver.find_element(By.ID, "GLUXZipUpdate")
    apply_button.click()
    return driver

def amazon_pdp(asin, driver):
    get_driver(f"https://www.amazon.in/dp/{asin}", "buybox", 5, driver=driver)
    time.sleep(2)
    
    try:
        text = driver.find_element(By.ID, "corePriceDisplay_desktop_feature_div").text
        mrp = driver.find_element(By.CLASS_NAME, "a-price-whole").text
        sp = driver.find_element(By.CLASS_NAME, "basisPrice").text.split('\n')[1]
    except:
        mrp = sp = 'NA'
    
    availability = 'NA'
    
    # First attempt with availability-string
    try:
        avail = driver.find_element(By.ID, "availability-string").text.lower()
        if 'in stock' in avail or 'left in stock' in avail:
            availability = 'Yes'
        else:
            availability = 'No'
    except:
        pass
    
    # Second attempt with availability if first attempt failed or returned NA
    if availability == 'NA':
        try:
            avail = driver.find_element(By.ID, "availability").text.lower()
            if 'in stock' in avail or 'left in stock' in avail:
                availability = 'Yes'
            else:
                availability = 'No'
        except:
            availability = 'NA'
    
    return [mrp, sp, availability]

def deal_pdp(driver):
    
    try:
        deal_text = driver.find_element(By.CLASS_NAME, "dealBadgeSupportingText").text

    except:
        deal_text = ''
        
    if deal_text != '':
        return 'Yes'
    else:
        return 'No'

def title_n_pdp(driver):
    
    try:
        title_len = len(driver.find_element(By.ID, "productTitle").text)

    except:
        title_len = 'NA'
        
    return title_len

def title_pdp(driver):
    
    try:
        title = driver.find_element(By.ID, "productTitle").text

    except:
        title = 'NA'
        
    return title

def title_n_pdp(driver):
    
    try:
        title_len = len(driver.find_element(By.ID, "productTitle").text)

    except:
        title_len = 'NA'
        
    return title_len

def bullets_pdp(driver):
    try:
        # Try multiple possible selectors for bullet points
        bullet_containers = driver.find_elements(
            By.CSS_SELECTOR,
            "#feature-bullets ul.a-unordered-list.a-vertical.a-spacing-mini, #feature-bullets ul.a-unordered-list"
        )
        
        if not bullet_containers:
            return 'NA'
            
        # Get counts from all containers
        total_bullets = 0
        for container in bullet_containers:
            # Count bullet points using two different methods for validation
            bullets_by_li = len(container.find_elements(By.CSS_SELECTOR, "li.a-spacing-mini"))
            bullets_by_text = len([line for line in container.text.split('\n') 
                                 if line.strip() and 'About this item' not in line])
            
            # Use the larger count (sometimes li elements might be hidden)
            container_count = max(bullets_by_li, bullets_by_text)
            total_bullets += container_count
            
        # Validate the count is reasonable
        if total_bullets > 20 or total_bullets == 0:  # Unlikely to have more than 20 bullets
            return 'NA'
            
        return total_bullets
        
    except Exception as e:
        print(f"Error in bullets_pdp: {str(e)}")  # For debugging
        return 'NA'

def images_pdp(driver):
    
    try:
        images = len(driver.find_elements(By.CLASS_NAME, "imageThumbnail"))

    except:
        images = 'NA'
        
    return images

def videos_pdp(driver):
    
    try:
        videos = len(driver.find_elements(By.CLASS_NAME, "videoThumbnail"))

    except:
        videos = 'NA'
        
    return videos

def edd_pdp(driver):
    
    try:
        delivery_msg = driver.find_element(By.ID, "deliveryBlockMessage")
        delivery_date_str = delivery_msg.find_element(By.CLASS_NAME, "a-text-bold").text
        
        delivery_date = datetime.strptime(delivery_date_str, '%A, %d %B').replace(year=datetime.now().year)

        # Calculate the difference in days
        today = datetime.now()
        days_difference = (delivery_date - today).days
        

    except:
        days_difference = 'NA'
        
    return days_difference

def edd_fresh_pdp(driver):
    
    try:
        delivery_msg = driver.find_element(By.ID, "deliveryBlockAbbreviated_feature_div")
        delivery_date_str = delivery_msg.find_element(By.CLASS_NAME, "a-text-bold").text
        
        delivery_date = datetime.strptime(delivery_date_str, '%A, %d %B').replace(year=datetime.now().year)

        # Calculate the difference in days
        today = datetime.now()
        days_difference = (delivery_date - today).days
        

    except:
        days_difference = 'NA'
        
    return days_difference

def n_variants_pdp(driver):
    
    try:
        twister = driver.find_element(By.ID, "twister_feature_div")
        n_variants = len(twister.find_elements(By.CLASS_NAME, "a-button-text"))

    except:
        n_variants = 'NA'
        
    return n_variants

def star1_pdp(driver):
    
    try:
        hist = driver.find_element(By.ID, "histogramTable").text.split("\n")
        start = hist[-1]
        

    except:
        start = 'NA'
        
    return start

def star2_pdp(driver):
    
    try:
        hist = driver.find_element(By.ID, "histogramTable").text.split("\n")
        start = hist[-3]
        

    except:
        start = 'NA'
        
    return start

def star3_pdp(driver):
    
    try:
        hist = driver.find_element(By.ID, "histogramTable").text.split("\n")
        start = hist[-5]
        

    except:
        start = 'NA'
        
    return start

def ratings_n_pdp(driver):
    
    try:
        rr = driver.find_element(By.ID, "averageCustomerReviews").text.split("\n")
        ratings_n = rr[1]
        

    except:
        ratings_n = 'NA'
        
    return ratings_n

def rating_pdp(driver):
    
    try:
        rr = driver.find_element(By.ID, "averageCustomerReviews").text.split("\n")
        ratings = rr[0]
        

    except:
        ratings = 'NA'
        
    return ratings

def subcat_pdp(driver):
    try:
        # First try the original product details section
        try:
            prod_table = driver.find_element(By.ID, "productDetails_db_sections")
            bsr_pattern = r'#([\d,]+)'
            matches = re.findall(bsr_pattern, prod_table.text)
            if len(matches) >= 2:
                return f"#{matches[-1]}"
        except:
            pass

        # Try the alternative UI structure
        try:
            # Find the subcategory list within detail bullets
            subcategory = driver.find_element(
                By.CSS_SELECTOR, 
                "ul.a-unordered-list.a-nostyle.a-vertical.zg_hrsr"
            )
            
            # Extract the subcategory ranking
            subcat_text = subcategory.find_element(By.CSS_SELECTOR, "span.a-list-item").text
            subcat_match = re.search(r'#([\d,]+)', subcat_text)
            
            if subcat_match:
                return f"#{subcat_match.group(1)}"
            return ''
        except:
            pass

        return 'NA'
    except:
        return 'NA'

def cat_pdp(driver):
    try:
        # First try the original product details section
        try:
            prod_table = driver.find_element(By.ID, "productDetails_db_sections")
            bsr_pattern = r'#([\d,]+)'
            matches = re.findall(bsr_pattern, prod_table.text)
            if matches:
                return f"#{matches[0]}"
        except:
            pass

        # Try the alternative UI structure
        try:
            # Find all detail bullet lists
            detail_bullets = driver.find_elements(
                By.CSS_SELECTOR, 
                "ul.a-unordered-list.a-nostyle.a-vertical.a-spacing-none.detail-bullet-list"
            )
            
            # Look through each bullet list
            for bullet_list in detail_bullets:
                if "Best Sellers Rank:" in bullet_list.text:
                    # Extract the main category ranking
                    bsr_match = re.search(r'#([\d,]+)\s+in\s+[^(]+', bullet_list.text)
                    if bsr_match:
                        return f"#{bsr_match.group(1)}"
        except:
            pass
            
        return 'NA'
    except:
        return 'NA'

def seller_pdp(driver):
    try:
        fresh_text = driver.find_element(By.ID, "fresh-merchant-info").text.split("\n")[-1]
        if fresh_text != "":
            return fresh_text

    except:
        fresh_text = 'NA'
        
#     if fresh_text == 'NA':
#         fresh = 'NA'
#     elif fresh_text == '':
#         fresh = 'No'
#     else:
#         fresh = 'Yes'
    
    
    
    try:
        normal_text = driver.find_element(By.ID, "sellerProfileTriggerId").text
        if normal_text != "":
            return normal_text

    except:
        normal_text = 'NA'
        
#     if normal_text == 'NA':
#         normal = 'NA'
#     elif normal_text == '':
#         normal = 'No'
#     else:
#         normal = 'Yes'
    
    
#     if fresh == 'Yes' or normal == 'Yes':
#         return 'Yes'
#     elif fresh == 'No' or normal == 'No':
#         return 'No'
#     else:
#         return 'NA'
    return 'NA'
    
def prod_dscp_pdp(driver):
    
    try:
        prod_dscp_text = driver.find_element(By.ID, "productDescription_feature_div").text

    except:
        prod_dscp_text = 'NA'
        
    if prod_dscp_text == 'NA':
        return 'NA'
    elif prod_dscp_text == '':
        return 'No'
    else:
        return 'Yes'

def bybx_pdp(driver):
    print("\n=== Starting BXGY Detection ===")
    
    # Initialize variables
    vsx = 'NA'
    sopp = 'NA'
    
    # First pattern check (vsxoffers)
    try:
        print("\nChecking vsxoffers pattern...")
        vsx_text = driver.find_element(By.ID, "vsxoffers_feature_div").text
        print(f"VSX text found: {vsx_text}")
        
        try:
            bxgy_box = driver.find_element(By.ID, "itembox-Partner")
            offer_text = bxgy_box.find_element(
                By.CSS_SELECTOR,
                "span.a-truncate-cut"
            ).get_attribute("textContent").lower()
            print(f"Found offer text in box: {offer_text}")
            
            if any(keyword in offer_text for keyword in ["buy"]): 
                #and \
               #any(keyword in offer_text for keyword in ["off", "discount", "qualifying"]):
                print("VSX pattern matched keywords - setting to Yes")
                vsx = 'Yes'
            else:
                print("VSX pattern did not match keywords - setting to No")
                vsx = 'No'
        except:
            print("Could not find itembox-Partner, checking vsx_text")
            if vsx_text == '':
                print("VSX text is empty - setting to No")
                vsx = 'No'
            else:
                print("VSX text is not empty - setting to Yes")
                vsx = 'Yes'
    except:
        print("Could not find vsxoffers_feature_div")
        vsx_text = 'NA'
        vsx = 'NA'

    # Second pattern check (soppATF)
    try:
        print("\nChecking soppATF pattern...")
        sopp_div = driver.find_element(By.ID, "soppATF_feature_div")
        print(f"Found soppATF div with text: {sopp_div.text}")
        
        # Try to find expanded content
        try:
            expanded_content = sopp_div.find_element(
                By.CSS_SELECTOR,
                "div.a-expander-content[data-expanded='true']"
            )
            print("Found expanded content")
            
            # Look for Partner Offers and description
            try:
                offer_title = expanded_content.find_element(
                    By.CSS_SELECTOR,
                    "span.sopp-offer-title"
                ).text
                offer_desc = expanded_content.find_element(
                    By.CSS_SELECTOR,
                    "span.description"
                ).text
                print(f"Found offer title: {offer_title}")
                print(f"Found offer description: {offer_desc}")
                
                if ("Partner Offers" in offer_title and
                    any(keyword in offer_desc.lower() for keyword in
                        ["buy"])):
                    print("SOPP matches Partner Offers and keywords - setting to Yes")
                    sopp = 'Yes'
                else:
                    print("SOPP does not match required patterns - setting to No")
                    sopp = 'No'
            except:
                print("Could not find offer title/description, checking a-truncate-full")
                try:
                    full_text = expanded_content.find_element(
                        By.CSS_SELECTOR,
                        "span.a-truncate-full"
                    ).text
                    print(f"Found full text: {full_text}")
                    
                    if any(keyword in full_text.lower() for keyword in
                          ["buy"]):
                        print("Full text matches keywords - setting to Yes")
                        sopp = 'Yes'
                    else:
                        print("Full text does not match keywords - setting to No")
                        sopp = 'No'
                except:
                    print("Could not find a-truncate-full - setting to No")
                    sopp = 'No'
        except:
            print("Could not find expanded content, checking raw sopp text")
            sopp_text = sopp_div.text
            if sopp_text == '':
                print("SOPP text is empty - setting to No")
                sopp = 'No'
            else:
                if any(keyword in sopp_text.lower() for keyword in
                      ["buy"]):
                    print("SOPP text matches keywords - setting to Yes")
                    sopp = 'Yes'
                else:
                    print("SOPP text does not match keywords - setting to No")
                    sopp = 'No'
    except:
        print("Could not find soppATF_feature_div")
        sopp = 'NA'

    # Final decision logic
    print(f"\nFinal values - VSX: {vsx}, SOPP: {sopp}")
    if sopp == 'Yes' or vsx == 'Yes':
        print("Returning: Yes")
        return 'Yes'
    elif sopp == 'No' and vsx == 'No':
        print("Returning: No")
        return 'No'
    else:
        print("Returning: NA")
        return 'NA'

def aplus_pdp(driver):
    
    try:
        aplus_text = driver.find_element(By.ID, "aplus_feature_div").text

    except:
        aplus_text = 'NA'
        
    if aplus_text == 'NA':
        return 'NA'
    elif aplus_text == '':
        return 'No'
    else:
        return 'Yes'

def sns_pdp(driver):
    
    try:
        sns_text = driver.find_element(By.ID, "snsAccordionRowMiddle").text

    except:
        sns_text = 'NA'
        
    if sns_text == 'NA':
        return 'NA'
    elif sns_text == '':
        return 'No'
    else:
        return 'Yes'

def coupon_pdp(driver):
    
    try:
        coupon_text = driver.find_element(By.ID, "promoPriceBlockMessage_feature_div").text

    except:
        coupon_text = 'NA'
        
    if coupon_text == 'NA':
        return 'NA'
    elif coupon_text == '':
        return 'No'
    else:
        return 'Yes'

def n_sellers_pdp(driver):
    
    try:
        ingress = driver.find_element(By.ID, "dynamic-aod-ingress-box")
        ingress.find_element(By.CLASS_NAME, "a-link-normal").click()
        time.sleep(2)
        n_sellers = len(driver.find_elements(By.ID, "aod-offer-price"))

    except:
        n_sellers = 'NA'
        
    return n_sellers    

def scrape_amazon_data(asin, driver, pincode):
    """Scraper function to scrape Amazon PDP data for a given ASIN and pincode"""
    try:
        print(f"Scraping ASIN {asin} for pincode {pincode}")
        mrp, sp, availability = amazon_pdp(asin, driver)
        deal = deal_pdp(driver)
        title = title_pdp(driver)
        title_n = title_n_pdp(driver)
        bullets = bullets_pdp(driver)
        images = images_pdp(driver)
        videos = videos_pdp(driver)
        edd = edd_pdp(driver)
        edd_fresh = edd_fresh_pdp(driver)
        n_variants = n_variants_pdp(driver)
        star3 = star3_pdp(driver)
        star2 = star2_pdp(driver)
        star1 = star1_pdp(driver)
        ratings_n = ratings_n_pdp(driver)
        ratings = rating_pdp(driver)
        sub_cat = subcat_pdp(driver)
        cat = cat_pdp(driver)
        seller = seller_pdp(driver)
        desp = prod_dscp_pdp(driver)
        bybx = bybx_pdp(driver)
        aplus = aplus_pdp(driver)
        sns = sns_pdp(driver)
        coupon = coupon_pdp(driver)
        n_sellers = n_sellers_pdp(driver)

        return [asin, pincode, title_n, mrp, sp, availability, deal, title, bullets, images, videos,
                edd, edd_fresh, n_variants, star3, star2, star1, ratings_n, ratings, sub_cat, cat, seller, desp,
                bybx, aplus, sns, coupon, n_sellers]
    except Exception as e:
        print(f"Error scraping data for ASIN {asin}, pincode {pincode}: {e}")
        return None
    
def process_pin_code(pin_code, prod_ids):
    results = []
    try:
        driver = get_driver("https://www.amazon.in/","nav-global-location-popover-link",5, custom_function=pincode_flow, code=pin_code)
        time.sleep(2)
            
        for prod_id in prod_ids:
            product_result = scrape_amazon_data(prod_id,driver,pin_code)
            time.sleep(2)
            results.append(product_result)
    except Exception as e:
        print(f"Error processing pin code {pin_code}: {str(e)}")
    driver.quit()
    return results


def run_parallel(input_pin_prods):
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_pin_code, input_pin_prod, input_pin_prods[input_pin_prod]) for input_pin_prod in input_pin_prods]
        for future in futures:
            results.extend(future.result())
    df_results = pd.DataFrame(results, columns=["ASIN", "Pincode", "Title Length", "MRP", "Live Price", "Availability", 
                                  "Deal Tag", "Title", "Bullet Points", "Count of Catalog Images", 
                                  "Videos in Catalog", "EDD", "EDD_Fresh", "Number of Variations", "3 Star Ratings", 
                                  "2 Star Ratings", "1 Star Ratings", "Total Ratings", "Ratings", 
                                  "Sub-Category BSR", "Category BSR", "Sold By", "Description", 
                                  "BXGY", "A+", "SNS", "Coupon", "Number of Other Sellers"])
    return df_results


if __name__ == "__main__":
    df_category_asin = pd.read_excel("Dashboard Master.xlsx", sheet_name = "Oshea - Amazon")

    df_category_asin['Hygiene Tracking'].value_counts()

    # Filter rows where the 'Live' column is 'Live'
    df_live = df_category_asin[df_category_asin['Hygiene Tracking'] == 'Yes']

    # Get the list of ASINs from the filtered data (taking the first 20 as an example)
    asins = list(df_live['ASIN'])
    print(len(set(asins))) # Print the ASINs to verify


    pincodes = ["400013","600005","122102","700016","560068"]

    input_format = {}
    for pincode in pincodes:
        input_format[pincode] = list(set(asins))
    start_time = time.time()  # Capture the start time

    df_amazon_add = run_parallel(input_format)

    end_time = time.time()  # Capture the end time
    elapsed_time = end_time - start_time  # Calculate the total time in seconds
    print(f"Time taken for the loop: {elapsed_time / 60} minutes")