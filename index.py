import os
import argparse
from selenium_browserkit import BrowserManager, Node, By, Utility

from w_bybit import Auto as BybitAuto, Setup as BybitSetup
PROJECT_URL = "https://ferra.ag"

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        self.bybit_setup = BybitSetup(node=node, profile=profile)
        
        self.run()

    def run(self):
        self.bybit_setup.run()
        self.node.new_tab(f'{PROJECT_URL}/?code=sPMyMrGVn')

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get('profile_name')

        self.bybit_auto = BybitAuto(node=node, profile=profile)
        self.run()

    def handle_popup_terms(self)-> bool:
        if self.node.has_texts('Terms, Privacy & Conditions'):
            self.node.find_and_click(By.XPATH, '(//a[@href="/terms"]/../../../label)[1]/span[1]')
            self.node.find_and_click(By.XPATH, '(//a[@href="/terms"]/../../../label)[2]/span[1]')
            if self.node.find_and_click(By.XPATH, '//a[@href="/terms"]/../../../..//button[contains(normalize-space(.),"Accept") and not(@disabled)]'):
                self.node.log('✅ Đã đóng popup Terms')
                self.node.reload_tab()
                return True
        else:
            return True
        return False
    def handle_popup_news(self)-> bool:
        if self.node.find(By.XPATH, '//span[contains(normalize-space(.),"t show again")]', timeout=5):
            if self.node.find_and_click(By.XPATH, '//span[contains(normalize-space(.),"t show again")]/../../div[contains(@class, "cursor-pointer")]'):
                self.node.log('✅ Đã đóng popup News')
                return True
        else:
            return True

    def check_login(self) -> bool|None:
        if self.node.has_texts('Connect Wallet'):
            if self.node.find(By.XPATH, '(//button[contains(normalize-space(.),"Connect Wallet")])[1]'):
                self.node.log(f'⚠️ Cần Connect Wallet')
                return False
        else:
            for _ in range(2):
                # chạy lần 2 để kiểm tra trạng thái
                if self.node.find(By.CSS_SELECTOR, '[src="/images/tokens/sui.png"]'):
                    if not self.node.find(By.XPATH,'//p[contains(normalize-space(.),"please login to continue!")]', timeout=5):
                        self.node.log('✅ Connected thành công')
                        return True
                    else:
                        self.node.find_and_click(By.XPATH, '//p[contains(normalize-space(.),"please login to continue!")]/../button')
                        self.bybit_auto.confirm('Confirm')

        self.node.log('❌ Không xác định được Connect?')
        return None
    
    def active_connect(self):
        self.node.find_and_click(By.XPATH, '(//button[contains(normalize-space(.),"Connect Wallet")])[1]')
        self.node.find_and_click(By.XPATH, '//button//p[contains(normalize-space(.),"Bybit Wallet")]')
        return self.bybit_auto.confirm('Confirm')

    def login(self):
        is_login = self.check_login()
        if is_login == True:
            return True
        elif is_login == False:
            if self.active_connect():
                return self.check_login()
        elif is_login == None:
            return None

    def check_in(self):
        text = self.node.get_text(By.XPATH, '(//span[contains(text(),"Check-in")]/..//span)')

        if text == "Check-in":
            self.node.find_and_click(By.XPATH, '//span[contains(text(),"Check-in")]')
            self.node.find_and_click(By.XPATH, '//button[contains(text(),"Check-in")]')
            if self.node.find(By.XPATH, '//span[contains(text(),"Check-in")]/..//span[contains(text(),"✓")]'):
                self.node.log('✅ Check-in thành công')
                return True
        else:
            return False

    def task_post_feeds(self) -> bool|None:
        current_dir = os.path.dirname(os.path.abspath(__file__))   # thư mục chứa index.py
        picture_path = os.path.join(current_dir, "picture.png")
        if not os.path.exists(picture_path):
            self.node.log("❌ Không tìm thấy file:", picture_path)
            return False

        if self.node.find(By.XPATH, '(//span[contains(normalize-space(.),"tweet on your Feeds")]/../..)[not(contains(@class,"pointer-events-none"))]', timeout=15):
            # page 2
            self.node.new_tab(f'{PROJECT_URL}/profile')
            message = 'usbgameretro.com - Vao day choi game tuoi tho nhe'
            input_picture = self.node.find(By.XPATH, '//button[contains(text(),"Post")]/..//input[@type="file"]')
            try:
                input_picture.send_keys(picture_path)
            except Exception as e:
                return
                print(e)
            
            self.node.find_and_input(By.XPATH, '//textarea', message, delay=0)
            self.node.find_and_click(By.XPATH, '//button[contains(text(),"Post") and not(@disabled)]')
            self.node.close_tab()
            # page 1 
            self.node.switch_tab(f'{PROJECT_URL}')
            self.node.find_and_click(By.XPATH, '(//span[contains(normalize-space(.),"tweet on your Feeds")]/../..)[not(contains(@class,"pointer-events-none"))]')
            self.node.find_and_click(By.XPATH, '//button[contains(text(),"Check")]')
            if self.node.find(By.XPATH, '//span[contains(normalize-space(.),"tweet on your Feeds")]/../..//span[contains(text(),"✓")]'):
                self.node.log(f'✅ Task post feed thành công')
                return True

    def task_post_guild(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))   # thư mục chứa index.py
        picture_path = os.path.join(current_dir, "picture.png")
        if not os.path.exists(picture_path):
            self.node.log("❌ Không tìm thấy file:", picture_path)
            return False
        if self.node.find(By.XPATH, '(//span[contains(normalize-space(.),"tweet in your Guild")]/../..)[not(contains(@class,"pointer-events-none"))]', timeout=15):
            # page 2
            self.node.new_tab(f'{PROJECT_URL}/lp-guild')
            if self.node.find_and_click(By.XPATH, '//button//div[contains(normalize-space(.),"My Guild")]', timeout=10):
                pass
            else:
                number_guilds = self.node.finds(By.XPATH, '//tr')
                for i in range(2,len(number_guilds)):
                    el_member_guild = self.node.find(By.XPATH, f'((//tr)[{i}]//td)[last() - 1]')
                    name_guild = self.node.get_text(By.XPATH, f'((//tr)[{i}]//td)[3]')
                    type_guild = self.node.get_text(By.XPATH, f'((//tr)[{i}]//td)[5]')
                    if type_guild and type_guild.lower() != "public":
                        self.node.log(f'⚠️ Bỏ qua {name_guild} vì type {type_guild}')
                        continue
                    text_member = el_member_guild.text
                    if not text_member:
                        self.node.log(f"❌ Không tìm thấy dữ liệu thành viên trong hàng {name_guild}")
                        continue

                    text_member_parts = text_member.split('/')
                    if len(text_member_parts) != 2:
                        self.node.log("❌ Không đúng định dạng dạng số/số.")
                        continue
                    try:
                        clean_parts = [x.strip().replace(",", "").replace(".", "") for x in text_member_parts]
                        if int(clean_parts[0]) < int(clean_parts[1]):
                            self.node.scroll_to_element(el_member_guild)
                            if not self.node.click(el_member_guild):
                                self.node.log(f'❌ Không thể di chuyển đến guild hàng {name_guild}')
                                continue
                            self.node.find_and_click(By.XPATH, '//span[contains(text(), "Join Guild")]')
                            self.node.find_and_click(By.XPATH, '//button[contains(text(),"Confirm")]')
                            
                            if self.node.find(By.XPATH, '//button[contains(normalize-space(.),"Leave Guild")]'):
                                self.node.log(f'✅ Join Guild thành công')
                                break
                            else:
                                self.node.log(f'❌ Join Guild {name_guild} không thành công')
                                return
                        else:
                            self.node.log(f'⚠️ Join Guild {name_guild} đã đạt giới hạn')
                            continue
                    except Exception as e:
                        self.node.log(f'❌ Không thể convert sang int: {e}')
                        continue
            # page 2 post
            message = 'usbgameretro.com - Vao day choi game tuoi tho nhe'
            input_picture = self.node.find(By.XPATH, '//button[contains(text(),"Post")]/..//input[@type="file"]')
            try:
                input_picture.send_keys(picture_path)
            except Exception as e:
                self.node.log(f'❌ Khôgn thể gửi hình ảnh: {e}')
                return
            self.node.find_and_input(By.XPATH, '//textarea', message, delay=0)
            self.node.find_and_click(By.XPATH, '//button[contains(text(),"Post") and not(@disabled)]')
            self.node.close_tab()
            # page 1 
            self.node.switch_tab(f'{PROJECT_URL}')
            self.node.find_and_click(By.XPATH, '(//span[contains(normalize-space(.),"tweet in your Guild")]/../..)[not(contains(@class,"pointer-events-none"))]')
            self.node.find_and_click(By.XPATH, '//button[contains(text(),"Check")]')
            if self.node.find(By.XPATH, '//span[contains(normalize-space(.),"tweet in your Guild")]/../..//span[contains(text(),"✓")]'):
                self.node.log(f'✅ Task post feed thành công')
                return True
        else:
            self.node.log(f'❌ Task post guild bị block')
    def run(self):
        completed = []
        if not self.bybit_auto.run():
            return
        self.node.new_tab(f'{PROJECT_URL}/quests', method="get")
        self.handle_popup_terms()
        self.handle_popup_news()
        if not self.login():
            return
        if self.check_in():
            completed.append('check-in')
        if self.task_post_feeds():
            completed.append('post feed')
        if self.task_post_guild():
            completed.append('post guild')
        self.node.snapshot(completed)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto', action='store_true', help="Chạy ở chế độ tự động")
    parser.add_argument('--headless', action='store_true', help="Chạy trình duyệt ẩn")
    parser.add_argument('--disable-gpu', action='store_true', help="Tắt GPU")
    args = parser.parse_args()

    profiles = Utility.read_data('profile_name', 'pwd_wallet', 'seeds')
    max_profiles = Utility.read_config('MAX_PROFLIES')

    if not profiles:
        print("Không có dữ liệu để chạy")
        exit()

    browser_manager = BrowserManager(auto_handler=Auto, setup_handler=Setup)
    browser_manager.update_config(
                        headless=args.headless,
                        disable_gpu=args.disable_gpu,
                        use_tele=True
                    )
    browser_manager.add_extensions('Bybit-Wallet-*.crx')
    browser_manager.run_menu(
        profiles=profiles,
        max_concurrent_profiles=max_profiles,
        auto=args.auto
    )