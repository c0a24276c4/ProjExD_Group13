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
    yoko = True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    return yoko


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_LEFT: (-2, 0),
        pg.K_RIGHT: (+2, 0),
        pg.K_SPACE: (0, ),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/2.png"), 0, 0.7)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+2, 0): img0,  # 右
        (-2, 0): img,  # 左
    }

    gravity = +0.1 

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+2, 0)]
        self.rect: pg.Rect = self.img.get_rect()
        self.rect.center = xy
        self.jump_state = False
        self.jump_high = -4

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rect)

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
        self.rect.move_ip(sum_mv)
        if check_bound(self.rect) != (True):
            self.rect.move_ip(-sum_mv[0], -sum_mv[1])
            self.jump_state = False
            self.jump_high = -4
        # if not (sum_mv[0] == 0 and sum_mv[1] == 0):
        #     self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rect)


class wall(pg.sprite.Sprite):
    """
    足場に関するクラス
    """
    def __init__(self, x: int, y: int):
        """
        引数1 x：足場を表示する左上x座標
        引数2 y：足場を表示する左上y座標
        """
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/brick_wall_3x.png"), 0, 0.08)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y


class enemy:
    """
    敵に関するクラス
    """
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/gorira.png"), 0, 0.2)
        self.rect = self.image.get_rect()


class taru(pg.sprite.Sprite):
    """
    敵の攻撃(樽)に関するクラス
    """
    def __init__(self, gorilla: "enemy"):
        """
        引数1 gorilla：攻撃を出す対象
        """
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/taru.png"),0, 0.05)
        self.rect = self.image.get_rect()
        self.rect.width = 10  # 敵の攻撃(樽)の当たり判定
        self.rect.height = 10
        self.rect.left = gorilla.rect.centerx  #敵の攻撃(樽)の初期位置
        self.rect.bottom = gorilla.rect.bottom+16
        self.vx = +3  # 敵の攻撃(樽)の移動スピード

    def update(self, screen: pg.Surface):
        """
        引数1 screen：画面Surface
        """
        yoko = check_bound(self.rect)  # 講義で使ったチェックバウンドを横判定だけにしたもので判別
        if not yoko:
            self.vx *= -1
        self.rect.move_ip(self.vx, 0)  # 横移動だけ更新
        screen.blit(self.image, self.rect)


def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.transform.rotozoom(pg.image.load(f"fig/back.webp"), 0, 1.3)
    walls = pg.sprite.Group()
    for i in range(8):
        walls.add(wall(i*90, 630))
    for i in range(6):
        walls.add(wall(i*90, 500))
    for i in range(6):
        walls.add(wall(120+i*90, 360))
    for i in range(6):
        walls.add(wall(i*90, 220))
    walls.add(wall(200, 120))
    clock = pg.time.Clock()
    bird = Bird((300, 200))
    hashigo = pg.transform.rotozoom(pg.image.load(f"fig/hashigo.png"), 0, 0.085)
    gorilla = enemy()
    tarus = pg.sprite.Group()
    tarus.add(taru(gorilla))
    tmr = 0

    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        screen.blit(bg_img, [0, 0])
        screen.blit(hashigo, [480, 530])
        screen.blit(hashigo, [200, 390])
        screen.blit(hashigo, [480, 250])
        screen.blit(hashigo, [210, 130])

        for i in pg.sprite.spritecollide(bird, tarus, True):  # 樽とあたったら終了
            return 0
        if tmr%200 == 0:  # 200フレームに1回，ゴリラの攻撃(樽)を出現させる
            tarus.add(taru(gorilla))
        if gorilla.rect.colliderect(bird.rect):  # ゴリラとあたったら終了
            return 0 
        
        tarus.draw(screen)
        screen.blit(gorilla.image, [15, 63])
        walls.draw(screen)
        bird.update(key_lst, screen)
        tarus.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()