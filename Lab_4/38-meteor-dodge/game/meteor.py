import pygame
import random
import math

class Meteor:
    def __init__(self, width, x=None, y=None, radius=None, vx=None, vy=None, can_split=None, color=None):
        self.x = random.randint(0, width) if x is None else x
        self.y = -30 if y is None else y
        self.radius = random.randint(12, 28) if radius is None else radius
        if vx is None or vy is None:
            angle = random.uniform(70,110)
            speed = random.uniform(2,5)
            self.vx = math.cos(math.radians(angle))*speed
            self.vy = math.sin(math.radians(angle))*speed
        else:
            self.vx = vx
            self.vy = vy
        self.can_split = self.radius >= 20 if can_split is None else can_split
        self.color = color if color is not None else (
            random.randint(160,220),
            random.randint(80,120),
            random.randint(40,80)
        )
        self.rot = 0
        self.rot_speed = random.uniform(-3,3)

    def create_fragments(self):
        if not self.can_split:
            return []
        base_angle=math.atan2(self.vy,self.vx)
        speed=max(3,math.hypot(self.vx,self.vy)*1.15)
        fragment_radius=max(8,int(self.radius*0.55))
        fragments=[]
        for direction in (-1,1):
            angle=base_angle+math.radians(28*direction)
            fragments.append(Meteor(
                0,
                x=self.x,
                y=self.y,
                radius=fragment_radius,
                vx=math.cos(angle)*speed,
                vy=math.sin(angle)*speed,
                can_split=False,
                color=self.color
            ))
        return fragments

    def update(self):
        self.x+=self.vx; self.y+=self.vy
        self.rot=(self.rot+self.rot_speed)%360

    def off_screen(self, height):
        return self.y > height + 60

    def collides(self, rect):
        cx,cy=rect.centerx,rect.centery
        dx,dy=self.x-cx,self.y-cy
        return (dx**2+dy**2)**0.5 < self.radius + 16

    def draw(self, screen):
        import math
        pts=[]
        for i in range(7):
            angle=math.radians(self.rot+i*(360/7))
            r=self.radius*(0.8+0.2*(i%2))
            pts.append((int(self.x+r*math.cos(angle)),int(self.y+r*math.sin(angle))))
        pygame.draw.polygon(screen,self.color,pts)
        inner=[(int(self.x+(r*0.5)*math.cos(math.radians(self.rot+i*(360/7)))),
                int(self.y+(r*0.5)*math.sin(math.radians(self.rot+i*(360/7)))))
               for i,(cx,cy) in enumerate(pts)]
        pygame.draw.polygon(screen,tuple(max(0,c-40) for c in self.color),inner)
