"""
上海海港足球俱乐部数据查询系统 - E2E自动化测试
测试目标：页面布局和数据验证
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    print("请先安装playwright: pip install playwright && npx playwright install")
    sys.exit(1)

BASE_URL = "http://localhost:5175/shanghaiport-fc-app/"
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PUBLIC_DATA_DIR = PROJECT_ROOT / "public" / "data"

class TestResult:
    def __init__(self):
        self.passed = []
        self.failed = []
    
    def add_pass(self, test_name: str, message: str = ""):
        self.passed.append({"name": test_name, "message": message})
        print(f"✅ PASS: {test_name}" + (f" - {message}" if message else ""))
    
    def add_fail(self, test_name: str, message: str = ""):
        self.failed.append({"name": test_name, "message": message})
        print(f"❌ FAIL: {test_name}" + (f" - {message}" if message else ""))
    
    def print_summary(self):
        total = len(self.passed) + len(self.failed)
        print("\n" + "=" * 60)
        print(f"测试总结: {len(self.passed)}/{total} 通过")
        print("=" * 60)
        if self.failed:
            print("\n失败的测试:")
            for f in self.failed:
                print(f"  - {f['name']}: {f['message']}")

class E2ETestRunner:
    def __init__(self):
        self.result = TestResult()
        self.browser = None
        self.page = None
    
    def setup(self, playwright):
        self.browser = playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_viewport_size({"width": 1280, "height": 720})
    
    def teardown(self):
        if self.browser:
            self.browser.close()
    
    def navigate_to_app(self):
        self.page.goto(BASE_URL, wait_until="networkidle")
        time.sleep(1)
    
    def test_page_layout(self):
        print("\n" + "=" * 60)
        print("测试组: 页面布局测试")
        print("=" * 60)
        
        self.page.set_viewport_size({"width": 1280, "height": 720})
        time.sleep(0.5)
        
        app_header = self.page.locator(".app-header")
        sidebar_header = self.page.locator(".sidebar-header")
        
        if app_header.count() == 0:
            self.result.add_fail("页面布局 - app-header存在", "app-header元素未找到")
            return
        if sidebar_header.count() == 0:
            self.result.add_fail("页面布局 - sidebar-header存在", "sidebar-header元素未找到")
            return
        
        self.result.add_pass("页面布局 - app-header存在")
        self.result.add_pass("页面布局 - sidebar-header存在")
        
        app_header_height = app_header.bounding_box()["height"]
        sidebar_header_height = sidebar_header.bounding_box()["height"]
        
        height_diff = abs(app_header_height - sidebar_header_height)
        if height_diff <= 2:
            self.result.add_pass("页面布局 - PC端header高度一致", 
                               f"app-header: {app_header_height}px, sidebar-header: {sidebar_header_height}px, 差异: {height_diff}px")
        else:
            self.result.add_fail("页面布局 - PC端header高度一致", 
                               f"app-header: {app_header_height}px, sidebar-header: {sidebar_header_height}px, 差异: {height_diff}px")
        
        self.page.set_viewport_size({"width": 375, "height": 667})
        time.sleep(0.5)
        
        app_header_height_mobile = app_header.bounding_box()["height"]
        sidebar_header_height_mobile = sidebar_header.bounding_box()["height"]
        
        height_diff_mobile = abs(app_header_height_mobile - sidebar_header_height_mobile)
        if height_diff_mobile <= 2:
            self.result.add_pass("页面布局 - 移动端header高度一致", 
                               f"app-header: {app_header_height_mobile}px, sidebar-header: {sidebar_header_height_mobile}px, 差异: {height_diff_mobile}px")
        else:
            self.result.add_fail("页面布局 - 移动端header高度一致", 
                               f"app-header: {app_header_height_mobile}px, sidebar-header: {sidebar_header_height_mobile}px, 差异: {height_diff_mobile}px")
        
        self.page.set_viewport_size({"width": 1280, "height": 720})
        time.sleep(0.5)
        
        sidebar = self.page.locator(".sidebar")
        toggle_btn = self.page.locator(".toggle-btn")
        
        if toggle_btn.count() > 0:
            toggle_btn.click()
            time.sleep(0.5)
            
            sidebar_class = sidebar.get_attribute("class")
            if "collapsed" in sidebar_class:
                self.result.add_pass("页面布局 - 侧边栏折叠功能", "侧边栏成功折叠")
            else:
                self.result.add_fail("页面布局 - 侧边栏折叠功能", "侧边栏未能折叠")
            
            toggle_btn.click()
            time.sleep(0.5)
        else:
            self.result.add_fail("页面布局 - 侧边栏折叠功能", "折叠按钮未找到")
    
    def test_navigation(self):
        print("\n" + "=" * 60)
        print("测试组: 导航功能测试")
        print("=" * 60)
        
        menu_items = [
            {"name": "球队信息", "selector": ".menu-item:has-text('球队信息')", "component": "Players"},
            {"name": "球队赛程", "selector": ".menu-item:has-text('球队赛程')", "component": "Schedule"},
            {"name": "历史赛季排名", "selector": ".menu-item:has-text('历史赛季排名')", "component": "Seasons"},
            {"name": "进球助攻榜", "selector": ".menu-item:has-text('进球助攻榜')", "component": "Statistics"},
            {"name": "历史比赛", "selector": ".menu-item:has-text('历史比赛')", "component": "History"},
        ]
        
        for item in menu_items:
            menu_item = self.page.locator(item["selector"])
            if menu_item.count() > 0:
                menu_item.click()
                time.sleep(0.5)
                
                card = self.page.locator(".card").first
                if card.count() > 0:
                    self.result.add_pass(f"导航 - {item['name']}", f"成功切换到{item['name']}组件")
                else:
                    self.result.add_fail(f"导航 - {item['name']}", "组件内容未加载")
            else:
                self.result.add_fail(f"导航 - {item['name']}", "菜单项未找到")
    
    def test_players_data(self):
        print("\n" + "=" * 60)
        print("测试组: 球员信息数据测试")
        print("=" * 60)
        
        players_menu = self.page.locator(".menu-item:has-text('球队信息')")
        if players_menu.count() > 0:
            players_menu.click()
            time.sleep(1)
        
        team_tabs = self.page.locator(".team-tab")
        if team_tabs.count() >= 2:
            self.result.add_pass("球员数据 - Tab切换", f"找到{team_tabs.count()}个Tab")
            
            first_team_tab = self.page.locator(".team-tab:has-text('一线队')")
            if first_team_tab.count() > 0:
                first_team_tab.click()
                time.sleep(0.5)
                
                try:
                    players_file = PUBLIC_DATA_DIR / "players.json"
                    if not players_file.exists():
                        players_file = DATA_DIR / "players.json"
                    with open(players_file, "r", encoding="utf-8") as f:
                        players_data = json.load(f)
                    
                    table_rows = self.page.locator(".card tbody tr")
                    row_count = table_rows.count()
                    
                    if row_count == len(players_data):
                        self.result.add_pass("球员数据 - 一线队数据行数", f"显示{row_count}行，数据文件有{len(players_data)}条")
                    else:
                        self.result.add_fail("球员数据 - 一线队数据行数", f"显示{row_count}行，但数据文件有{len(players_data)}条")
                except Exception as e:
                    self.result.add_fail("球员数据 - 一线队数据验证", str(e))
            
            b_team_tab = self.page.locator(".team-tab:has-text('B队')")
            if b_team_tab.count() > 0:
                b_team_tab.click()
                time.sleep(0.5)
                
                try:
                    players_b_file = PUBLIC_DATA_DIR / "players_b.json"
                    if not players_b_file.exists():
                        players_b_file = DATA_DIR / "players_b.json"
                    with open(players_b_file, "r", encoding="utf-8") as f:
                        players_b_data = json.load(f)
                    
                    table_rows = self.page.locator(".card tbody tr")
                    row_count = table_rows.count()
                    
                    if row_count == len(players_b_data):
                        self.result.add_pass("球员数据 - B队数据行数", f"显示{row_count}行，数据文件有{len(players_b_data)}条")
                    else:
                        self.result.add_fail("球员数据 - B队数据行数", f"显示{row_count}行，但数据文件有{len(players_b_data)}条")
                except Exception as e:
                    self.result.add_fail("球员数据 - B队数据验证", str(e))
        else:
            self.result.add_fail("球员数据 - Tab切换", "未找到Tab切换按钮")
        
        first_team_tab = self.page.locator(".team-tab:has-text('一线队')")
        if first_team_tab.count() > 0:
            first_team_tab.click()
            time.sleep(0.5)
        
        search_input = self.page.locator(".search-input").first
        if search_input.count() > 0:
            search_input.fill("颜骏凌")
            time.sleep(0.5)
            
            visible_rows = self.page.locator(".card tbody tr:visible")
            if visible_rows.count() >= 1:
                self.result.add_pass("球员数据 - 搜索功能", f"搜索'颜骏凌'显示{visible_rows.count()}行")
            else:
                self.result.add_fail("球员数据 - 搜索功能", "搜索无结果")
            
            search_input.fill("")
            time.sleep(0.5)
    
    def test_schedule_data(self):
        print("\n" + "=" * 60)
        print("测试组: 赛程数据测试")
        print("=" * 60)
        
        schedule_menu = self.page.locator(".menu-item:has-text('球队赛程')")
        if schedule_menu.count() > 0:
            schedule_menu.click()
            time.sleep(1)
        
        team_tabs = self.page.locator(".team-tab")
        if team_tabs.count() >= 2:
            first_team_tab = self.page.locator(".team-tab:has-text('一线队')")
            if first_team_tab.count() > 0:
                first_team_tab.click()
                time.sleep(0.5)
                
                try:
                    schedule_file = PUBLIC_DATA_DIR / "schedule.json"
                    if not schedule_file.exists():
                        schedule_file = DATA_DIR / "schedule.json"
                    with open(schedule_file, "r", encoding="utf-8") as f:
                        schedule_data = json.load(f)
                    
                    table_rows = self.page.locator(".card tbody tr")
                    row_count = table_rows.count()
                    
                    if row_count == len(schedule_data):
                        self.result.add_pass("赛程数据 - 一线队数据行数", f"显示{row_count}行，数据文件有{len(schedule_data)}条")
                    else:
                        self.result.add_fail("赛程数据 - 一线队数据行数", f"显示{row_count}行，但数据文件有{len(schedule_data)}条")
                except Exception as e:
                    self.result.add_fail("赛程数据 - 一线队数据验证", str(e))
            
            b_team_tab = self.page.locator(".team-tab:has-text('B队')")
            if b_team_tab.count() > 0:
                b_team_tab.click()
                time.sleep(0.5)
                
                try:
                    schedule_b_file = PUBLIC_DATA_DIR / "schedule_b.json"
                    if not schedule_b_file.exists():
                        schedule_b_file = DATA_DIR / "schedule_b.json"
                    with open(schedule_b_file, "r", encoding="utf-8") as f:
                        schedule_b_data = json.load(f)
                    
                    table_rows = self.page.locator(".card tbody tr")
                    row_count = table_rows.count()
                    
                    if row_count == len(schedule_b_data):
                        self.result.add_pass("赛程数据 - B队数据行数", f"显示{row_count}行，数据文件有{len(schedule_b_data)}条")
                    else:
                        self.result.add_fail("赛程数据 - B队数据行数", f"显示{row_count}行，但数据文件有{len(schedule_b_data)}条")
                except Exception as e:
                    self.result.add_fail("赛程数据 - B队数据验证", str(e))
        
        filter_buttons = self.page.locator(".filter-buttons button")
        if filter_buttons.count() >= 3:
            filter_buttons.nth(1).click()
            time.sleep(0.5)
            self.result.add_pass("赛程数据 - 状态筛选", "已结束筛选按钮可点击")
            
            filter_buttons.nth(0).click()
            time.sleep(0.5)
    
    def test_seasons_data(self):
        print("\n" + "=" * 60)
        print("测试组: 历史赛季排名数据测试")
        print("=" * 60)
        
        seasons_menu = self.page.locator(".menu-item:has-text('历史赛季排名')")
        if seasons_menu.count() > 0:
            seasons_menu.click()
            time.sleep(1)
        
        try:
            with open(DATA_DIR / "seasons.json", "r", encoding="utf-8") as f:
                seasons_data = json.load(f)
            
            table_rows = self.page.locator(".card tbody tr")
            row_count = table_rows.count()
            
            if row_count == len(seasons_data):
                self.result.add_pass("历史赛季排名 - 数据行数", f"显示{row_count}行，数据文件有{len(seasons_data)}条")
            else:
                self.result.add_fail("历史赛季排名 - 数据行数", f"显示{row_count}行，但数据文件有{len(seasons_data)}条")
        except Exception as e:
            self.result.add_fail("历史赛季排名 - 数据验证", str(e))
    
    def test_statistics_data(self):
        print("\n" + "=" * 60)
        print("测试组: 进球助攻榜数据测试")
        print("=" * 60)
        
        stats_menu = self.page.locator(".menu-item:has-text('进球助攻榜')")
        if stats_menu.count() > 0:
            stats_menu.click()
            time.sleep(1)
        
        try:
            with open(DATA_DIR / "goal_details.json", "r", encoding="utf-8") as f:
                goal_data = json.load(f)
            
            card_content = self.page.locator(".card-content")
            if card_content.count() > 0:
                self.result.add_pass("进球助攻榜 - 数据加载", "组件成功加载")
            else:
                self.result.add_fail("进球助攻榜 - 数据加载", "组件未加载")
        except Exception as e:
            self.result.add_fail("进球助攻榜 - 数据验证", str(e))
    
    def test_history_data(self):
        print("\n" + "=" * 60)
        print("测试组: 历史比赛数据测试")
        print("=" * 60)
        
        history_menu = self.page.locator(".menu-item:has-text('历史比赛')")
        if history_menu.count() > 0:
            history_menu.click()
            time.sleep(1)
        
        try:
            with open(DATA_DIR / "history_schedule.json", "r", encoding="utf-8") as f:
                history_data = json.load(f)
            
            card_content = self.page.locator(".card-content")
            if card_content.count() > 0:
                self.result.add_pass("历史比赛 - 数据加载", "组件成功加载")
            else:
                self.result.add_fail("历史比赛 - 数据加载", "组件未加载")
        except Exception as e:
            self.result.add_fail("历史比赛 - 数据验证", str(e))
    
    def test_responsive_design(self):
        print("\n" + "=" * 60)
        print("测试组: 响应式设计测试")
        print("=" * 60)
        
        viewports = [
            {"name": "桌面端 (1920x1080)", "width": 1920, "height": 1080},
            {"name": "笔记本 (1366x768)", "width": 1366, "height": 768},
            {"name": "平板 (768x1024)", "width": 768, "height": 1024},
            {"name": "手机 (375x667)", "width": 375, "height": 667},
        ]
        
        for viewport in viewports:
            self.page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
            time.sleep(0.5)
            
            sidebar = self.page.locator(".sidebar")
            main_content = self.page.locator(".main-content")
            
            if sidebar.count() > 0 and main_content.count() > 0:
                self.result.add_pass(f"响应式 - {viewport['name']}", "页面正常显示")
            else:
                self.result.add_fail(f"响应式 - {viewport['name']}", "页面元素缺失")
        
        self.page.set_viewport_size({"width": 1280, "height": 720})
        time.sleep(0.5)
    
    def test_header_height_and_title_responsive(self):
        print("\n" + "=" * 60)
        print("测试组: Header高度与标题响应式测试")
        print("=" * 60)
        
        test_widths = [1920, 1600, 1366, 1200, 1024, 900, 768, 600, 500, 400, 375]
        
        all_passed = True
        failed_widths = []
        
        for width in test_widths:
            self.page.set_viewport_size({"width": width, "height": 720})
            time.sleep(0.3)
            
            app_header = self.page.locator(".app-header")
            sidebar_header = self.page.locator(".sidebar-header")
            
            if app_header.count() == 0 or sidebar_header.count() == 0:
                self.result.add_fail(f"Header响应式 - {width}px宽度", "Header元素未找到")
                all_passed = False
                failed_widths.append(width)
                continue
            
            app_header_height = app_header.bounding_box()["height"]
            sidebar_header_height = sidebar_header.bounding_box()["height"]
            
            height_diff = abs(app_header_height - sidebar_header_height)
            
            h1_element = app_header.locator("h1")
            h2_element = app_header.locator("h2")
            
            h1_wrapped = False
            h2_wrapped = False
            
            if h1_element.count() > 0:
                h1_box = h1_element.bounding_box()
                if h1_box["height"] > 50:
                    h1_wrapped = True
            
            if h2_element.count() > 0:
                h2_box = h2_element.bounding_box()
                if h2_box["height"] > 30:
                    h2_wrapped = True
            
            issues = []
            if height_diff > 2:
                issues.append(f"高度差异{height_diff:.1f}px")
                all_passed = False
            if h1_wrapped:
                issues.append("h1标题换行")
                all_passed = False
            if h2_wrapped:
                issues.append("h2副标题换行")
                all_passed = False
            
            if issues:
                self.result.add_fail(f"Header响应式 - {width}px宽度", ", ".join(issues))
                failed_widths.append(width)
            else:
                self.result.add_pass(f"Header响应式 - {width}px宽度", 
                                   f"app-header: {app_header_height:.1f}px, sidebar-header: {sidebar_header_height:.1f}px")
        
        self.page.set_viewport_size({"width": 1280, "height": 720})
        time.sleep(0.5)
        
        return all_passed

    def run_all_tests(self):
        with sync_playwright() as playwright:
            self.setup(playwright)
            try:
                self.navigate_to_app()
                
                self.test_page_layout()
                self.test_navigation()
                self.test_players_data()
                self.test_schedule_data()
                self.test_seasons_data()
                self.test_statistics_data()
                self.test_history_data()
                self.test_responsive_design()
                self.test_header_height_and_title_responsive()
                
            finally:
                self.teardown()
        
        self.result.print_summary()
        return len(self.result.failed) == 0

if __name__ == "__main__":
    print("=" * 60)
    print("上海海港足球俱乐部数据查询系统 - E2E自动化测试")
    print("=" * 60)
    print(f"测试URL: {BASE_URL}")
    print(f"数据目录: {DATA_DIR}")
    print("=" * 60)
    
    runner = E2ETestRunner()
    success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)
