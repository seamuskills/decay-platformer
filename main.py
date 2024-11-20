import pygame, pygame_menu, colorsys

pygame.init() #initiate pygame
sc = pygame.display.set_mode((512,256)) #set display to 512x256 pixels (good on repl.it but bad for normal displays)

font = pygame.font.SysFont("freemono",16,bold=True) #set up a font for debug text and the check/x mark in the menu
debug = False #whether debug info is enabled
playercolor = (255,255,255) #current player color (r,g,b)
camx = 0 #camera x and y
camy = 0
pstart = (0,0) #what coord the player goes to if they die.
difficulty = 1 #the difficulty of the game

level = 0 #what level are we on

levels = [ #level data, # means a wall, G means a goal, B means a blob and P is where the player starts, I use - for empty space but any character except #,G,B,or P would work
	[
		"-------------------####",
		"-P---------------####G------B",
		"#####----####--#########--#######"
	],
	[
		"--------B",
		"-------######",
		"",
		"",
		"-#####",
		"",
		"-------#####-----###---#####------###-----#",
		"P----#######--B--############-B--####----##-------G",
		"###################################################"
	],
	[
		"----------########----###----#######---#######-----",
		"----P----####B-------############B------####B---G-B",
		"###################################################"
	],
	[
		"-B------######",
		"###",
		"",
		"-----------------------B",
		"--------#####---------#####-------#####-----###",
		"-P",
		"###-----------------------------------------------G"
	],
	[
		"-----------------------------------###",
		"-P-----###-----------B-----###-------------GB",
		"###------#####-----#####-----------------#######"
	],
	[
		"-----------------#####",
		"-----####--------------------B",
		"----------------------B------####",
		"-------------------######",
		"--P----------------------------G",
		"####------------------------#####"
	],
	[
		"why are you looking at------B",
		"the code... just play---#####",
		"the game--------------------------G",
		"---------------------------------###",
		"-P--------####--------B",
		"###-----------------#####"
	],
	[
		"PBBBBB-BB----BBBB---BBB------BBB-BBB-----BBG",
		"######-##----####---###------###-###-----###"
	],
	[
		"###  #  # #    #",
		"-#---#--#--#--#",
		"-#---####---##",
		"-#---#--#--#--#",
		"-#---#--#-#----#    thanks for playing ;)",
		"",
		"#PBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBG#",
		"#################################################"
	]
]

menuTheme = pygame_menu.themes.THEME_DARK.copy() #making the "theme" for the menu that decides how it is styled
menuTheme.title_background_color = (51,51,51) #Title bar color
menuTheme.background_color = (34,34,34) #background color 
menuTheme.widget_font = pygame_menu.font.FONT_MUNRO #what font the buttons use
menuTheme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_TITLE_ONLY_DIAGONAL #the style of the bar where the title resides
menuTheme.title_font = pygame_menu.font.FONT_MUNRO #font for the title
menuTheme.widget_selection_effect = pygame_menu.widgets.LeftArrowSelection() #what it looks like to have something selected

def sign(x): #return the sign of a number (1, 0, or -1)
	if x>0: return 1 #if above 0 return 1
	if x<0: return -1 #if below 0 return -1
	return 0 #if 0 return 0

pauseMenu = pygame_menu.Menu("Paused",512,256,theme=menuTheme) #pause menu
c = pauseMenu.get_clock() #use this clock so deltatime works correctly when unpausing the game
optionsMenu = pygame_menu.Menu("Options",512,256, theme=menuTheme) #menu for options
changeLevelMenu = pygame_menu.Menu("Level Select",512,256,theme=menuTheme) #menu for changeing level
endMenu = pygame_menu.Menu("GG!",512,256,theme=menuTheme)

def kill(): #kill the game
	pygame.quit()
	exit()

def toggleDebug(x): #toggle debug text
	global debug
	debug = x

def gotoOptions(): #goto options menu
	optionsMenu.enable()
	optionsMenu.mainloop(sc)

def changeColor(color,cursor_ms_counter): #change player color, no idea why cursor_ms_counter is passed to this function but if I don't include it than it raises an exception.
	if color != (-1,-1,-1): #if the color is valid
		global playercolor
		playercolor = color

def changeDif(x,value): #change difficulty
	global difficulty
	difficulty = value

def gotochangeLevelMenu(): #go to changelevel menu
	changeLevelMenu.enable()
	changeLevelMenu.mainloop(sc)

def changeLevel(x, l): #change level
	global level
	level = l
	p.die()

def restart():
	changeLevel("dummytext",0)
	endMenu.disable()

