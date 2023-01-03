import asyncio
import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.sprite import RenderUpdates
from pygame.rect import Rect
from playsound import playsound
from enum import Enum
# import numpy as np
from render import *
from bots import *
pygame.init()
pygame.mixer.init()
font = pygame.font.SysFont("Tahoma", 20, 1)

# TITLE SCREEN LOGIC
def size_inc(n=4):
    if n < 12:
        return 'INCREASED'
def size_dec(n=4):
    if n > 2:
        return 'DECREASED'
def mode_change(mode):
    return 'CHANGED'
modes = {
    0: 'easy',
    1: 'medium',
    2: 'hard',
    3: 'multiplayer',    
}
ai_player = {x for x in modes.values() if x != 'multiplayer'}
BLACK = (0,0,0)
GREEN = (0, 156, 0)

class GameState(Enum):
    QUIT = -1
    TITLE = 0
    NEWGAME = 1
    HOWTOPLAY = 2

def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.

def create_surface_with_text(text, font_size, text_rgb, bg_rgb):
    font = pygame.font.SysFont("Tahoma", font_size, bold=True)
    surface = font.render(text, True, text_rgb, bg_rgb)
    return surface.convert_alpha()

class UIElement(Sprite):
    def __init__(self, center_position, text, font_size, bg_rgb, text_rgb, action=None):
        self.mouse_over = False
        default_image = create_surface_with_text(text=text, font_size=font_size, text_rgb=text_rgb, bg_rgb=bg_rgb)
        highlighted_image = create_surface_with_text(text=text, font_size=font_size * 2, text_rgb=text_rgb, bg_rgb=bg_rgb)
        self.images = [default_image, highlighted_image]
        self.rects = [
            default_image.get_rect(center=center_position),
            highlighted_image.get_rect(center=center_position)
        ]
        self.action = action
        super().__init__()

    @property
    def image(self):
        return self.images[1] if self.mouse_over else self.images[0]
    
    @property
    def rect(self):
        return self.rects[1] if self.mouse_over else self.rects[0]

    def update(self, mouse_pos, mouse_up):
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            if mouse_up:
                return self.action
        else:
            self.mouse_over = False
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
# Additional functionalities for game implementation
def change_texture(self, texture):
    # This function will change the texture of an object with matching dimensions, size, and rotation
    if texture == 'x' and not self.modded:
        for name in self.points:
            if 'cross' in name:
                self.visible.add(name)
        self.color = (255,0,0)
        self.thickness = 5
        self.modded = True
    elif texture == 'o' and not self.modded:
        self.visible.add('circle')
        self.color = (255,255,0)
        self.thickness = 5
        self.modded = True
    else:
        print("Tile already filled")

