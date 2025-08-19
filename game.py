import curses
import random
import time
from enum import Enum, auto

class Difficulty(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()

class AirplaneGame:
    def __init__(self):
        self.init_curses()
        self.init_colors()
        self.game_setup()

    def init_curses(self):
        self.scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.scr.keypad(True)
        self.scr.nodelay(True)
        self.rows, self.cols = self.scr.getmaxyx()
        self.rows -= 2  # Space for status bar
        self.cols -= 1

    def init_colors(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Player
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Food
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    # Enemies
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Status

    def game_setup(self):
        self.score = 0
        self.level = 1
        self.difficulty = Difficulty.EASY
        self.player = [self.rows//2, self.cols//2]
        self.foods = []
        self.enemies = []
        self.game_active = True
        self.target_fps = 60  # افزایش فریم‌ریت به 60 FPS
        self.last_frame_time = time.time()

    def show_menu(self, title, items, selected=0):
        self.scr.clear()
        self.scr.addstr(1, (self.cols - len(title))//2, title, curses.A_BOLD)
        
        for i, item in enumerate(items):
            y = self.rows//2 - len(items)//2 + i
            attr = curses.A_REVERSE if i == selected else curses.A_NORMAL
            self.scr.addstr(y, (self.cols - len(item))//2, item, attr)
        
        self.scr.refresh()

    def select_difficulty(self):
        options = [
            "EASY - Slow enemies, more food",
            "MEDIUM - Balanced challenge",
            "HARD - Fast enemies, less food"
        ]
        selected = 0
        
        while True:
            self.show_menu("SELECT DIFFICULTY", options, selected)
            
            try:
                key = self.scr.getkey()
                if key == 'KEY_UP' and selected > 0:
                    selected -= 1
                elif key == 'KEY_DOWN' and selected < 2:
                    selected += 1
                elif key in ('\n', '\r'):
                    self.difficulty = list(Difficulty)[selected]
                    # تنظیم سرعت بازی بر اساس سطح دشواری
                    self.target_fps = {
                        Difficulty.EASY: 45,
                        Difficulty.MEDIUM: 60, 
                        Difficulty.HARD: 75
                    }[self.difficulty]
                    break
            except:
                pass

    def show_instructions(self):
        info = {
            Difficulty.EASY: "Enemies: Slow | Food: Plenty",
            Difficulty.MEDIUM: "Enemies: Normal | Food: Normal",
            Difficulty.HARD: "Enemies: Fast | Food: Rare"
        }[self.difficulty]
        
        msg = [
            "CONTROLS:",
            "WASD - Move",
            "Q - Quit",
            "",
            "DIFFICULTY:",
            info,
            "",
            "Press any key to start"
        ]
        self.show_menu("AIRPLANE GAME", msg)
        self.scr.getch()

    def init_level(self):
        self.player = [self.rows//2, self.cols//2]
        
        # تنظیم تعداد المان‌ها بر اساس سطح دشواری
        food_count = {Difficulty.EASY: 8, Difficulty.MEDIUM: 5, Difficulty.HARD: 3}[self.difficulty]
        enemy_count = {Difficulty.EASY: 3, Difficulty.MEDIUM: 5, Difficulty.HARD: 7}[self.difficulty]
        
        # تولید موقعیت‌های تصادفی بدون تداخل
        positions = set([(self.player[0], self.player[1])])
        
        # ایجاد غذاها
        self.foods = []
        while len(self.foods) < food_count:
            pos = (random.randint(0, self.rows-1), random.randint(0, self.cols-1))
            if pos not in positions:
                self.foods.append(list(pos))
                positions.add(pos)
        
        # ایجاد دشمنان
        self.enemies = []
        while len(self.enemies) < enemy_count:
            pos = (random.randint(0, self.rows-1), random.randint(0, self.cols-1))
            if pos not in positions:
                self.enemies.append(list(pos))
                positions.add(pos)

    def draw(self):
        self.scr.erase()  # استفاده از erase به جای clear برای عملکرد بهتر
        
        # نوار وضعیت
        status = f"Score: {self.score} | Level: {self.level} | Mode: {self.difficulty.name}"
        self.scr.addstr(0, 0, status[:self.cols], curses.color_pair(4))
        
        # رسم بازیکن
        try:
            self.scr.addch(self.player[0]+1, self.player[1], 'A', curses.color_pair(1))
        except:
            pass
        
        # رسم غذاها
        for food in self.foods:
            try:
                self.scr.addch(food[0]+1, food[1], 'F', curses.color_pair(2))
            except:
                pass
        
        # رسم دشمنان
        for enemy in self.enemies:
            try:
                self.scr.addch(enemy[0]+1, enemy[1], 'E', curses.color_pair(3))
            except:
                pass
        
        self.scr.refresh()

    def handle_input(self):
        try:
            key = self.scr.getkey().lower()
            y, x = self.player
            
            if key == 'w' and y > 0: y -= 1
            elif key == 's' and y < self.rows-1: y += 1
            elif key == 'a' and x > 0: x -= 1
            elif key == 'd' and x < self.cols-1: x += 1
            elif key == 'q': 
                return False
            
            self.player = [y, x]
        except:
            pass
        
        return True

    def update(self):
        # بررسی جمع‌آوری غذا
        for food in self.foods[:]:
            if food == self.player:
                self.score += 10
                self.foods.remove(food)
                # اضافه کردن غذا جدید
                while True:
                    new_pos = [random.randint(0, self.rows-1), random.randint(0, self.cols-1)]
                    if new_pos != self.player and new_pos not in self.enemies:
                        self.foods.append(new_pos)
                        break
        
        # حرکت دشمنان
        chase_prob = {
            Difficulty.EASY: 0.4,
            Difficulty.MEDIUM: 0.6,
            Difficulty.HARD: 0.8
        }[self.difficulty]
        
        for enemy in self.enemies:
            if random.random() < chase_prob:
                # تعقیب بازیکن
                if enemy[0] < self.player[0]: enemy[0] += 1
                elif enemy[0] > self.player[0]: enemy[0] -= 1
                
                if enemy[1] < self.player[1]: enemy[1] += 1
                elif enemy[1] > self.player[1]: enemy[1] -= 1
            else:
                # حرکت تصادفی
                enemy[0] += random.choice([-1, 0, 1])
                enemy[1] += random.choice([-1, 0, 1])
            
            # محدودیت مرزها
            enemy[0] = max(0, min(self.rows-1, enemy[0]))
            enemy[1] = max(0, min(self.cols-1, enemy[1]))
            
            # بررسی برخورد
            if enemy == self.player:
                self.game_over()
                return False
        
        # ارتقاء سطح
        if self.score >= self.level * 100:
            self.level += 1
            self.init_level()
        
        return True

    def game_over(self):
        self.scr.clear()
        self.scr.addstr(self.rows//2, self.cols//2-5, "GAME OVER!", curses.A_BOLD)
        self.scr.addstr(self.rows//2+1, self.cols//2-8, f"Final Score: {self.score}")
        self.scr.addstr(self.rows//2+3, self.cols//2-10, "Press any key to exit")
        self.scr.refresh()
        self.scr.nodelay(False)
        self.scr.getch()
        self.game_active = False

    def run(self):
        self.select_difficulty()
        self.show_instructions()
        self.init_level()
        
        try:
            while self.game_active:
                frame_start = time.time()
                
                if not self.handle_input() or not self.update():
                    break
                
                self.draw()
                
                # کنترل فریم‌ریت دقیق
                frame_time = time.time() - frame_start
                target_time = 1.0 / self.target_fps
                sleep_time = target_time - frame_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    # اگر فریم طول کشید، یک پیام دیباگ نمایش دهید
                    self.scr.addstr(1, 0, f"Frame lag: {-sleep_time:.4f}s ", curses.A_DIM)
        finally:
            curses.endwin()

if __name__ == "__main__":
    AirplaneGame().run()