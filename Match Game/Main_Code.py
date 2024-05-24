import pygame
import random
import os

class Husbu:
    def __init__(self):

        pygame.init()

        #kartu
        self.w_kartu = 110
        self.h_kartu = 110
        self.padding = 10

        self.row = 4
        self.col = 5

        #layar
        self.w_screen = 800
        self.h_screen = 650

        self.screen = pygame.display.set_mode((self.w_screen, self.h_screen))
        pygame.display.set_caption("Remember Your Husbu")

        #gambar buat kartu
        self.assets = "Assets"
        self.format_img = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
        self.image_filenames = [f for f in os.listdir(self.assets) if os.path.isfile(os.path.join(self.assets, f)) and os.path.splitext(f)[1].lower() in self.format_img]
        self.images = [pygame.image.load(os.path.join(self.assets, f)) for f in self.image_filenames]

        #tes eror kalo ga cukup gambarnya (harusnya cukup)
        if len(self.images) < (self.row * self.col) // 2:
            raise ValueError("Gambar husbunya kurang.")

        #duplikat kartu jadi dua
        self.cards = self.images[: (self.row * self.col) // 2] * 2
        random.shuffle(self.cards)

        #nengahin kartu
        self.w_rect_tengah = self.col * self.w_kartu + self.col * self.padding
        self.h_rect_tengah = self.row * self.h_kartu + self.row * self.padding
        self.offset_x = (self.w_screen - self.w_rect_tengah) // 2
        self.offset_y = (self.h_screen - self.h_rect_tengah) // 2

        #kosongan kartu (rect nya)
        self.card_rects = []
        for y in range(self.row):
            for x in range(self.col):
                rect_x = self.offset_x + x * (self.w_kartu + self.padding)
                rect_y = self.offset_y + y * (self.h_kartu + self.padding)
                self.card_rects.append(pygame.Rect(rect_x, rect_y, self.w_kartu, self.h_kartu))

        #import font
        self.font_path = os.path.join(self.assets, 'Nexa-Heavy.ttf')
        self.fbesar = pygame.font.Font(self.font_path, 68)
        self.fmed = pygame.font.Font(self.font_path, 45)
        self.fkecil = pygame.font.Font(self.font_path, 25)

        #state gamenya
        self.flipped = []
        self.matched = []
        self.waiting = False
        self.wait_time = 1000 
        self.start_ticks = 0
        self.start_time = 0  
        self.show_all_cards = False
        self.show_start_time = 0
        self.score = 0

        #state layarnya
        self.START = 0
        self.PLAYING = 1
        self.GAME_OVER = 2
        self.game_state = self.START

        #button akhiri game
        self.w_button_A = 200
        self.h_button_A = 50
        self.button_x = (self.w_screen - self.w_button_A) // 2
        self.button_y = self.offset_y + self.h_rect_tengah + self.padding

        self.run = True

    def round_edge(self, surface, radius):
        mask = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        rounded_image = surface.copy()
        rounded_image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return rounded_image

    def kartu(self):
        for i, rect in enumerate(self.card_rects):
            if i in self.flipped or i in self.matched:
                scaled_image = pygame.transform.scale(self.cards[i], (self.w_kartu, self.h_kartu))
                rounded_image = self.round_edge(scaled_image, 15)
                self.screen.blit(rounded_image, rect.topleft)
            else:
                pygame.draw.rect(self.screen, (79, 97, 112), rect, border_radius=15)

    def garis_besar(self, event):
        if self.game_state == self.START:
            self.show_all_cards = True
            self.show_start_time = pygame.time.get_ticks()
        elif self.game_state == self.GAME_OVER:
            self.restart()
        elif self.game_state == self.PLAYING and not self.waiting:
            if len(self.flipped) < 2:
                for i, rect in enumerate(self.card_rects):
                    if rect.collidepoint(event.pos) and i not in self.matched and i not in self.flipped:
                        self.flipped.append(i)
                        break

            #akhiri game
            if self.button_x <= event.pos[0] <= self.button_x + self.w_button_A and self.button_y <= event.pos[1] <= self.button_y + self.h_button_A:
                self.game_state = self.GAME_OVER

    def cek_match(self):
        if len(self.flipped) == 2 and not self.waiting:
            if self.cards[self.flipped[0]] == self.cards[self.flipped[1]]:
                self.matched.extend(self.flipped)
                self.flipped = []
                self.score += 10 
                #kalo match semua
                if len(self.matched) == len(self.card_rects):
                    self.game_state = self.GAME_OVER
            else:
                self.waiting = True
                self.start_ticks = pygame.time.get_ticks()

        if self.waiting:
            seconds = (pygame.time.get_ticks() - self.start_ticks)
            if seconds > self.wait_time:
                self.flipped = []
                self.waiting = False

    def time_left(self):
        waktu = pygame.time.get_ticks() - self.start_time
        if waktu > 60000:  #1 menit = 60.000
            self.game_state = self.GAME_OVER

        sisa_waktu = max(0, 60000 - waktu)
        teks_waktu = self.fmed.render(f"Time Left: {sisa_waktu // 1000}s", True, (245, 237, 229))
        self.screen.blit(teks_waktu, (20, 20))

    def button_akhiri(self):
        pygame.draw.rect(self.screen, (217, 74, 74), (self.button_x, self.button_y, self.w_button_A, self.h_button_A), border_radius=15)
        akhiri = self.fkecil.render("Akhiri Game", True, (245, 237, 229))
        akhiri_rect = akhiri.get_rect(center=(self.button_x + self.w_button_A // 2, self.button_y + self.h_button_A // 2))
        self.screen.blit(akhiri, akhiri_rect)

    def screen_mulai(self):
        if self.show_all_cards:
            for i, rect in enumerate(self.card_rects):
                scaled_image = pygame.transform.scale(self.cards[i], (self.w_kartu, self.h_kartu))
                rounded_image = self.round_edge(scaled_image, 15)
                self.screen.blit(rounded_image, rect.topleft)

            if pygame.time.get_ticks() - self.show_start_time >= 3000:  #3 detik
                self.game_state = self.PLAYING
                self.start_time = pygame.time.get_ticks()  # Update start_time ketika permainan dimulai
        else:
            welcome_text = self.fbesar.render("Remember Your Husbu", True, (245, 237, 229))
            welcome_text_rect = welcome_text.get_rect(center=(self.w_screen // 2, self.h_screen // 2 - 100))
            self.screen.blit(welcome_text, welcome_text_rect)

            text = self.fbesar.render("Lessgooooooo", True, (245, 237, 229))
            text_rect = text.get_rect(center=(self.w_screen // 2, self.h_screen // 2 + 100))
            self.screen.blit(text, text_rect)

            #ganti warna teks
            if text_rect.collidepoint(pygame.mouse.get_pos()):
                text = self.fbesar.render("Lessgooooooo", True, (217, 74, 74))
                self.screen.blit(text, text_rect)
       
    def screen_selesai(self):
        text1 = self.fbesar.render("Yeay Selesai!", True, (217, 74, 74))
        text1_rect = text1.get_rect(center=(self.w_screen // 2, self.h_screen // 2 - 100))
        self.screen.blit(text1, text1_rect)

        text2 = self.fbesar.render("Score: " + str(self.score), True, (245, 237, 229))
        text2_rect = text2.get_rect(center=(self.w_screen // 2, self.h_screen // 2))
        self.screen.blit(text2, text2_rect)

        restart_text = self.fbesar.render("Main Lagi?", True, (245, 237, 229))
        restart_rect = restart_text.get_rect(center=(self.w_screen // 2, self.h_screen // 2 + 100))
        self.screen.blit(restart_text, restart_rect)

        # Ganti warna teks
        if restart_rect.collidepoint(pygame.mouse.get_pos()):
            restart_text = self.fbesar.render("Main Lagi?", True, (100, 100, 100))
            self.screen.blit(restart_text, restart_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    self.restart()

    def bagan_score(self):
        score_text = self.fmed.render(f"Score: {self.score}", True, (245, 237, 229))
        score_text_rect = score_text.get_rect(topright=(self.w_screen - 20, 20))
        self.screen.blit(score_text, score_text_rect)

    def restart(self):
        self.flipped = []
        self.matched = []
        self.score = 0
        random.shuffle(self.cards)
        self.game_state = self.START
        self.show_all_cards = True
        self.show_start_time = pygame.time.get_ticks()

    def mulai(self):
        while self.run:
            self.screen.fill((54, 73, 88))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.garis_besar(event)

            if self.game_state == self.START:
                self.screen_mulai()
            elif self.game_state == self.PLAYING:
                self.kartu()
                self.cek_match()
                self.time_left()
                self.button_akhiri()
                self.bagan_score() 
            elif self.game_state == self.GAME_OVER:
                self.screen_selesai()

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Husbu()
    game.mulai()
