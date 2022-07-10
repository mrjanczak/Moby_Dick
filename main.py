import os
import pgzrun
import time
from pgzhelper import *
from math import sin, cos, pi
import numpy as np
from adventurelib import *
from adventurelib import _handle_command
from shapely.geometry import Point, LinearRing, Polygon
from pprint import pprint

# poly = Polygon(((0, 0), (0, 1), (1, 1), (1, 0)))
# point = Point(0.5, 0.5)
# q = Point((0.0, 0.0))

# screen size
WIDTH = 800
HEIGHT = 600
MARGIN = 10
# size of standard lego plate in px - one room
ROOM_W, ROOM_H = 700,700

ALF0 = 40.5
ALF1 = -16.
rad = pi/180
ALF_ = np.array([(ALF0)*rad, (ALF1)*rad, (ALF0+180)*rad, (ALF1+180)*rad,])

# Points and polygones defining rooms' exits
C = [Point(-MARGIN,-MARGIN), 
    Point(WIDTH + MARGIN,-MARGIN), 
    Point(WIDTH + MARGIN,HEIGHT + MARGIN), 
    Point(-MARGIN,HEIGHT + MARGIN) ]
P = [Point(int(cos(ALF_[0])*ROOM_H), 0), 
    Point(WIDTH, int(cos(ALF_[1])*ROOM_W)), 
    Point(WIDTH - int(cos(ALF_[0])*ROOM_H), HEIGHT), 
    Point(0, HEIGHT - int(cos(ALF_[1])*ROOM_W)) ]
Pp= [Point(int(cos(ALF_[0])*ROOM_H), -MARGIN), 
    Point(WIDTH + MARGIN, int(cos(ALF_[1])*ROOM_W)), 
    Point(WIDTH - int(cos(ALF_[0])*ROOM_H), HEIGHT + MARGIN), 
    Point(-MARGIN, HEIGHT - int(cos(ALF_[1])*ROOM_W)) ]

EX_POLY = [None] * 4
for i in range(4):
    j = (i + 1) % 4
    EX_POLY[i]= A(Polygon([Pp[i], P[i], P[j], Pp[j], C[j]]) )

# player pos. default translation when change the room - for each exit (N/E/S/W)
EX_TRANS = np.array([np.array([+cos(ALF_[2]), -sin(ALF_[2]) ]) * ROOM_H,
                     np.array([+cos(ALF_[3]), -sin(ALF_[3]) ]) * ROOM_W,
                     np.array([+cos(ALF_[0]), -sin(ALF_[0]) ]) * ROOM_H,
                     np.array([+cos(ALF_[1]), -sin(ALF_[1]) ]) * ROOM_W ]).astype(int)
def prepare_map(map_):
    """Connect adjacent rooms' exits"""
    imax = len(map_)
    for i in range(imax):
        jmax = len(map_[i])
        for j in range(jmax):
            if i < imax-1 and isinstance(map_[i][j], Room) and isinstance(map_[i+1][j], Room):
                map_[i][j].south = Exit(map_[i+1][j], EX_POLY[2], trans = EX_TRANS[2])
                map_[i+1][j].north = Exit(map_[i][j], EX_POLY[0], trans = EX_TRANS[0])
            if j < jmax-1 and isinstance(map_[i][j], Room) and isinstance(map_[i][j+1], Room):
                map_[i][j].east = Exit(map_[i][j+1], EX_POLY[1], trans = EX_TRANS[1])
                map_[i][j+1].west = Exit(map_[i][j], EX_POLY[3], trans = EX_TRANS[3])

command = '> '
message = get_message()

def layer_poly(p0):
    # rhomb polygon with bottom corner same as layer image bootom corner to position player between layers
    w = 2 * WIDTH
    h = 2 * HEIGHT
    p1 = Point(p0.x + int(h * cos(ALF_[0])), p0.y - int(h * sin(ALF_[0])))
    p2 = Point(p1.x + int(w * cos(ALF_[3])), p1.y - int(w * sin(ALF_[3])))
    p3 = Point(p2.x + int(h * cos(ALF_[2])), p2.y - int(h * sin(ALF_[2])))
    return Polygon([p0, p1, p2, p3])

Room.add_direction('up', 'down')
Room.add_direction('entry1', 'exit1')
Room.add_direction('entry2', 'exit2')
Room.add_direction('entry3', 'exit3')


# Town
# ----
town_a1 = Room("""You are in front of \"The Crossed Harpoons\" and \"The Sword-Fish Inn". It seems as too expensive for You.""")
town_a2 = Room("""You wander into the poorest, most deserted streets near the water. 
There is a cheap inn called "The Spouter Inn," run by someone unfortunately named Peter Coffin. (Bad omen? You decide.)""")
town_a3 = Room("You are in front of \"Whaleman’s Chapel\", which most sailors visit before they embark on a voyage.")
town_a3.layers = [ Layer('chapel_l1'), Layer('chapel_l2', layer_poly(Point(740,370)) ), Layer('chapel_door1')]