# Game class will represent a game state of 3d tic-tac-toe
class Game:
    board_map = {
        'x': 1,
        'o': -1,
    }

    def __init__(self, n = 4, difficulty= 'easy' ):
        self.n = n
        self.difficulty = difficulty 
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.prepared = False
        self.running = False
        self.sounds = {
            'move_tile': pygame.mixer.Sound("sounds/beep.ogg"),
            'claim_tile':  pygame.mixer.Sound("sounds/place.ogg"),
            'victory': pygame.mixer.Sound("sounds/win.ogg"),
            'title_music': pygame.mixer.Sound("sounds/title_music.ogg"),
            'loss': pygame.mixer.Sound("sounds/lose.ogg"),
        }
        pygame.init()
    
    def prepare_game(self):
        if not self.prepared:
            self.winning_lines = self.generate_winning_lines()
            self.visited = set()
            self.reset_ref = self.create_cube()
            self.visual = self.create_cube()
            self.moving = False
            self.turn = 0
            self.prev = 0,0
            self.won = False, 0
            self.board = [[[0 for _ in range(self.n)] for __ in range(self.n)] for ___ in range(self.n)]
            self.tie = False
            self.curr_highlight = 0
            self.prepared = True
    def add_o(self, obj):
        obj.points['circle'] = [
            obj.points['ref_front_center'][0].copy(),
            obj.points['ref_right_center'][0].copy(),
            obj.points['ref_back_center'][0].copy(),
            obj.points['ref_left_center'][0].copy(),
            obj.points['ref_front_center'][0].copy(),
            obj.points['ref_top_center'][0].copy(),
            obj.points['ref_back_center'][0].copy(),
            obj.points['ref_bottom_center'][0].copy(),
            obj.points['ref_front_center'][0].copy(),
            obj.points['ref_top_center'][0].copy(),
            obj.points['ref_left_center'][0].copy(),
            obj.points['ref_bottom_center'][0].copy(),
            obj.points['ref_right_center'][0].copy(),
            obj.points['ref_top_center'][0].copy(),
            obj.points['ref_front_center'][0].copy(),
        ]
    
    def add_x(self, obj):
        obj.points['cross_0'] = [ obj.points["ABCDAEFGHE"][0].copy(), obj.points["ABCDAEFGHE"][-3].copy() ]
        obj.points['cross_1'] = [ obj.points["ABCDAEFGHE"][1].copy(), obj.points["ABCDAEFGHE"][-2].copy() ]
        obj.points['cross_2'] = [ obj.points["ABCDAEFGHE"][5].copy(), obj.points["ABCDAEFGHE"][2].copy()  ]
        obj.points['cross_3'] = [ obj.points["ABCDAEFGHE"][3].copy(), obj.points["ABCDAEFGHE"][6].copy()  ]

    def create_cube(self):
        cube_visual = []
        if self.n % 2 == 1:
            for i in range(-self.n//2 + 1, self.n//2 + 1):
                for j in range(-self.n//2 + 1, self.n//2 + 1):
                    for k in range(-self.n//2 + 1, self.n//2 + 1):
                        temp = Object3D("objects_3d/cube.txt")
                        self.add_x(temp)
                        self.add_o(temp)
                        temp.color = GREEN
                        temp.update(4*i,4*j,4*k,0,0,0,0.5)
                        cube_visual.append(temp)
        else:
            for i in range(-self.n//2 + 1, self.n//2 + 1):
                for j in range(-self.n//2 + 1, self.n//2 + 1):
                    for k in range(-self.n//2 + 1, self.n//2 + 1):
                        temp = Object3D("objects_3d/cube.txt")
                        self.add_x(temp)
                        self.add_o(temp)
                        temp.color = GREEN
                        temp.update(-2 + 4*i,-2 + 4*j,-2 + 4*k,0,0,0,0.5)
                        cube_visual.append(temp)
        return cube_visual
    
    def reset_cube_position(self):
        for obj, ref_obj in zip(self.visual, self.reset_ref):
            for name in obj.points:
                section, ref_section = obj.points[name], ref_obj.points[name]
                for p, ref_p in zip(section, ref_section):
                    p.x = ref_p.x
                    p.y = ref_p.y
                    p.z = ref_p.z
                    p.update()

    def generate_winning_lines(self):
        winning_lines = set()
        
        # Add lines in xy plane
        winning_lines |= {tuple([(x, y, z) for y in range(self.n)]) for x in range(self.n) for z in range(self.n)}
        
        # Add lines in yz plane
        winning_lines |= {tuple([(x, y, z) for y in range(self.n)]) for z in range(self.n) for x in range(self.n)}
        
        # Add lines in zx plane
        winning_lines |= {tuple([(x, y, z) for x in range(self.n)]) for z in range(self.n) for y in range(self.n)}
        
        # Add lines in x direction
        winning_lines |= {tuple([(x, y, z) for x in range(self.n)]) for y in range(self.n) for z in range(self.n)}
        
        # Add lines in z direction
        winning_lines |= {tuple([(x, y, z) for z in range(self.n)]) for x in range(self.n) for y in range(self.n)}
        
        # Add diagonal lines
        winning_lines |= {tuple([(x, x, x) for x in range(self.n)])}
        winning_lines |= {tuple([(x, x, self.n-1-x) for x in range(self.n)])}
        winning_lines |= {tuple([(x, self.n-1-x, x) for x in range(self.n)])}
        winning_lines |= {tuple([(x, self.n-1-x, self.n-1-x) for x in range(self.n)])}
        winning_lines |= {tuple([(x, x, y) for x in range(self.n)]) for y in range(self.n)}
        winning_lines |= {tuple([(y, x, x) for x in range(self.n)]) for y in range(self.n)}
        winning_lines |= {tuple([(x, y, x) for x in range(self.n)]) for y in range(self.n)}
        winning_lines |= {tuple([(x, self.n -1 -x, y) for x in range(self.n)]) for y in range(self.n)}
        winning_lines |= {tuple([(y, x, self.n -1 -x) for x in range(self.n)]) for y in range(self.n)}
        winning_lines |= {tuple([(x, y, self.n -1 -x) for x in range(self.n)]) for y in range(self.n)}

        return winning_lines

    def nd_index_map(self, i):
        x = i % self.n
        y = ( i // self.n ) % self.n
        z = i // ( self.n * self.n )
        return z,x,y
    
    def xyz_to_i(self, x,y,z):
        return y + x*self.n**2 + z*self.n

    def p_move(self, texture):
        for i, obj in enumerate(self.visual):
            x,y,z = self.nd_index_map(i)
            if obj.highlighted and (x,y,z) not in self.visited:
                change_texture(obj,texture)
                self.board[x][y][z] = Game.board_map[texture]
                self.visited.add((x,y,z))
                self.sounds['claim_tile'].play()
                return True
        return False

    def p2_move(self):
        if self.difficulty in ai_player:
            if self.check_victory()[0]:
                return None
            if self.difficulty == 'easy':
                i,j,k = random_move(self.board)
            elif self.difficulty == 'medium':
                i,j,k = fill_winning_lines(self.board, self.winning_lines)
            elif self.difficulty == "hard":
                i,j,k = best_move(self.board, self.winning_lines)
            if (i,j,k) not in self.visited:
                change_texture(self.visual[self.xyz_to_i(i,j,k)], 'o')
                self.board[i][j][k] = -1
                self.visited.add((i,j,k))
            else:
                self.p2_move()

        if self.difficulty == 'multiplayer':
            self.p_move('o')
    
    def run(self):
        if self.running:
            back_txt = "Back to Menu"
        else:
            back_txt = "Play Again"
        dx, dy, dz, x_rot, y_rot, z_rot, sc = 0,0,0,0,0,0,1
        quit_btn = UIElement(
            center_position=(WIDTH//2, 7*HEIGHT//8),
            font_size=30,
            bg_rgb=BLACK,
            text_rgb=GREEN,
            text="Quit",
            action=GameState.QUIT,
        )
        back_btn = UIElement(
            center_position=(7 * WIDTH//8,HEIGHT//8),
            font_size=30,
            bg_rgb=BLACK,
            text_rgb=GREEN,
            text=back_txt,
            action=GameState.TITLE,
        )
        self.screen.fill(BLACK)
        self.running = True
        winner = self.check_victory()
        if winner[0]:
            self.running = False
            buttons = [back_btn, quit_btn]
            self.curr_highlight = None
            if winner[0] == 0:
                text = font.render('Tie!', True, (0,255,0), (0,0,0))
            elif winner[1] == 1:
                text = font.render('Player 1 Wins!', True, (0,255,0), (0,0,0))
            elif winner[1] == -1:
                text = font.render('Player 2 Wins!', True, (0,255,0), (0,0,0))
            text_rect = text.get_rect()
            text_rect.center = (WIDTH // 2, HEIGHT // 8)
            z_rot = 0.0085
            mouse_up = False
            self.screen.blit(text, text_rect)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_up = True
            for button in buttons:
                ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
                if ui_action is not None:
                    return ui_action
                button.draw(self.screen)
                # pygame.display.flip()
                
        else:
            mouse_up = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.moving = True
                    mouse_up = True
                if event.type == pygame.MOUSEBUTTONUP:
                    self.moving = False
                if event.type == pygame.MOUSEMOTION and self.moving:
                    m_x, m_y = pygame.mouse.get_pos()
                    if m_x < self.prev[0]:
                        m_x = 0.1
                    elif m_x >= self.prev[0]:
                        m_x = -0.1
                    if m_y < self.prev[1]:
                        m_y = -0.1
                    elif m_y >= self.prev[1]:
                        m_y = 0.1
                    z_rot = m_x/3
                    x_rot = m_y/3
                if event.type == pygame.MOUSEWHEEL:
                    sc += event.y / 100
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    if self.difficulty in ai_player:
                        if self.p_move('x'):
                            self.p2_move()
                        else:
                            print("Choose another tile")
                    else:
                        if self.turn == 0 and self.p_move('x'):
                            self.turn = 1
                        elif self.turn == 1 and self.p_move('o'):
                            self.turn = 0
                        else:
                            print("Choose another tile")
                
                # This if block provides highlighter movement logic
                # UP/DOWN: Move the highlight in the +- y direction
                # RIGHT/LEFT: Move the highlighter in the +- x direction
                # LSHIFT + UP/DOWN: Move the highlighter in the +- z direction

                if self.curr_highlight is not None:
                    keys = pygame.key.get_pressed()
                    old_x, old_y, old_z = self.nd_index_map(self.curr_highlight)
                    if keys[pygame.K_UP] and not keys[pygame.K_LSHIFT]:
                        new_y = old_y - 1
                        new_i = self.xyz_to_i(old_x, new_y, old_z) 
                        if 0 <= new_y < self.n:
                            self.sounds['move_tile'].play()
                            self.curr_highlight = new_i
                    if keys[pygame.K_DOWN] and not keys[pygame.K_LSHIFT]:
                        new_y = old_y + 1
                        new_i = self.xyz_to_i(old_x, new_y, old_z) 
                        if 0 <= new_y < self.n:
                            self.sounds['move_tile'].play()
                            self.curr_highlight = new_i
                    if keys[pygame.K_RIGHT]:
                        new_x = old_x + 1
                        new_i = self.xyz_to_i(new_x, old_y, old_z)
                        if 0 <= new_x < self.n:
                            self.sounds['move_tile'].play()
                            self.curr_highlight = new_i
                    if keys[pygame.K_LEFT]:
                        new_x = old_x - 1
                        new_i = self.xyz_to_i(new_x, old_y, old_z) 
                        if 0 <= new_x < self.n:
                            self.sounds['move_tile'].play()
                            self.curr_highlight = new_i
                    if keys[pygame.K_LSHIFT] and keys[pygame.K_UP]:
                        new_z = old_z + 1
                        new_i = self.xyz_to_i(old_x, old_y, new_z) 
                        if 0 <= new_z < self.n:
                            self.sounds['move_tile'].play()
                            self.curr_highlight = new_i
                    if keys[pygame.K_LSHIFT] and keys[pygame.K_DOWN]:
                        new_z = old_z - 1
                        new_i = self.xyz_to_i(old_x, old_y, new_z) 
                        if 0 <= new_z < self.n:
                            self.sounds['move_tile'].play()
                            self.curr_highlight = new_i
            buttons = [quit_btn, back_btn]
            
            for button in buttons:
                ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
                if ui_action is not None:
                    return ui_action
                button.draw(self.screen)
                # pygame.display.flip()
            # This keys block provides functionality for keyboard controlled camera movement and camera reset
            # LCTRL + UP/DOWN: Rotate cube about z axis
            # LCTRL + RIGHT/LEFT: Rotate cube about x axis
            # SPACE: Reset cube positions to initial positions without changing value of cube

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LCTRL]:
                if keys[pygame.K_LEFT]:
                    z_rot -= 0.1
                if keys[pygame.K_RIGHT]:
                    z_rot += 0.1
                if keys[pygame.K_UP]:
                    x_rot += 0.1
                if keys[pygame.K_DOWN]:
                    x_rot -= 0.1
            if keys[pygame.K_SPACE]:
                self.reset_cube_position()
            self.prev = pygame.mouse.get_pos()

        # This for block displays all objects in board and highlights if possible
        for i, object_3d in enumerate(self.visual):
            object_3d.update(dx, dy, dz, x_rot, y_rot, z_rot, sc)
            if self.curr_highlight is not None and i == self.curr_highlight:
                object_3d.display(self.screen, True)
                object_3d.highlighted = True
            else:
                object_3d.display(self.screen)
                object_3d.highlighted = False
        
        # If a player has won already, display the win screen text
        
        pygame.display.flip()

        return GameState.NEWGAME

    def check_p1_win(self):
        for line in self.winning_lines:
            values = [self.board[x][y][z] for x, y, z in line]
            if all(v == 1 for v in values):
                return True, 1, line
        return False, 0
    def check_p2_win(self):
        for line in self.winning_lines:
            values = [self.board[x][y][z] for x, y, z in line]
            if all(v == -1 for v in values):
                return True, -1, line
        return False, 0
    def make_win_line(self, line):
        points = {'line': []}
        for v in line:
            center = self.visual[self.xyz_to_i(*v)].points['center'][0]
            points['line'].append(center.copy())
        win_line = Object3D(points= points)
        win_line.color = (255,255,255)
        win_line.thickness = 10
        self.visual.append(win_line)

    def check_victory(self):
        if self.won[0]:
            return self.won
        p1, p2 = self.check_p1_win(), self.check_p2_win()
        if p1[0] and p2[0]:
            self.sounds['victory'].play()
            self.won = True, 0
            return True, 0
        elif p1[0]:
            self.won = p1
            self.sounds['victory'].play()
            self.make_win_line(p1[2])
            return p1
        elif p2[0]:
            self.won = p2
            if self.difficulty == 'multiplayer':
                self.sounds['victory'].play()
            else:
                self.sounds['loss'].play()
            self.make_win_line(p2[2])
            return p2
        else:
            return False, 0

    def title_screen(self, start_txt="Start"):
        start_btn = UIElement(
            center_position=(WIDTH//2,HEIGHT//2),
            font_size=30,
            bg_rgb=BLACK,
            text_rgb=GREEN,
            text=start_txt,
            action=GameState.NEWGAME,
        )
        how_to_play_btn = UIElement(
            center_position=(WIDTH//2, 5*HEIGHT//8),
            font_size=30,
            bg_rgb=BLACK,
            text_rgb=GREEN,
            text="How To Play",
            action=GameState.HOWTOPLAY,
        )
        quit_btn = UIElement(
            center_position=(WIDTH//2, 3*HEIGHT//4),
            font_size=30,
            bg_rgb=BLACK,
            text_rgb=GREEN,
            text="Quit",
            action=GameState.QUIT,
        )
        size_increase_btn = UIElement(
            center_position=(WIDTH//16 + 75, HEIGHT//16),
            font_size=20,
            bg_rgb=BLACK,
            text_rgb=GREEN,
            text="+1",
            action= size_inc(self.n),
        )
        size_decrease_btn = UIElement(
            center_position=(WIDTH//16+25, HEIGHT//16),
            font_size=20,
            bg_rgb=BLACK,
            text_rgb=GREEN,
            text="-1",
            action= size_dec(self.n),
        )
        mode_display_btn = UIElement(
            center_position=(7 * WIDTH//8 + 25, HEIGHT//8 - 50),
            font_size=20,
            bg_rgb=BLACK,
            text_rgb=GREEN,
            text= modes[self.mode],
            action = mode_change(self.mode),
        )

        title_card, n_display, mode_select = "T-CUBED", f"Board size: {self.n}", "Game Mode"
        buttons = [start_btn, how_to_play_btn, quit_btn]
        if not self.running:
            buttons += [size_increase_btn, size_decrease_btn, mode_display_btn]
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            self.screen.fill(BLACK)
        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            blit_text(self.screen, title_card, (WIDTH//2 - 190, HEIGHT//3 - 100), pygame.font.SysFont('Tahoma', 96), GREEN)
            if not self.running:
                blit_text(self.screen, n_display, (WIDTH//16, HEIGHT//8 - 100), pygame.font.SysFont('Tahoma', 20), GREEN)
                blit_text(self.screen, mode_select, (7 * WIDTH//8, HEIGHT//8- 100), pygame.font.SysFont('Tahoma', 20), GREEN)
            button.draw(self.screen)
        pygame.display.flip()
        return GameState.TITLE
    
    def how_to_play(self):
        back_btn = UIElement(
            center_position=(7 * WIDTH//8,HEIGHT//8),
            font_size=30,
            bg_rgb=BLACK,
            text_rgb=GREEN,
            text="Back to Title",
            action=GameState.TITLE,
        )
        with open("text_files/instructions.txt") as f:
            instructions = f.read()
            f.close() 

        buttons = [back_btn]
        mouse_up = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            self.screen.fill(BLACK)
            # self.screen.blit(controls, controls_rect)
        for button in buttons:
            ui_action = button.update(pygame.mouse.get_pos(), mouse_up)
            if ui_action is not None:
                return ui_action
            button.draw(self.screen)
            blit_text(self.screen, instructions, (WIDTH//6, HEIGHT//6), pygame.font.SysFont('Tahoma',16), GREEN)
        pygame.display.flip()
        return GameState.HOWTOPLAY
    
    async def main(self):
        pygame.init()
   
        FPS = 60
        FramePerSec = pygame.time.Clock()
        FramePerSec.tick(FPS)

        pygame.display.set_caption("T^3")
        
        start_music = self.sounds['title_music']
        self.n = 4
        self.mode = 0 # easy, 1: multiplayer
        start_music.play(loops=-1)
        game_state = GameState.TITLE
        while True:
            if not self.running:
                self.difficulty = modes[self.mode]
            if game_state == GameState.TITLE:
                if self.prepared and not self.running:
                    start_music.play(loops=-1)
                if self.running:
                    start_txt = "CONTINUE"
                else:
                    start_txt = "Start"
                    self.prepared = False
                game_state = self.title_screen(start_txt)
        
            if game_state == GameState.NEWGAME:
                self.prepare_game()
                start_music.stop()
                game_state = self.run()
            
            if game_state == GameState.QUIT:
                pygame.mixer.quit()
                pygame.quit()
                return
            
            if game_state == GameState.HOWTOPLAY:
                game_state = self.how_to_play()

            if game_state == 'INCREASED':
                if self.n < 12:
                    self.n += 1
            if game_state == 'DECREASED':
                if self.n > 2:
                    self.n -= 1
            if game_state == 'CHANGED':
                self.mode += 1
                self.mode %= len(modes)
            if game_state in ('CHANGED','DECREASED','INCREASED'):
                game_state = self.title_screen()
            # pygame.display.flip()
            pygame.display.update()
            await asyncio.sleep(0)
if __name__ == "__main__":
    g = Game()
    asyncio.run( g.main() )
    