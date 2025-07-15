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


def score_screen(msg: str, score: int, screen: pg.Surface, tmr: int):
    over = pg.Surface((WIDTH, HEIGHT))
    over.set_alpha(255)
    over.fill((0, 0, 0))
    screen.blit(over, (0, 0))

    font = pg.font.Font(None, 80)
    if msg == "Clear":
        score += 500*tmr
        txt = font.render(f"score: {score}", True, (0, 255, 0))
    else:
        txt = font.render(f"score: {score}", True, (255, 0, 0))
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH // 2, HEIGHT // 2 + 100
    screen.blit(txt, txt_rct)

    pg.display.update()

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
            self.sky_state = True
            self.jump_high = -1
        
        else:
            # 横移動と画像切替（通常どおり）
            for k, mv in __class__.delta.items():
                if key_lst[k] and k != pg.K_SPACE and k not in [pg.K_UP, pg.K_DOWN]:
                    sum_mv[0] += mv[0]
                    #print(mv)
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
                #print("a")
                sum_mv[1] += self.sky_high
                self.sky_high += __class__.gravity
            else:
                self.sky_high = 0


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
        """
        引数1 x：足場を表示する左上x座標
        引数2 y：足場を表示する左上y座標
        """
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
    over.set_alpha(0)
    over.fill((0, 0, 0))
    screen.blit(over, (0, 0))

    font = pg.font.Font(None, 80)
    txt = font.render(msg, True, color)
    txt_rct = txt.get_rect()
    txt_rct.center = WIDTH // 2, HEIGHT // 2-100
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
        self.rct = self.image.get_rect()
        self.rct.center = 100, HEIGHT-630

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rct)

class Timer:
    """
    残り時間を表示するクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (255, 255, 0)
        self.value = 180
        self.image = self.font.render(f"time: {self.value}", 0, self.color)
        self.rct = self.image.get_rect()
        self.rct.center = 500, HEIGHT-630

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"time: {self.value}", 0, self.color)
        screen.blit(self.image, self.rct)


class enemy:
    """
    敵に関するクラス
    """
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/gorira.png"), 0, 0.2)
        self.rct = self.image.get_rect()
    

class taru(pg.sprite.Sprite):
    """
    敵の攻撃(樽)に関するクラス
    """

    gravity = +0.05

    def __init__(self, gorilla: "enemy"):
        """
        引数1 gorilla：攻撃を出す対象
        """
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/taru.png"),0, 0.05)
        self.rct = self.image.get_rect()
        #self.rct.width = 10 # 敵の攻撃(樽)の当たり判定
        #self.rct.height = 10
        self.rct.left = gorilla.rct.centerx #敵の攻撃(樽)の初期位置
        self.rct.bottom = gorilla.rct.bottom+16
        self.vx = +3 # 敵の攻撃(樽)の移動スピード
        self.sky_state = False
        self.vy = 0 
        self.sky_high = 0

    def update(self, screen: pg.Surface):
        """
        引数1 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct) # 講義で使ったチェックバウンドを横判定だけにしたもので判別
        if not yoko:
            self.vx *= -1
            if self.rct.bottom >= 600 and self.rct.left <= 100:
                self.kill()

        if not self.sky_state:  # 床にいるかの判定
            #print("a")
            self.vy += self.sky_high
            self.sky_high += __class__.gravity
        else:
            self.vy = 0

        

    
        self.rct.move_ip(self.vx, self.vy) # 横移動だけ更新
        screen.blit(self.image, self.rct)

def main():
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.transform.rotozoom(pg.image.load(f"fig/back.webp"), 0, 1.3)
    walls = pg.sprite.Group()
    clock = pg.time.Clock()
    bird = Bird((450, 100))  #100 605
    score = Score()
    hashigo = pg.transform.rotozoom(pg.image.load(f"fig/hashigo4.png"), 0, 0.085)  # 梯子を獲得
    takara = pg.transform.rotozoom(pg.image.load(f"fig/takara.png"), 0, 0.05)  # 宝を獲得
    takara_rect = takara.get_rect()
    takara_rect.center = 220, 40
    print(takara_rect)
    gorilla = enemy()
    tarus = pg.sprite.Group()
    tarus.add(taru(gorilla))
    tmr = 0  
    timer = Timer()  

    ladder_rects = [
        hashigo.get_rect(topleft=(480, 500)),
        hashigo.get_rect(topleft=(200, 360)),
        hashigo.get_rect(topleft=(480, 220)),
        hashigo.get_rect(topleft=(210, 90))
    ]

    for i in range(8):
        walls.add(Wall(i*90, 630))
    for i in range(6):
        walls.add(Wall(i*90, 500))
    for i in range(6):
        walls.add(Wall(120+i*90, 360))
    for i in range(6):
        walls.add(Wall(i*90, 220))
    walls.add(Wall(200, 90))

    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0

        screen.blit(bg_img, [0, 0])
        screen.blit(takara, [220, 40])
        for lad in ladder_rects:
            screen.blit(hashigo, lad.topleft)

        # screen.blit(hashigo, [480, 500])
        # screen.blit(hashigo, [200, 360])
        # screen.blit(hashigo, [480, 220])
        # screen.blit(hashigo, [210, 100])

        bird.sky_state = False
        for i,wall in enumerate(walls):  # 床の情報を取得
            if wall.rect.colliderect(bird.rct):  # 床のrectとこうかとんのrectのが重なっているのかの判定
                # print(i)
                if wall.wall_bound(bird.rct):  # 床にいるのか判定
                    bird.jump_high = -4
                    bird.jump_state = False
                    bird.sky_state = True
        
        for i, taru_x in enumerate(tarus):
            taru_x.sky_state = False
            for i,wall in enumerate(walls):  # 床の情報を取得
                for i, taru_y in enumerate(tarus):
                    if wall.rect.colliderect(taru_y.rct):
                        taru_y.sky_state = True


        for i, taru1 in enumerate(tarus):  # 樽とあたったら終了
            if taru1.rct.colliderect(bird.rct):
                score_screen("a", score.value, screen, timer.value)
                game_end(screen, "Game Over",(255, 0, 0)) #oキーを押すとゲームオーバー
                return 0
        if takara_rect.colliderect(bird.rct):
            print("a")
            score_screen("Clear", score.value, screen, timer.value)
            game_end(screen, "Game Clear", (0, 255, 0)) #cキーを押すとゲームクリア
            return 0
        if tmr%200 == 0:  # 200フレームに1回，ゴリラの攻撃(樽)を出現させる
            tarus.add(taru(gorilla))
        if gorilla.rct.colliderect(bird.rct):  # ゴリラとあたったら終了
            score_screen("a", score.value, screen, timer.value)
            game_end(screen, "Game Over", (255, 0, 0)) #oキーを押すとゲームオーバー
            return 0 
        
        tarus.update(screen)
        screen.blit(gorilla.image, [15, 63])
        walls.draw(screen)
        bird.update(key_lst, screen, ladder_rects)
        score.update(screen)
        timer.update(screen)
        pg.display.update()
        tmr += 1
        if tmr % 50 == 0:
            score.value += 1
            timer.value -= 1
        if timer.value < 0:
            score_screen("a", score.value, screen, timer.value)
            game_end(screen, "Game Over", (255, 0, 0)) #oキーを押すとゲームオーバー
            return 0

        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