pauseButtons = [
	pauseMenu.add.button("resume",pauseMenu.disable), #disable menu button
	pauseMenu.add.button("options",gotoOptions), #go to options menu
	pauseMenu.add.button("level select",gotochangeLevelMenu), #go to level select
	pauseMenu.add.button("quit",kill) #quit game
]
optionsButtons = [
	optionsMenu.add.toggle_switch("debug info",onchange=toggleDebug,width=60,state_text=("╳","√"),state_text_font=font,state_color=((100,100,255),(255,165,0)),state_text_font_color=((0,0,0),(0,0,0))), #toggle debug info
	optionsMenu.add.color_input("player color: ",color_type="hex",onchange=changeColor,default="#ffffff",input_underline="."), #change player color
	optionsMenu.add.selector(title="difficulty",items=[("easy",0.5),("normal",1),("hard",1.4)],default = 1,onchange=changeDif,style=pygame_menu.widgets.SELECTOR_STYLE_FANCY,font_color=(0,0,0)), #difficulty dropdown menu
	optionsMenu.add.button("back",optionsMenu.disable) #exit Options
]
levelOptions = [("level "+str(i),i) for i in range(len(levels))] #set up the list to be used as an argument in buttons

changeLevelButtons = [
	changeLevelMenu.add.selector("level: ",items=levelOptions,onchange=changeLevel,style=pygame_menu.widgets.SELECTOR_STYLE_FANCY,font_color=(0,0,0)), #select the levels
	changeLevelMenu.add.button("back",changeLevelMenu.disable) #exit this menu
]
endButtons = [
	endMenu.add.label("Thanks for playing!"),
	endMenu.add.button("restart",restart)
]

def approach(x,y,amm): #go from x to y by amm without overshooting y
	if x<y:
		x+= amm
		x = min(x,y)
	elif x>y:
		x-=amm
		x = max(x,y)
	return x

dt = 0 #deltatime measures how long the last gameloop (frame) took, on average it is 16
grav = 0.02 #gravity

walls = [] #list of all walls and blobs
blobs = []

class wall: #wall
	def __init__(self,x,y,w=16,h=16):
		self.x = x
		self.y = y
		self.h = h #width
		self.w = w #height
		walls.append(self) #add self to list

	def rect(self):
		return (self.x,self.y,self.w,self.h) #rect function, returns the rect of the wall or other object.

	def draw(self):
		pygame.draw.rect(sc,(34,34,34),(self.x-camx,self.y-camy,self.w,self.h)) #draw this wall

class Blob: #the blobs which gets you size and which you must collect to activate the goal
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.w = 8 #width
		self.h = 8 #height
		blobs.append(self) #add self to the list
	
	def draw(self):
		global playercolor
		pygame.draw.rect(sc,playercolor,(self.x-camx,self.y-camy,self.w,self.h)) #draw self using playercolor

class Goal: #the goal
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.w = 16 #width
		self.h = 16 #height
		self.color = [1,1,1] #current color (h,s,v)
	
	def draw(self):
		if blobs == []: #if there are no blobs
			self.color[0] = (self.color[0]+0.0025) #incerment hue
			color = list(colorsys.hsv_to_rgb(self.color[0],	self.color[1],self.color[2])) #convert it to rgb
			color = [i*255 for i in color] #multiply the values by 255 so pygame can use it correctly
			pygame.draw.rect(sc,color,(self.x-camx,self.y-camy,	self.w,self.h)) #draw self using that color
		else:
			pygame.draw.rect(sc,(0,0,0),(self.x-camx,self.y-camy,self.w,self.h)) #draw self as black (inactive)

g = Goal(200,200) #set up the goal (1 per level)