# Chapel edge offset - to do check exits
ring = LinearRing([[739,372],[659,350],[676,326],[624,314],[607,334],[315,250],[479,106],[799,197],[799,322]]).parallel_offset(0, 'right')
town_a3.excluded = [ A(Polygon(ring.coords)),
                     A(Polygon([[619,311],[594,340],[659,360],[681,326]]), tag='door_closed'),
                     A(Polygon([[658,350],[656,389],[685,358]]), False, tag="door_open") ]                
town_a4 = Room("You are in the port. You see 3 ships moored to harbour")

town = [[town_a1, town_a2, town_a3, town_a4],
[None, None, None, None]]
prepare_map(town)

# Overwrite default map settings
town_a3.west.point = Point(500,300) 

# Define town's interiors
# Chapel : Floor + Wall1 | Barrier | Desks 2x4
# Studio render settings: Photoreal | Orthographic | 
# Rotation 1st box | Pan X -580 Y 258 | Zoom 2

chapel_candle = Item('chapel candle', 'candle', image='chapel_candle', pos = (0,0), pick_at = None) 
chapel = Room("""When You enter the chapel, you find a group of sailors, and sailors’ wives and widows sitting silently, each of them lost in their own thoughts.
They all seem to be reading the different plaques on the walls—memorials to men who died at sea.""")
chapel.items = Bag([chapel_candle])
chapel.exit1   = Exit(town_a3,A(Polygon([[399,545],[422,522],[557,561],[530,581]])),  Point(505,535), )
town_a3.entry1 = Exit(chapel, A(Polygon([[612,334],[624,319],[665,330],[654,34]])),   Point(630,350), is_open = False )
chapel.scale = 0.27
chapel.layers = [
    Layer('chapel_floor',   items = [chapel_candle]),
    Layer('chapel_barrier',  layer_poly(Point(163,397)) ),
    Layer('chapel_desk12',   layer_poly(Point(405,377)) ),            
    Layer('chapel_desk11',   layer_poly(Point(274,491)) ),            
    Layer('chapel_desk22',   layer_poly(Point(493,405)) ),
    Layer('chapel_desk21',   layer_poly(Point(363,518)) ),
    Layer('chapel_desk32',   layer_poly(Point(583,434)) ),
    Layer('chapel_desk31',   layer_poly(Point(493,510)) ),
    Layer('chapel_desk42',   layer_poly(Point(674,458)) ),
    Layer('chapel_desk41',   layer_poly(Point(586,538)) ),
    ]      
chapel.included = [
    A(Polygon([[149,470],[252,382],[194,336],[146,331],[200,277],[238,303],[296,341],[324,341],[404,274],[797,388],[800,450],[627,602],[582,598]]))
    ]  
chapel.excluded = [
    A(Polygon([[274,491],[355,421],[310,407],[229,479]])),
    A(Polygon([[405,377],[486,307],[441,293],[360,365]])),
    A(Polygon([[363,518],[444,448],[399,434],[318,506]])),
    A(Polygon([[493,405],[574,335],[529,321],[448,393]])),
    A(Polygon([[493,510],[532,475],[491,462],[448,498]])),
    A(Polygon([[583,434],[666,360],[622,348],[539,419]])),
    A(Polygon([[586,538],[627,499],[582,485],[542,523]])),
    A(Polygon([[674,458],[755,388],[710,374],[629,446]])),
    ] 
chapel.stairs = [ Stairs(A(Polygon([[253,382],[193,336],[237,302],[295,342]])), [0,-11*rad]) ]



# Ship
# ----
ship_a1I = Room("You are at lower deck of ship Pequod")


# Sea
# ---
sea_a1 = Room("You are at the sea")


# Whale
# -----
whale_1 = Room("You are inside of the great sperm whale")


# Initiate game
# -------------
set_context("town")
current_room = town[0][2]

player = Actor("ismael",name = 'ismael', costiume = 'costiume1')
player.costiume = "costiume1"
player.icon = player.image
player.anchors=[(250, 450),(300, 450),(250, 500),(200, 450)]
player.steps = [
    ['e1','e2','e3','e2_','e1_','e4','e5','e4_'],
    ['s1','s2','s3','s2_','s1_','s4','s5','s4_'],
    ['w1','w2','w3','w2_','w1_','w4','w5','w4_'],
    ['n1','n2','n3','n2_','n1_','n4','n5','n4_'],
    ]
# player.steps = [os.path.join(player.player.costiume, step) for step in player.steps]   
# player.steps = [os.path.join(player.player.image, step) for step in player.steps]   

player.image = player.steps[0][0]
player.dir0 = player.dir1 = 0
player.anchor = player.anchors[player.dir1]
player.images = player.steps[player.dir1]
player.scale = current_room.scale # default 0.2

print(vars(current_room.west))

player.pos = current_room.west.point.x, current_room.west.point.x  # 630,350
player.fps = 15
player.speed = 2 # px/frame
player.layer = len(current_room.layers) - 1

# Define inventory
inventory = Bag()


