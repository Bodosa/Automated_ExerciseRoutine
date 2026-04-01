import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import os

ACCOUNT_EMAIL = "bodosa@test.com"
ACCOUNT_PASSWORD = "bodosa"
GYM_URL = "https://appbrewery.github.io/gym/"


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

driver = webdriver.Chrome(options=chrome_options)
driver.get(GYM_URL)

# wait instead of time.sleep()
wait = WebDriverWait(driver, 5)

# login button - wait
login_button = wait.until(ec.element_to_be_clickable((By.ID, "login-button")))
login_button.click()


# fill the email and password - wait
email_fill = wait.until(ec.presence_of_element_located((By.ID, "email-input")))
email_fill.clear()
email_fill.send_keys(ACCOUNT_EMAIL)


pass_fill = wait.until(ec.presence_of_element_located((By.ID, "password-input")))
pass_fill.clear()
pass_fill.send_keys(ACCOUNT_PASSWORD)

# login button
login_button = driver.find_element(By.ID, "submit-button")
login_button.click()

wait.until(ec.presence_of_element_located((By.ID, "schedule-page")))


# finding all class cards
class_cards = driver.find_elements(By.CSS_SELECTOR, "div[id^='class-card-']")
booked_classes = 0
waitlist_count = 0
already_booked = 0
processed_classes = []


for card in class_cards:
    # getting the day from parent day group
    day_group = card.find_element(By.XPATH, "./ancestor::div[contains(@id, 'day-group-')]")
    day_title = day_group.find_element(By.TAG_NAME, "h2").text

    # checking Wednesday or Thursday
    if "Wed" in day_title or "Thu" in day_title:
        # checking the 6pm class
        time_text = card.find_element(By.CSS_SELECTOR, "p[id^='class-time-']").text
        if "6:00 PM" in time_text:
            class_name = card.find_element(By.CSS_SELECTOR, "h3[id^='class-name-']").text
            btn_card = card.find_element(By.CSS_SELECTOR, "button[id^='book-button-']")

            # tracking the class details
            class_info = f"{day_title} on {class_name}"

            # check if it's available + incrementing the counter(s)
            if btn_card.text == "Booked":
                print(f"✓ Already booked: {class_info}")
                already_booked += 1
                processed_classes.append(f"[Booked] {class_info}")
            elif btn_card.text == "Waitlisted":
                print(f"✓ Already on waitlist: {class_info}")
                already_booked += 1
                processed_classes.append(f"[Waitlisted] {class_info}")
            elif btn_card.text == "Book Class":
                btn_card.click()
                print(f"✓ Successfully booked: {class_info}")
                booked_classes += 1
                processed_classes.append(f"[New Booking] {class_info}")
                time.sleep(1)
            elif btn_card.text == "Join Waitlist":
                btn_card.click()
                print(f"✓ Joined waitlist for: {class_info}")
                waitlist_count += 1
                processed_classes.append(f"[New Waitlist] {class_info}")
                time.sleep(1)
            break


# Verifying classes bookings on My Booking Page
total_booked = already_booked + booked_classes + waitlist_count
print(f"\n--- Total Tuesday/Thursday 6pm classes: {total_booked} ---")
print("\n--- VERIFYING ON MY BOOKINGS PAGE ---")

# click on bookings page
my_bookings = driver.find_element(By.ID, "my-bookings-link")
my_bookings.click()
wait.until(ec.presence_of_element_located((By.ID, "my-bookings-page")))

# counting all tuesday/thursday 6pm booked classes
verified_count = 0

all_cards = driver.find_elements(By.CSS_SELECTOR, "div[id*='card-']")

for card in all_cards:
    try:
        when_paragraph = card.find_element(By.XPATH, ".//p[strong[text()='When:']]")
        when_text = when_paragraph.text

        # checking if it's Thu or Tues class
        if ("Wed" in when_text or "Thu" in when_text) and "6:00 PM" in when_text:
            class_name = card.find_element(By.TAG_NAME, "h3").text
            print(f"  ✓ Verified: {class_name}")
            verified_count += 1
    except NoSuchElementException:
        pass


# comparison
print(f"\n--- VERIFICATION RESULT ---")
print(f"Expected: {total_booked} bookings")
print(f"Found: {verified_count} bookings")

if total_booked == verified_count:
    print("✅ SUCCESS: All bookings verified!")
else:
    print(f"❌ MISMATCH: Missing {total_booked - verified_count} bookings")






# print("\n--- BOOKING SUMMARY ---")
# print(f"Classes booked: {booked_classes}")
# print(f"Waitlists joined: {waitlist_count}")
# print(f"Already booked/waitlisted: {already_booked}")
# print(f"Total Saturday 6pm classes processed: {booked_classes + waitlist_count + already_booked}")
#
# print("\n--- DETAILED CLASS LIST ---")
# for class_detail in processed_classes:
#     print(f"  • {class_detail}")


