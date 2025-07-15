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
    delta = {  # 押下キーと移動量の辞書
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
        pg.K_SPACE: (0, ),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/2.png"), 0, 0.7)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+1, 0): img0,  # 右
        (-1, 0): img,  # 左
    }

    gravity = +0.1 

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+1, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.jump_state = False
        self.jump_high = -4

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k] and k != pg.K_SPACE:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
                if key_lst[k] and k == pg.K_RIGHT:
                    self.img = __class__.img0
                if key_lst[k] and k == pg.K_LEFT:
                    self.img = __class__.img
            elif key_lst[k] and k == pg.K_SPACE:
                self.jump_state = True
        if self.jump_state:
            sum_mv[1] += self.jump_high
            self.jump_high += __class__.gravity
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
            self.jump_state = False
            self.jump_high = -4
        # if not (sum_mv[0] == 0 and sum_mv[1] == 0):
        #     self.img = __class__.imgs[tuple(sum_mv)]
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


def game_end(screen: pg.Surface, msg: str, color: tuple[int, int, int]):
    over = pg.Surface((WIDTH, HEIGHT))
    over.set_alpha(200)
    over.fill((0, 0, 0))
    screen.blit(over, (0, 0))

    font = pg.font.Font(None, 80)
    txt = font.render(msg, True, color)
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH // 2, HEIGHT // 2
    screen.blit(txt, txt_rct)

    pg.display.update()
    time.sleep(3)
    pg.quit()


def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.transform.rotozoom(pg.image.load(f"fig/back.webp"), 0, 1.3)
    walls = pg.sprite.Group()
    clock = pg.time.Clock()
    bird = Bird((300, 200))
    hashigo = pg.transform.rotozoom(pg.image.load(f"fig/hashigo.png"), 0, 0.085)
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
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_o:
                    game_end(screen, "Game Over", (255, 0, 0)) #oキーを押すとゲームオーバー
                elif event.key == pg.K_c:
                    game_end(screen, "Game Clear", (0, 255, 0)) #cキーを押すとゲームオーバー
        screen.blit(bg_img, [0, 0])
        screen.blit(hashigo, [480, 530])
        screen.blit(hashigo, [200, 390])
        screen.blit(hashigo, [480, 250])
        screen.blit(hashigo, [210, 130])

            
        walls.draw(screen)
        bird.update(key_lst, screen)
        pg.display.update()
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()