def blit_text(surface, text, pos, font=pygame.font.SysFont('Arial', 20), color=pygame.Color('white')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    max_width -= 2*x
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

def draw():
    global player, current_room
    screen.clear()

    for l,layer in enumerate(current_room.layers):
        image_path = os.path.join('')
        screen.blit(layer.image, (0, 0))

        if layer.items:
            for i, item in enumerate(layer.items): 
                screen.blit(item.image, item.pos)

        if player.layer == l:
            player.draw()
            screen.draw.circle(player.pos, 2, (255,0,0))

        poly = current_room.layers[player.layer].poly
        if isinstance(poly, Polygon):
            c = poly.exterior.coords
            screen.draw.line(c[0], c[1], (255, 0, 0))
            screen.draw.line(c[1], c[2], (255, 0, 0))
            screen.draw.line(c[2], c[3], (255, 0, 0))
            screen.draw.line(c[3], c[0], (255, 0, 0))


    screen.draw.text(command, (20, 20), fontsize=20)
    blit_text(screen.surface, message, (20, 40))

def on_mouse_down(pos):
    if player.collidepoint(pos):
        #sounds.eep.play()
        player.image = 'e2'
        time.sleep(1)
        player.image = 'e1'

def update():
    global player, ALF_, SPEED, message, command, current_room
    player.dir0 = player.dir1
    if keyboard.up:
        player.dir1 = 0
    elif keyboard.right:
        player.dir1 = 1
    elif keyboard.down:
        player.dir1 = 2
    elif keyboard.left:
        player.dir1 = 3

    if keyboard.left or keyboard.right or keyboard.up or keyboard.down:   
        if player.dir0 != player.dir1: 
            pos0 = player.pos
            player.anchor = player.anchors[player.dir1]
            player.images = player.steps[player.dir1]
            current_room.scale
            player.pos = pos0

        x0,y0 = player.x, player.y     

        # stairs detection
        alf_ = ALF_
        for stairs in current_room.stairs:
            if stairs.steps.active and Point(player.x, player.y).within(stairs.steps.poly):
                alf_ = ALF_ + np.append(stairs.bet, stairs.bet)

        player.x += player.speed * cos(alf_[player.dir1])
        player.y -= player.speed * sin(alf_[player.dir1])

        # check if player changes room
        for dir in current_room.exits():
            exit_ = current_room.exit(dir)
            prev_room = current_room
            if isinstance(exit_, Exit) and Point(player.x, player.y).within(exit_.a.poly) and exit_.a.active:                
                current_room = exit_.room
                rev_direction = current_room.rev_direction(dir)
                if current_room.exit(rev_direction).point:
                    start = current_room.exit(rev_direction).point
                elif current_room.exit(rev_direction).trans:
                    trans = current_room.exit(rev_direction).trans
                    start = Point(player.x + trans[0], player.y + trans[1])
                player.x, player.y = start.x, start.y
                player.scale = current_room.scale

        # Collision detection
        stop = False
        for a in current_room.included:
            if a.active and not Point(player.x, player.y).within(a.poly):
                stop = True
        for a in current_room.excluded:
            if  a.active and Point(player.x, player.y).within(a.poly):
                stop = True 
        if stop:
            player.x, player.y = x0, y0
            player.image = player.images[0]

        # set layer of player
        last_layer = len(current_room.layers) - 1
        player.layer = last_layer
        for i in range(last_layer,-1,-1):
            layer = current_room.layers[i]
            if layer.poly and Point(player.x, player.y).within(layer.poly):
                player.layer = i - 1

        player.animate()
    else:
        player.image = player.images[0]

def on_key_down(key, unicode, mod):
    global message, command

    if len(str(key)) == 6:
        command = command + str(key)[5]
    elif key == keys.SPACE:
        command = command + ' '
    elif key == keys.BACKSPACE:
        command = command[:len(command)-1]           
    elif key == keys.RETURN:
        _handle_command(command[2:])
        message = get_message()
        command = '> '

@when("open door")
def open_door():
    global town_a3

    if current_room == town_a3:
        say("""You open the door! 
        Go into the church.
        And pray to the Lord for many whales...""")
        town_a3.layers[len(town_a3.layers)-1].image = 'chapel_door2'
        town_a3.entry1.a.active = True
        for a in town_a3.excluded:
            if a.tag == "door_closed": a.active = False
            if a.tag == "door_open": a.active = True
    else:
        say("I don't see door in this area")
    # pprint(vars(town_a3.excluded[1]))

@when("close door")
def open_door():
    global town_a3

    if current_room == town_a3:    
        say("""You close the door! 
        """)
        town_a3.layers[len(town_a3.layers)-1].image = 'chapel_door1'
        town_a3.entry1.a.active = False
        for a in town_a3.excluded:
            if a.tag == "door_closed": a.active = True
            if a.tag == "door_open": a.active = False    
    else:
        say("I don't see door in this area")


# initiate adventure lib
start()

# initiate pgzero
pgzrun.go()