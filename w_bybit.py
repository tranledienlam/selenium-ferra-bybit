import argparse
from selenium_browserkit import BrowserManager, Node, By, Utility

EXTENSION_URL = 'chrome-extension://pdliaogehgdbhbnmkklieghmmjkpigpa'

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        
        # self.run()

    def run(self):
        # Chuyển đến trang extension
        self.node.go_to(f'{EXTENSION_URL}/popup.html', 'get')

class Auto:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get('profile_name')
        self.pwd_wallet : str|None = profile.get('pwd_wallet')
        self.seeds : str|None = profile.get('seeds')
        self.node.wait = 2

        # self.run()

    def confirm(self, text: str = 'Cancel') -> bool:
        '''Text phải đúng Hoa/thường trong html'''
        done = False
        current_window = self.driver.current_window_handle

        # Chuyển sang tab chứa extension hoặc mở mới nếu chưa có
        if not self.node.switch_tab(f'{EXTENSION_URL}'):
            self.node.new_tab(f'{EXTENSION_URL}/popup.html')
        
        if text in self.node.has_texts(text):
            if self.node.find_and_click(By.XPATH, f'//button[contains(normalize-space(.),"{text}")]'):
                done = True
        
        self.driver.switch_to.window(current_window)
        return done

    def _check_unlocked(self) -> bool|None:
        self.node.find(By.XPATH, '//*[ @type="password" or contains(normalize-space(.), "Import Existing Wallet")]')
        texts = self.node.has_texts(['Unlock', 'Import Existing Wallet'])
        if 'Unlock' in texts:
            self.node.log(f'⚠️ Cần Unlock Bybit wallet')
            return True
        elif 'Import Existing Wallet' in texts:
            self.node.log(f'⚠️ Cần Import Bybit wallet')
            return False
        else:
            self.node.log(f'❌ Không xác định được unlock/Import?')
            return None

    def _active_unlock(self) -> bool: 
        if not self.pwd_wallet:
            self.node.log(f'❌ Không thể unlock ví: thiếu mật khẩu')
            return False

        if self.node.find_and_input(By.XPATH, '//input[@type="password"]', self.pwd_wallet, delay=0):
            if self.node.find_and_click(By.XPATH, '//button[not(@disabled)]'):
                return True
            else:
                self.node.log('❌ Không tìm thấy nút Unlock')
        else:
            self.node.log('❌ Không tìm thấy input mật khẩu để unlock')

        return False

    def _active_import(self) -> bool|None:
        if self.seeds:
            seeds_parts = self.seeds.split(' ')
            if len(seeds_parts) != 12:
                self.node.log(f'❌ Không thể import ví: thiếu {len(seeds_parts)}/12 seeds')
                return False
        else:
            self.node.log(f'❌ Không thể import ví: thiếu 12 seeds')
            return False
        if not self.pwd_wallet:
            self.node.log(f'❌ Không thể import ví: thiếu mật khẩu')
            return False

        if self.node.find_and_click(By.XPATH, '//span[contains(normalize-space(.),"Import Existing Wallet")]'):
            # page 1
            for i in range(2):
                self.node.find_and_input(By.XPATH, f'(//input[@type="password"])[{i+1}]', self.pwd_wallet, wait=0, delay=0)
            self.node.find_and_click(By.XPATH, '//input[@type="checkbox"]/../..')
            self.node.find_and_click(By.XPATH, '//button[not(@disabled)]')
            # page 2
            self.node.find_and_click(By.XPATH, '(//*[contains(normalize-space(.), "Import Wallet")])[last()]')
            # page 3
            for i in range(12):
                self.node.find_and_input(By.XPATH, f'(//input[@type="password"])[{i+1}]', seeds_parts[i], delay=0)
            if self.node.find_and_click(By.XPATH, '//button[contains(text(),"Import") and not(@disabled)]'):
                return self.node.wait_for_disappear(By.XPATH, '//button[@disabled]')
            return None
        else:
            self.node.log(f'❌ Không tìm thấy nút "Import Existing Wallet"')
            return False

    def _check_login(self) -> bool:
        if self.node.has_texts('Tokens'):
            self.node.log(f'✅ Login wallet thành công')
            return True
        else:
            self.node.log('❌ Không tìm thấy "Tokens" để xác định login thành công')
            return False

    def _login(self) -> bool|None:
        is_unlock = self._check_unlocked()
        if is_unlock == None:
            return None
        elif is_unlock == False:
            self._active_import()
        elif is_unlock == True:
            if not self._active_unlock():
                return False

        return self._check_login()
    
    def change_network(self, network_name: str, rpc_url: str, chain_id: str, symbol: str, block_explorer: str | None= None):
        pass
    
    def change_network_other(self, network_name):
        pass

    def run(self):
        # Chuyển đến trang extension
        self.node.go_to(f'{EXTENSION_URL}/popup.html')
        return self._login()


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
                        use_tele=False,
                        use_ai=False
                    )
    browser_manager.add_extensions('Bybit-Wallet-*.crx')
    browser_manager.run_menu(
        profiles=profiles,
        max_concurrent_profiles=max_profiles,
        auto=args.auto
    )