import pygame,math,random
from pygame import Vector2


Map = [
[1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,1],
[1,0,0,0,0,0,0,0,0,1],
[1,0,0,0,1,1,0,0,0,1],
[1,0,0,0,1,1,0,0,0,1],
[1,0,0,0,0,0,0,0,0,1],
[1,0,1,0,0,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1]
]


pygame.init()

screen = pygame.display.set_mode((800,400))
screen.set_alpha()

clock = pygame.time.Clock()


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

class Boundary:
    
    def __init__(self,point1,point2):
        self.a = Vector2(point1)
        self.b = Vector2(point2)
    
    def Show(self):
        a = (self.a.x + 400,self.a.y )
        b = (self.b.x + 400,self.b.y)
        pygame.draw.line(screen,(255,255,255),a,b)


FOV = 40
class Particle:
    
    def __init__(self):
        self.pos = Vector2(200,200)
        self.dir = Vector2(1,0)
        self.CreateRays()
    
    def CreateRays(self):
        self.rays = []
        angle = math.sqrt(self.dir[0]**2 + self.dir[1]**2)
        for x in range(0,FOV*3,1):
            self.rays.append(Ray(self.pos,angle + x/3))        
    
    def rotate(self,angle):
        self.dir = self.dir.rotate(angle)
        for ray in self.rays:
            ray.Rotate(angle)
    
    def Move(self,mag):
        self.pos += self.rays[len(self.rays)//2].Dir * mag
        for ray in self.rays:
            ray.Move(self.pos)
    
    def look(self,walls):
        width = 400//len(self.rays)
        dists = []
        for x,ray in enumerate(self.rays):
            closest = None
            record = 400
            for wall in walls:
                pt = ray.cast(wall)
                if pt:
                    d = Dist(self.pos, pt)
                    a = math.atan2(ray.Dir[0],ray.Dir[1]) - math.atan2(self.dir[0],self.dir[1])
                    #print(a)
                    #d *= math.cos(a)
                    if d < record:
                        record = d
                        closest = pt
            if closest:
                #pygame.draw.line(screen,(255,255,255),(int(self.pos.x),int(self.pos.y)),(int(closest.x),int(closest.y)))
                height = translate(record,0,400,400,0)
                col = translate(record**2,0,400**2,255,0)
                pygame.draw.rect(screen,(col,col,col),(x*width,200 - (height/2),width,height))
                
    
    def update(self,x,y):
        self.pos.x = x
        self.pos.y = y
    
    
    def Show(self):
        pygame.draw.circle(screen,(255,255,255),(int(self.pos.x + 400),int(self.pos.y)),5)
        self.rays[0].Show()
        self.rays[-1].Show()
        #for x in range(len(self.rays)):
            #self.rays[x].Show()


def Dist(pt1, pt2):
    return math.sqrt(abs(pt1.x - pt2.x)**2 + abs(pt1.y - pt2.y)**2)
    #return abs(pt1.x - pt2.x) + abs(pt1.y - pt2.y)


class Ray:
    
    def __init__(self,pos,angle):
        self.pos = pos
        self.Dir = Vector2(1,0)
        self.Dir = self.Dir.rotate(angle)
    
    def Show(self):
        pos = (self.pos.x + 400,self.pos.y)
        pygame.draw.line(screen,(255,255,255),pos,pos + (self.Dir*50))
    
    def Move(self,point):
        self.pos = point
    
    def lookAt(self,x,y):
        self.Dir.x = x - self.pos.x
        self.Dir.y = y - self.pos.y
        self.Dir = self.Dir.normalize()
    
    def Rotate(self,angle):
        self.Dir = self.Dir.rotate(angle)
    
    def cast(self,wall):
        x1 = wall.a.x
        y1 = wall.a.y
        x2 = wall.b.x
        y2 = wall.b.y
        
        x3 = self.pos.x
        y3 = self.pos.y
        x4 = self.pos.x + self.Dir.x
        y4 = self.pos.y + self.Dir.y
        
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            return 
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
        
        if t > 0 and t < 1 and u > 0:
            pt = Vector2()
            pt.x = x1 + t * (x2 - x1)
            pt.y = y1 + t * (y2 - y1)
            return pt
        return


walls = []

for x in range(len(Map)):
    for y in range(len(Map[x])):
        if (y == 0 or y == len(Map)-1) and (x == 0 or x == len(Map[x])-1):
            continue
        if Map[x][y]:
            if x != len(Map) -1:
                if Map[x+1][y] == False:
                    walls.append(Boundary((y*40,(x+1)*40),((y+1)*40,(x+1)*40)))
            if x != 0:
                if Map[x-1][y] == False:
                    walls.append(Boundary((y*40,x*40),((y+1)*40,x*40)))
            if y != len(Map[x])-1:
                if Map[x][y+1] == False:
                    walls.append(Boundary(((y+1)*40,x*40),((y+1)*40,(x+1)*40))) 
            if y != 0:
                if Map[x][y-1] == False:
                    walls.append(Boundary((y*40,(x)*40),(y*40,(x+1)*40)))     


#for x in range(5):
    #walls.append(Boundary((random.randint(0,400),random.randint(0,400)),(random.randint(0,400),random.randint(0,400))))
    
#walls.append(Boundary((0,0),(0,400)))
#walls.append(Boundary((0,0),(400,0)))
#walls.append(Boundary((400,0),(400,400)))
#walls.append(Boundary((0,400),(400,400)))


particle = Particle()
key = ""

running = True
while running:
    screen.fill((0,0,0))
    
    mouseX,mouseY = pygame.mouse.get_pos()
    
    #particle.update(mouseX,mouseY)
    for wall in walls:
        wall.Show()

    particle.Show()
    particle.look(walls)
    p = False
    
    clock.tick(40)
    #print(clock.get_fps())
    
    if key == "a":
        particle.rotate(-4)
    if key == "d":
        particle.rotate(4)
    if key == "w":
        particle.Move(2)
    if key == "s":
        particle.Move(-2)
        
    
    pygame.display.update()
    for e in pygame.event.get():
        if e.type == 12:
            pygame.quit()
            running = False
        if e.type == 2:
            key = e.unicode
        if e.type == 3:
            key = ""
            