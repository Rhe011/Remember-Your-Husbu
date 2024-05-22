import pygame
import random
import os

class MemoryGame:
    def __init__(self):
        # Inisialisasi Pygame
        pygame.init()

        # Ukuran kartu dan padding
        self.CARD_WIDTH = 110
        self.CARD_HEIGHT = 110
        self.PADDING = 10

        # Ukuran grid
        self.ROWS = 4
        self.COLS = 5

        # Hitung ukuran layar berdasarkan grid dan padding
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 650

        # Inisialisasi layar
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Remember Your Husbu")

        # Load gambar kartu
        self.image_dir = "Assets"
        self.valid_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
        self.image_filenames = [f for f in os.listdir(self.image_dir) if os.path.isfile(os.path.join(self.image_dir, f)) and os.path.splitext(f)[1].lower() in self.valid_extensions]
        self.images = [pygame.image.load(os.path.join(self.image_dir, f)) for f in self.image_filenames]

        # Pastikan kita punya cukup gambar untuk grid
        if len(self.images) < (self.ROWS * self.COLS) // 2:
            raise ValueError("Tidak cukup gambar untuk membuat grid kartu yang sesuai.")

        # Duplikasi dan acak gambar
        self.cards = self.images[: (self.ROWS * self.COLS) // 2] * 2
        random.shuffle(self.cards)

        # Menghitung offset untuk memusatkan grid
        self.total_grid_width = self.COLS * self.CARD_WIDTH + (self.COLS - 1) * self.PADDING
        self.total_grid_height = self.ROWS * self.CARD_HEIGHT + (self.ROWS - 1) * self.PADDING
        self.offset_x = (self.SCREEN_WIDTH - self.total_grid_width) // 2
        self.offset_y = (self.SCREEN_HEIGHT - self.total_grid_height) // 2

        # Membuat rect untuk setiap kartu
        self.card_rects = []
        for y in range(self.ROWS):
            for x in range(self.COLS):
                rect_x = self.offset_x + x * (self.CARD_WIDTH + self.PADDING)
                rect_y = self.offset_y + y * (self.CARD_HEIGHT + self.PADDING)
                self.card_rects.append(pygame.Rect(rect_x, rect_y, self.CARD_WIDTH, self.CARD_HEIGHT))

        # Load custom font
        self.font_path = os.path.join(self.image_dir, 'Nexa-Heavy.ttf')
        self.font_large = pygame.font.Font(self.font_path, 68)
        self.font_medium = pygame.font.Font(self.font_path, 45)
        self.font_small = pygame.font.Font(self.font_path, 25)

        # State permainan
        self.flipped_cards = []
        self.matched_cards = []
        self.waiting = False
        self.wait_time = 1000  # Waktu tunggu dalam milidetik
        self.start_ticks = 0
        self.start_time = 0  # Tambahkan variabel start_time
        self.show_all_cards = False
        self.show_start_time = 0

        # State untuk layar utama dan game over
        self.START = 0
        self.PLAYING = 1
        self.GAME_OVER = 2
        self.game_state = self.START

        # Menghitung posisi tombol "Akhiri Game"
        self.button_width = 200
        self.button_height = 50
        self.button_x = (self.SCREEN_WIDTH - self.button_width) // 2
        self.button_y = self.offset_y + self.total_grid_height + self.PADDING

        # Loop utama
        self.run = True

    def create_rounded_mask(self, surface, radius):
        mask = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        rounded_image = surface.copy()
        rounded_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return rounded_image

    def draw_cards(self):
        for i, rect in enumerate(self.card_rects):
            if i in self.flipped_cards or i in self.matched_cards:
                scaled_image = pygame.transform.scale(self.cards[i], (self.CARD_WIDTH, self.CARD_HEIGHT))
                rounded_image = self.create_rounded_mask(scaled_image, 15)
                self.screen.blit(rounded_image, rect.topleft)
            else:
                pygame.draw.rect(self.screen, (79, 97, 112), rect, border_radius=15)

    def handle_mouse_event(self, event):
        if self.game_state == self.START:
            self.show_all_cards = True
            self.show_start_time = pygame.time.get_ticks()
        elif self.game_state == self.GAME_OVER:
            self.reset_game()
        elif self.game_state == self.PLAYING and not self.waiting:
            if len(self.flipped_cards) < 2:
                for i, rect in enumerate(self.card_rects):
                    if rect.collidepoint(event.pos) and i not in self.matched_cards and i not in self.flipped_cards:
                        self.flipped_cards.append(i)
                        break

            # Cek apakah tombol "Akhiri Game" diklik
            if self.button_x <= event.pos[0] <= self.button_x + self.button_width and self.button_y <= event.pos[1] <= self.button_y + self.button_height:
                self.game_state = self.GAME_OVER

    def check_for_match(self):
        if len(self.flipped_cards) == 2 and not self.waiting:
            if self.cards[self.flipped_cards[0]] == self.cards[self.flipped_cards[1]]:
                self.matched_cards.extend(self.flipped_cards)
                self.flipped_cards = []
                # Check if all cards are matched
                if len(self.matched_cards) == len(self.card_rects):
                    self.game_state = self.GAME_OVER
            else:
                self.waiting = True
                self.start_ticks = pygame.time.get_ticks()

        if self.waiting:
            seconds = (pygame.time.get_ticks() - self.start_ticks)
            if seconds > self.wait_time:
                self.flipped_cards = []
                self.waiting = False

    def display_timer(self):
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time > 60000:  # 1 menit = 60000 milidetik
            self.game_state = self.GAME_OVER

        # Display remaining time
        remaining_time = max(0, 60000 - elapsed_time)
        timer_text = self.font_medium.render(f"Time Left: {remaining_time // 1000}s", True, (245, 237, 229))
        self.screen.blit(timer_text, (20, 20))

    def draw_end_button(self):
        pygame.draw.rect(self.screen, (217, 74, 74), (self.button_x, self.button_y, self.button_width, self.button_height), border_radius=15)
        end_text = self.font_small.render("Akhiri Game", True, (245, 237, 229))
        end_text_rect = end_text.get_rect(center=(self.button_x + self.button_width // 2, self.button_y + self.button_height // 2))
        self.screen.blit(end_text, end_text_rect)

    def display_start_screen(self):
        if self.show_all_cards:
            for i, rect in enumerate(self.card_rects):
                scaled_image = pygame.transform.scale(self.cards[i], (self.CARD_WIDTH, self.CARD_HEIGHT))
                rounded_image = self.create_rounded_mask(scaled_image, 15)
                self.screen.blit(rounded_image, rect.topleft)

            if pygame.time.get_ticks() - self.show_start_time >= 3000:  # 3 detik
                self.game_state = self.PLAYING
                self.start_time = pygame.time.get_ticks()  # Update start_time ketika permainan dimulai
        else:
            welcome_text = self.font_large.render("Remember Your Husbu", True, (245, 237, 229))
            welcome_text_rect = welcome_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(welcome_text, welcome_text_rect)

            text = self.font_large.render("Lessgooooooo", True, (245, 237, 229))
            text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 100))
            self.screen.blit(text, text_rect)

            # Periksa apakah mouse mendekati teks
            if text_rect.collidepoint(pygame.mouse.get_pos()):
                text = self.font_large.render("Lessgooooooo", True, (217, 74, 74))  # Ubah warna teks saat mouse mendekat
                self.screen.blit(text, text_rect)

    def display_game_over_screen(self):
        text = self.font_large.render("Yeay Selesai!", True, (217, 74, 74))
        text_rect = text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(text, text_rect)

        subtext = self.font_large.render("Lagi?", True, (245, 237, 229))
        subtext_rect = subtext.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(subtext, subtext_rect)

        # Periksa apakah mouse mendekati teks "Click to Restart"
        if subtext_rect.collidepoint(pygame.mouse.get_pos()):
            subtext = self.font_large.render("Lagi?", True, (100, 100, 100))  # Ubah warna teks saat mouse mendekat
            self.screen.blit(subtext, subtext_rect)

    def reset_game(self):
        self.flipped_cards = []
        self.matched_cards = []
        random.shuffle(self.cards)
        self.game_state = self.START
        self.show_all_cards = True
        self.show_start_time = pygame.time.get_ticks()

    def run_game(self):
        while self.run:
            self.screen.fill((54, 73, 88))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_event(event)

            if self.game_state == self.START:
                self.display_start_screen()
            elif self.game_state == self.PLAYING:
                self.draw_cards()
                self.check_for_match()
                self.display_timer()
                self.draw_end_button()
            elif self.game_state == self.GAME_OVER:
                self.display_game_over_screen()

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = MemoryGame()
    game.run_game()
