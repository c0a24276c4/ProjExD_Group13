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
        pg.K_RIGHT: (1, 0),
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

    gravity = +0.05

    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.imgs[(+1, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.jump_state = False
        self.sky_state = False
        self.jump_high = -1
        self.sky_high = 0
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
                    self.sky_state = False
            if self.jump_state:
                sum_mv[1] += self.jump_high
                self.jump_high += __class__.gravity
            if not self.sky_state:  # 床にいるかの判定
                print("a")
                sum_mv[1] += self.sky_high
                self.sky_high += __class__.gravity
            else:
                self.sky_high = 0

        # ↓キーで降りる（常に許可）
        if key_lst[pg.K_DOWN]:
            sum_mv[1] += 2

        self.rct.move_ip(sum_mv)
    
        if check_bound(self.rct) != (True, True):  # 四方に飛んだ場合
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
            # self.jump_state = False
            # self.jump_high = -4

        screen.blit(self.img, self.rct)




class Wall(pg.sprite.Sprite):
    """
    足場に関するクラス
    """
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/brick_wall_3x.png"), 0, 0.08)
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y

    def wall_bound(self,obj_rct: pg.Rect) -> tuple[bool, bool]:
        """
        引数：こうかとんのRect
        戻り値：ブロックに乗っているのかの判定結果（画面内：True/画面外：False）
        """
        #print(obj_rct.bottom,self.rect.top)
        ue = False
        if obj_rct.bottom-self.rect.top<=5:
            ue = True
            # print(" obj_rct.bottom > self.rect.top")
        return ue
    
def game_end(screen: pg.Surface, msg: str, color: tuple[int, int, int]): # ゲームクリア、オーバー設定
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

class Score:
    """
    スコアを表示するクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (255, 255, 0)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-630

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.transform.rotozoom(pg.image.load(f"fig/back.webp"), 0, 1.3)
    walls = pg.sprite.Group()
    clock = pg.time.Clock()
    bird = Bird((100, 100))
    score = Score()
    hashigo = pg.transform.rotozoom(pg.image.load(f"fig/hashigo.png"), 0, 0.085)  # 梯子を獲得

    ladder_rects = [
        hashigo.get_rect(topleft=(480, 530)),
        hashigo.get_rect(topleft=(200, 390)),
        hashigo.get_rect(topleft=(480, 250)),
        hashigo.get_rect(topleft=(210, 130))
    ]

    for i in range(8):
        walls.add(Wall(i*90, 630))
    for i in range(6):
        walls.add(Wall(i*90, 500))
    for i in range(6):
        walls.add(Wall(120+i*90, 360))
    for i in range(6):
        walls.add(Wall(i*90, 220))
    walls.add(Wall(200, 120))


    # print(walls)

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
        for lad in ladder_rects:
            screen.blit(hashigo, lad.topleft)

        screen.blit(hashigo, [480, 530])
        screen.blit(hashigo, [200, 390])
        screen.blit(hashigo, [480, 250])
        screen.blit(hashigo, [210, 130])
        bird.sky_state = False
        for i,wall in enumerate(walls):  # 床の情報を取得
            if wall.rect.colliderect(bird.rct):  # 床のrectとこうかとんのrectのが重なっているのかの判定
                # print(i)
                if wall.wall_bound(bird.rct):  # 床にいるのか判定
                    bird.jump_high = -4
                    bird.jump_state = False
                    bird.sky_state = True

            #     bird.sky_high = 0
            #     bird.sky_state = False
            #     print("a")

                # bird.sky_state = True
        #     bird.sky_high = 0
            #else:
        #     print("b")
                # bird.sky_state = False
            # else:
                # print("a")
        #     # Fall()
        #     # print("c")
        #     bird.sky_high += 0.1
        #     bird.sky_state = True
        #     print(bird.sky_high)
            # bird.rct.move_ip([0, bird.sky_high])
            # screen.blit(bird.img, bird.rct)

            
        walls.draw(screen)
        bird.update(key_lst, screen, ladder_rects)
        score.update(screen)
        pg.display.update()
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