class player: #player
	def __init__(self):
		self.x = 0
		self.y = 0
		self.w = 16 #width
		self.h = 16 #height
		self.hsp = 0 #horizontal speed
		self.vsp = 0 #vertical speed
		self.walksp = 0.2 #max walk speed
		self.acc = 0.01 #acceleration toward walk speed
		self.jumpForce = 0.4
		self.falltimer = 120 #how long you can be off the ground before dying
		self.jumped = False #have you jumped already? (for kyote jumping)
	
	def update(self):
		global camx, camy #camera x and y
		camx = approach(camx,self.x-128,abs((self.x-128)-camx)/16) #move camx toward x
		camy = self.y-150 #snap cam y at y
		keys = pygame.key.get_pressed() #getkeys
		move = keys[pygame.K_d]-keys[pygame.K_a] #get input (right-left always returns positive for right negetive for left and 0 for neither and both)

		self.grounded = pygame.Rect(self.x,self.y+1,self.w,self.h).collidelist([i.rect() for i in walls]) != -1 #get if we are on the ground

		self.vsp += grav*(not self.grounded) #if not grounded than add gravity to our vsp
		
		if not self.grounded: #if we are not grounded
			self.falltimer -= 1 #fall timer goes down
			if self.falltimer < 0: #if its 0 or less
				self.die() #die
		else:
			self.jumped = False# if grounded you havent jumped
			self.falltimer = 120 #reset fall timer

		if (self.grounded or self.falltimer > 110) and keys[pygame.K_w] and not self.jumped: #if grounded or falling for < 10 ticks (kyote time) and havent jumped already.
			self.vsp = self.jumpForce*-1 #set vsp 
			self.jumped = True #you jumped
			self.w -= 2*difficulty #subtract from size based on difficulty
			self.h -= 2*difficulty

		if self.grounded: #if on ground
			self.hsp = approach(self.hsp,move*self.walksp,self.acc) #accelerate toward where we wanna move
		else:
			self.hsp = approach(self.hsp,move*self.walksp,self.acc/2) #accelerate at half acceleration

		if pygame.Rect(self.x+self.hsp*dt,self.y,self.w,self.h).collidelist([i.rect() for i in walls]) != -1: #if I will collide with a wall
			while pygame.Rect(self.x+sign(self.hsp),self.y,self.w,self.h).collidelist([i.rect() for i in walls]) == -1: #while im not 1 pixel away
				self.x += sign(self.hsp) #go one pixel toward it
			self.hsp = 0 #reset speed
		self.x += self.hsp*dt #move x by speed * deltatime making it fps independant
		if self.grounded: # if on the ground
			self.w -= abs(self.hsp) #subtract size by speed
			self.h -= abs(self.hsp)
		if self.w < 1:
			self.die() #if size < 1 than die

		if pygame.Rect(self.x,self.y+self.vsp*dt,self.w,self.h).collidelist([i.rect() for i in walls]) != -1: #if im going to hit a wall
			while pygame.Rect(self.x,self.y+sign(self.vsp),self.w,self.h).collidelist([i.rect() for i in walls]) == -1: #while im not 1 pixel away
				self.y += sign(self.vsp) #go to the wall by a pixel
			self.vsp = 0 #reset speed
		self.y += self.vsp*dt #move by speed * deltatime

		if pygame.Rect(self.x,self.y,self.w,self.h).collidelist([wall.rect(i) for i in blobs]) != -1: # if touching a blob
			self.y -= (17-self.w) #go up so you dont get stuck
			self.w, self.h = 16,16 #reset size
			blobs.remove(blobs[pygame.Rect(self.x,self.y,self.w,self.h).collidelist([wall.rect(i) for i in blobs])]) #remove that blob
		
		if pygame.Rect(self.x,self.y,self.w,self.h) .colliderect((g.x,g.y,g.w,g.h)) and blobs == []: #if touching goal and no blobs
			global level #incerment level and die
			level += 1
			if level == 9:
				endMenu.enable()
				endMenu.mainloop(sc)
			else:
				self.die()

	def die(self): #die
		load_level(levels[level]) #reload the level
		self.w, self.h = 16,16 #reset size
		self.x, self.y = pstart #goto pstart
		self.hsp,self.vsp = 0,0 #reset speed
		self.falltimer = 120 #reset falltimer (or you just die again)

	def draw(self):
		global playercolor
		pygame.draw.rect(sc,playercolor,(self.x-camx,self.y-camy,self.w,self.h)) #draw self using playercolor

def load_level(level_data): #load level
	global pstart, walls, blobs
	Len = 0 #len of the wall
	blobs = [] #reset blobs
	walls = [] #reset walls
	for i,y in enumerate(level_data): #for all the strings
		for h,x in enumerate(level_data[i]): #for all the chars in that string
			if level_data[i][h] == "#": #if its a wall
				try: #failsafe for walls on the edge of leveldata
					if level_data[i][h+1] == "#": #if next to a wall
						Len += 1 #incerment length
					else:
						Len += 1 #incerment length by 1 again
						wall(h*16-(Len*16)+16,i*16,Len*16) #make a wall of that length
						Len = 0 #reset length
				except IndexError:
					Len += 1 #same but in the failsafe
					wall(h*16-(Len*16)+16,i*16,Len*16)
					Len = 0
			if level_data[i][h] == "B": #blobs
				Blob(h*16+4,i*16+8)
			if level_data[i][h] == "P": #player start
				pstart = (h*16, i*16)
			if level_data[i][h] == "G": #goal
				global g
				g = Goal(h*16,i*16)

load_level(levels[0]) #load the first level

p = player() #set up the player

debug_text = {"fps":"c.get_fps()","x":"round(p.x,2)","y":"round(p.y,2)","dt":"dt","hsp":"round(p.hsp,2)","vsp":"round(p.vsp,2)","size":"p.w"} #dict of debug text {name:variable}

while True: #mainloop
	for event in pygame.event.get(): #go through all the events
		if event.type == pygame.QUIT:
			kill() #kill if the event is quit (x button pressed)
		if event.type == pygame.KEYDOWN: #if keydown
			if event.key == 27: #if it is escape
				pauseMenu.enable() #enable pause menu
				pauseMenu.mainloop(sc) #pause menu mainloop

	sc.fill((16,16,16)) #clear screen

	p.draw() #draw and update player
	p.update()

	for i in walls: #draw walls
		i.draw()
	
	for i in blobs: #draw blobs
		i.draw()

	g.draw() #draw goal

	if debug: #draw debug text
		for i,(k,v) in enumerate(debug_text.items()):
			text = font.render(k+": "+str(eval(v)),True,(255,255,255))
			sc.blit(text,(0,i*16))

	pygame.display.flip() #update display
	dt = c.tick(60) #pace program and generate deltatime