import pygame
import os, sys
import random

pygame.init()
size = width, height = 1024, 700
screen = pygame.display.set_mode(size)
FPS = 60
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
tank_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
damage_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ['нажмите любую клавишу']

    fon = pygame.transform.scale(load_image('game_over.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord = 650
        intro_rect.top = text_coord
        intro_rect.x = 100
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    print(fullname)

    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '%':
                Tile('empty', x, y)
            elif level[y][x] == '+':
                Tile('lava', x, y)


tile_images = {
    'wall': load_image('obsidian.png'),
    'empty': load_image('cobblestone.png'),
    'lava': load_image('lava.png')
}

tile_width = tile_height = 64


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        if tile_type == 'wall':
            wall_group.add(self)
        if tile_type == 'lava':
            damage_group.add(self)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Bullet(pygame.sprite.Sprite):
    pass


class Tank(pygame.sprite.Sprite):
    def __init__(self, sheet, speed, x, y, columns=4, rows=1):
        super().__init__(tank_group, all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 3
        self.image = self.frames[self.cur_frame]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.speed = speed

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def go(self, x=0, y=0):
        if x == 1:
            self.image = self.frames[3]
        elif x == -1:
            self.image = self.frames[0]
        elif y == 1:
            self.image = self.frames[2]
        elif y == -1:
            self.image = self.frames[1]
        return self.rect.x + self.speed * x, self.rect.y + self.speed * y


def main():
    fps = 60
    running = True
    generate_level(load_level('level.txt'))
    tank = Tank(load_image('heavy_tank.png'), 200, 64, 64)
    all_sprites.add(tank)
    tank_group.add(tank)
    all_sprites.draw(screen)
    go_x, go_y = None, None
    while running:
        # внутри игрового цикла ещё один цикл
        # приема и обработки сообщений
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    go_x, go_y = tank.go(0, -1)
                if event.key == pygame.K_DOWN:
                    go_x, go_y = tank.go(0, 1)
                if event.key == pygame.K_LEFT:
                    go_x, go_y = tank.go(-1, 0)
                if event.key == pygame.K_RIGHT:
                    go_x, go_y = tank.go(1, 0)
        try:
            if tank.rect.x < go_x:
                if not pygame.sprite.spritecollideany(tank, wall_group):
                    tank.rect.x += tank.speed // FPS
                else:
                    tank.rect.x -= 5
                    go_x = tank.rect.x
            if tank.rect.x > go_x:
                if not pygame.sprite.spritecollideany(tank, wall_group):
                    tank.rect.x -= tank.speed // FPS
                else:
                    tank.rect.x += 5
                    go_x = tank.rect.x
            if tank.rect.y < go_y:
                if not pygame.sprite.spritecollideany(tank, wall_group):
                    tank.rect.y += tank.speed // FPS
                else:
                    tank.rect.y -= 5
                    go_y = tank.rect.y
            if tank.rect.y > go_y:
                if not pygame.sprite.spritecollideany(tank, wall_group):
                    tank.rect.y -= tank.speed // FPS
                else:
                    tank.rect.y += 5
                    go_y = tank.rect.y
        except TypeError:
            pass
        if pygame.sprite.spritecollideany(tank, damage_group):
            start_screen()
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == '__main__':
    main()
