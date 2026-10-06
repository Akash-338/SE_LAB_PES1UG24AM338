import pygame
import random
from game.ship import Ship
from game.meteor import Meteor

WIDTH,HEIGHT=700,520
FPS=60
BG=(8,5,20)

class Laser:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x-2,y-16,4,16)
        self.speed=10

    def update(self):
        self.rect.y-=self.speed

    def off_screen(self):
        return self.rect.bottom<0

    def draw(self, screen):
        pygame.draw.rect(screen,(100,240,255),self.rect)
        pygame.draw.rect(screen,(220,255,255),self.rect.inflate(-2,0))

class ShieldOrb:
    def __init__(self, width):
        self.x=random.randint(24,width-24)
        self.y=-24
        self.radius=14
        self.speed=2

    def update(self):
        self.y+=self.speed

    def off_screen(self, height):
        return self.y-self.radius>height

    def draw(self, screen):
        pygame.draw.circle(screen,(80,220,255),(int(self.x),int(self.y)),self.radius,2)
        pygame.draw.circle(screen,(140,255,220),(int(self.x),int(self.y)),5)

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Meteor Dodge")
        self.clock=pygame.time.Clock()
        self.font=pygame.font.SysFont("monospace",26,bold=True)
        self.big_font=pygame.font.SysFont("monospace",46,bold=True)
        self.stars=[(random.randint(0,WIDTH),random.randint(0,HEIGHT),random.randint(1,3)) for _ in range(80)]
        self.reset()

    def reset(self):
        self.ship=Ship(WIDTH//2,HEIGHT-80)
        self.meteors=[]
        self.lasers=[]
        self.shield_orbs=[]
        self.shield_active=False
        self.orb_timer=0
        self.orb_spawn_interval=random.randint(FPS*8,FPS*12)
        self.timer=0
        self.spawn_interval=60
        self.survival_frames=0
        self.consecutive_survival_frames=0
        self.base_score=0
        self.score=0
        self.multiplier=1
        self.game_over=False
        self.started=False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: return False
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_SPACE:
                    if self.game_over:
                        self.reset()
                    elif not self.started:
                        self.started=True
                    else:
                        self.lasers.append(Laser(*self.ship.rect.center))
        return True

    def update(self):
        if self.game_over or not self.started: return
        keys=pygame.key.get_pressed()
        self.ship.move(keys,WIDTH,HEIGHT)
        self.survival_frames+=1
        self.consecutive_survival_frames+=1
        self.base_score+=1
        self.multiplier=1+self.consecutive_survival_frames//(FPS*10)
        self.score+=self.multiplier
        self.timer+=1
        if self.timer>=self.spawn_interval:
            self.meteors.append(Meteor(WIDTH))
            self.timer=0
            self.spawn_interval=max(20,self.spawn_interval-0.3)
        self.orb_timer+=1
        if self.orb_timer>=self.orb_spawn_interval and not self.shield_orbs:
            self.shield_orbs.append(ShieldOrb(WIDTH))
            self.orb_timer=0
            self.orb_spawn_interval=random.randint(FPS*8,FPS*12)
        active_orbs=[]
        for orb in self.shield_orbs:
            orb.update()
            dx=orb.x-self.ship.rect.centerx
            dy=orb.y-self.ship.rect.centery
            if (dx**2+dy**2)**0.5 < orb.radius+16:
                self.shield_active=True
            elif not orb.off_screen(HEIGHT):
                active_orbs.append(orb)
        self.shield_orbs=active_orbs
        shielded_meteors=[]
        for m in self.meteors:
            m.update()
            if m.collides(self.ship.rect):
                if self.shield_active:
                    self.shield_active=False
                    self.consecutive_survival_frames=0
                    self.multiplier=1
                    shielded_meteors.append(m)
                else:
                    self.consecutive_survival_frames=0
                    self.multiplier=1
                    self.game_over=True
        if shielded_meteors:
            self.meteors=[m for m in self.meteors if m not in shielded_meteors]
        self.meteors=[m for m in self.meteors if not m.off_screen(HEIGHT)]
        active_lasers=[]
        destroyed_meteors=[]
        new_fragments=[]
        for laser in self.lasers:
            laser.update()
            if laser.off_screen():
                continue
            hit_meteor=None
            for meteor in self.meteors:
                if meteor in destroyed_meteors:
                    continue
                dx=meteor.x-laser.rect.centerx
                dy=meteor.y-laser.rect.centery
                if (dx**2+dy**2)**0.5 < meteor.radius+4:
                    hit_meteor=meteor
                    break
            if hit_meteor is not None:
                destroyed_meteors.append(hit_meteor)
                new_fragments.extend(hit_meteor.create_fragments())
            else:
                active_lasers.append(laser)
        if destroyed_meteors:
            self.meteors=[m for m in self.meteors if m not in destroyed_meteors]
            self.meteors.extend(new_fragments)
        self.lasers=active_lasers
    def draw(self):
        self.screen.fill(BG)
        for sx,sy,sr in self.stars:
            pygame.draw.circle(self.screen,(200,200,220),(sx,sy),sr)
        for m in self.meteors: m.draw(self.screen)
        for orb in self.shield_orbs: orb.draw(self.screen)
        for laser in self.lasers: laser.draw(self.screen)
        self.ship.draw(self.screen)
        if self.shield_active:
            pygame.draw.circle(self.screen,(80,220,255),self.ship.rect.center,30,2)
            pygame.draw.circle(self.screen,(160,255,240),self.ship.rect.center,26,1)
        sc=self.font.render(f"Time: {self.survival_frames//60}s",True,(200,200,240))
        self.screen.blit(sc,(10,10))
        score_text=self.font.render(f"Score: {self.score}",True,(200,200,240))
        self.screen.blit(score_text,(10,40))
        multiplier_text=self.font.render(f"Multiplier: {self.multiplier}x",True,(200,240,200))
        self.screen.blit(multiplier_text,(10,70))
        if not self.started:
            msg=self.font.render("Press SPACE to launch",True,(180,180,240))
            self.screen.blit(msg,(WIDTH//2-msg.get_width()//2,HEIGHT//2))
        if self.game_over:
            ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            ov.fill((0,0,0,150))
            self.screen.blit(ov,(0,0))
            m=self.big_font.render("DESTROYED!",True,(220,80,60))
            s=self.font.render(f"Survived {self.survival_frames//60}s | SPACE to Restart",True,(200,200,200))
            self.screen.blit(m,(WIDTH//2-m.get_width()//2,HEIGHT//2-40))
            self.screen.blit(s,(WIDTH//2-s.get_width()//2,HEIGHT//2+20))
        pygame.display.flip()

    def run(self):
        running=True
        while running:
            running=self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
