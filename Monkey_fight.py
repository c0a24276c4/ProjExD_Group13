import math
import os
import random
import sys
import time
import pygame as pg


os.chdir(os.path.dirname(os.path.abspath(__file__)))
WIDTH = 663  # ゲームウィンドウの幅
HEIGHT = 663  # ゲームウィンドウの高さ


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
        pg.K_SPACE: (0,),
        pg.K_UP: (0, -2),
        pg.K_DOWN: (0, 2)
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/2.png"), 0, 0.7)
    img = pg.transform.flip(img0, True, False)
    imgs = {
        (+1, 0): img0,
        (-1, 0): img,
    }
    gravity = +0.1

    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.imgs[(+1, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.jump_state = False
        self.jump_high = -4
        self.on_ladder = False

    def change_img(self, num: int, screen: pg.Surface):
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface, ladder_rects: list[pg.Rect]):
        sum_mv = [0, 0]
    
    # 「↑キーが押されていて、かつはしごに重なっている」場合だけ登り判定を有効にする
        if key_lst[pg.K_UP]:
            self.on_ladder = any(self.rct.colliderect(lad) for lad in ladder_rects)
        else:
            self.on_ladder = False

        if self.on_ladder:
            sum_mv[1] = -2
            self.jump_state = False
            self.jump_high = -4
        else:
            # 横移動と画像切替（通常どおり）
            for k, mv in __class__.delta.items():
                if key_lst[k] and k != pg.K_SPACE and k not in [pg.K_UP, pg.K_DOWN]:
                    sum_mv[0] += mv[0]
                if k == pg.K_RIGHT:
                    self.img = __class__.img0
                if k == pg.K_LEFT:
                    self.img = __class__.img
                elif key_lst[k] and k == pg.K_SPACE:
                    self.jump_state = True

        # はしごにいないときだけジャンプ・重力
        if self.jump_state:
            sum_mv[1] += self.jump_high
            self.jump_high += __class__.gravity

        # ↓キーで降りる（常に許可）
        if key_lst[pg.K_DOWN]:
            sum_mv[1] += 2

        self.rct.move_ip(sum_mv)
    
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
            self.jump_state = False
            self.jump_high = -4

        screen.blit(self.img, self.rct)



class wall(pg.sprite.Sprite):
    """
    足場に関するクラス
    """
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/brick_wall_3x.png"), 0, 0.08)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y


def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.transform.rotozoom(pg.image.load(f"fig/back.webp"), 0, 1.3)
    walls = pg.sprite.Group()
    clock = pg.time.Clock()
    bird = Bird((300, 200))
    hashigo = pg.transform.rotozoom(pg.image.load(f"fig/hashigo.png"), 0, 0.085)

    ladder_rects = [
        hashigo.get_rect(topleft=(480, 530)),
        hashigo.get_rect(topleft=(200, 390)),
        hashigo.get_rect(topleft=(480, 250)),
        hashigo.get_rect(topleft=(210, 130))
    ]

    for i in range(8):
        walls.add(wall(i*90, 630))
    for i in range(6):
        walls.add(wall(i*90, 500))
    for i in range(6):
        walls.add(wall(120+i*90, 360))
    for i in range(6):
        walls.add(wall(i*90, 220))
    walls.add(wall(200, 120))

    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0

        screen.blit(bg_img, [0, 0])
        for lad in ladder_rects:
            screen.blit(hashigo, lad.topleft)

        walls.draw(screen)
        bird.update(key_lst, screen, ladder_rects)
        pg.display.update()
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
