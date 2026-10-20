"""Original, human-scale, component-modelled furniture; not asset stand-ins.
Functions use model_lib scope origin/angle. All important shapes are mesh geometry.
"""
import math
import model_lib as g

def plant(name,x,y,z=0,size=1):
 g.lathe(name+'_POT',(x,y,z),[(.13*size,0),(.20*size,.30*size),(.21*size,.33*size),(.18*size,.34*size),(.16*size,.28*size)],'Terracotta',20)
 g.cylinder(name+'_SOIL',(x,y,z+.30*size),.17*size,.025,'Soil')
 for i in range(7):
  a=i*2.4;xx=x+math.cos(a)*.25*size;yy=y+math.sin(a)*.25*size;zz=z+(.62+(i%3)*.14)*size
  g.rod(name+'_STEM',(x,y,z+.3*size),(xx,yy,zz),.009*size,'Leaf',6);o=g.sphere(name+'_LEAF',(xx,yy,zz),(.24*size,.13*size,.41*size),'Leaf',12,8);o.rotation_euler.y=.35*math.cos(a)

def chair(name,x=0,y=0,angle=0,mat='OliveFabric'):
 # arm-free upholstered chair, four taper-looking legs, curved back with side stiles
 with g.scope(origin=g.ORIGIN+__import__('mathutils').Vector((math.cos(g.ANGLE)*x-math.sin(g.ANGLE)*y,math.sin(g.ANGLE)*x+math.cos(g.ANGLE)*y,0)),angle=g.ANGLE+angle):
  for xx in [-.19,.19]:
   for yy in [-.19,.19]:g.rod(name+'_LEG',(xx*1.12,yy*1.1,.04),(xx,yy,.43),.024,'Oak',10)
  g.box(name+'_SEAT_FRAME',(0,0,.43),(.48,.48,.065),'Oak',.025);g.box(name+'_SEAT_CUSHION',(0,-.01,.49),(.46,.46,.11),mat,.055)
  for xx in [-.205,.205]:g.rod(name+'_BACK_STILE',(xx,.19,.43),(xx,.19,.92),.023,'Oak')
  g.box(name+'_BACK',(0,.19,.79),(.46,.08,.30),mat,.045)

def sofa(name,x,y,width=2.35,angle=0,mat='Upholstery'):
 # Use nesting offset without changing floor elevation.
 o=g.ORIGIN.copy();a=g.ANGLE;xx=o.x+math.cos(a)*x-math.sin(a)*y;yy=o.y+math.sin(a)*x+math.cos(a)*y
 with g.scope(origin=(xx,yy,o.z),angle=a+angle,fixture='sofa'):
  for q in [-width/2+.2,width/2-.2]:
   for yy in [-.30,.30]:g.box(name+'_FOOT',(q,yy,.13),(.065,.065,.2),'Walnut',.015)
  g.box(name+'_BASE',(0,0,.30),(width,.86,.24),mat,.09)
  for q in [-width/2+.11,width/2-.11]:g.box(name+'_ARM',(q,0,.58),(.22,.9,.50),mat,.09)
  for k in range(3):
   q=(k-1)*(width-.48)/3;w=(width-.48)/3-.02
   g.box(name+'_SEAT',(q,-.07,.49),(w,.68,.19),mat,.075);g.box(name+'_BACK',(q,.31,.78),(w,.20,.59),mat,.085)
  for q in [-width*.28,width*.28]:
   p=g.box(name+'_PILLOW',(q,.1,.76),(.38,.16,.38),'Linen',.10);p.rotation_euler.y=.14*(1 if q>0 else -1)

def table(name,x,y,width=1.6,depth=.85,height=.76,mat='Oak'):
 with g.scope(fixture='dining_table'):
  g.box(name+'_TOP',(x,y,height),(width,depth,.07),mat,.045)
  for dx in [-width/2+.12,width/2-.12]:
   for dy in [-depth/2+.12,depth/2-.12]:g.rod(name+'_LEG',(x+dx,y+dy,.05),(x+dx*.95,y+dy*.95,height-.04),.035,'Oak')

def dining(name,x,y):
 table(name,x,y)
 for dx in [-.48,.48]:
  chair(name+'_CHAIR',x+dx,y+.72,0);chair(name+'_CHAIR',x+dx,y-.72,math.pi)
 for dx in [-.48,.48]:
  for dy in [-.22,.22]:
   g.cylinder(name+'_PLATE',(x+dx,y+dy,.81),.13,.018,'Porcelain',24);g.lathe(name+'_CUP',(x+dx+.17,y+dy,.81),[(.045,0),(.05,.10),(.04,.102),(.035,.02)],'Porcelain',16)
 g.lathe(name+'_VASE',(x,y,.81),[(.08,0),(.12,.12),(.05,.24),(.048,.28)],'Terracotta',20)
 for k in range(3):g.rod(name+'_FLOWER_STEM',(x,y,.9),(x+.1*math.sin(k),y+.08*math.cos(k),1.24),.006,'Leaf',6);g.sphere(name+'_FLOWER',(x+.1*math.sin(k),y+.08*math.cos(k),1.24),(.09,.09,.07),'Linen',10,6)

def bookcase(name,x,y,width=1.5,height=2.0):
 with g.scope(fixture='storage'):
  for xx in [-width/2,width/2]:g.box(name+'_SIDE',(x+xx,y,height/2),(.06,.32,height),'Oak',.012)
  for k in range(5):
   z=.12+k*(height-.2)/4;g.box(name+'_SHELF',(x,y,z),(width,.34,.045),'Oak',.009)
   if k<4:
    for j in range(7):g.box(name+'_BOOK',(x-width/2+.13+j*(width-.25)/7,y-.015,z+.15),(.065,.23,.22+(j%3)*.035),['Terracotta','Teal','Paper','OliveFabric'][j%4],.008)

def wardrobe(name,x,y,width=1.8,angle=0):
 o=g.ORIGIN.copy();a=g.ANGLE
 with g.scope(origin=(o.x+math.cos(a)*x-math.sin(a)*y,o.y+math.sin(a)*x+math.cos(a)*y,o.z),angle=a+angle,fixture='storage'):
  g.box(name+'_CARCASS',(0,0,1.12),(width,.56,2.2),'Oak',.025)
  for k in [-1,1]:
   g.box(name+'_PANEL',(k*width/4,-.292,1.12),(width/2-.035,.025,2.12),'Linen',.01);g.rod(name+'_HANDLE',(k*.10,-.325,1.00),(k*.10,-.325,1.35),.014,'Bronze')

def bed(name,x,y,angle=0,width=1.6):
 o=g.ORIGIN.copy();a=g.ANGLE
 with g.scope(origin=(o.x+math.cos(a)*x-math.sin(a)*y,o.y+math.sin(a)*x+math.cos(a)*y,o.z),angle=a+angle,fixture='bed'):
  for xx in [-width/2+.12,width/2-.12]:
   for yy in [-.85,.85]:g.box(name+'_FOOT',(xx,yy,.14),(.08,.08,.2),'Walnut',.02)
  g.box(name+'_FRAME',(0,0,.29),(width+.12,2.12,.27),'Oak',.065);g.box(name+'_MATTRESS',(0,0,.49),(width,2,.24),'Linen',.11)
  g.box(name+'_HEADBOARD',(0,1.055,.66),(width+.25,.10,1.15),'OliveFabric',.06)
  g.box(name+'_DUVET',(0,-.24,.64),(width+.03,1.51,.16),'Linen',.09)
  g.box(name+'_THROW',(0,-.65,.733),(width+.06,.46,.03),'Upholstery',.025)
  for xx in [-width*.25,width*.25]:g.box(name+'_PILLOW',(xx,.66,.68),(width*.43,.50,.17),'Linen',.075)
  for xx in [-width/2-.43,width/2+.43]:
   g.box(name+'_NIGHTSTAND',(xx,.76,.27),(.48,.42,.45),'Oak',.025);g.box(name+'_DRAWER',(xx,.535,.31),(.42,.025,.16),'Walnut',.01);g.cylinder(name+'_LAMP_BASE',(xx,.78,.52),.105,.025,'Bronze')
   g.rod(name+'_LAMP_STEM',(xx,.78,.54),(xx,.78,.80),.012,'Bronze');g.lathe(name+'_SHADE',(xx,.78,.75),[(.15,0),(.10,.21),(.09,.21),(.14,0)],'Linen',24)

def faucet(name,x,y,z):
 g.rod(name+'_TAP',(x,y,z),(x,y,z+.24),.016,'Steel');g.rod(name+'_SPOUT',(x,y,z+.24),(x,y-.15,z+.24),.016,'Steel');g.rod(name+'_SPOUT_END',(x,y-.15,z+.24),(x,y-.15,z+.20),.018,'Steel');g.rod(name+'_LEVER',(x+.06,y,z+.08),(x+.06,y,z+.20),.011,'Steel')
def kitchen(name,x,y,modules=5):
 # Back is +Y. 600 mm modular cabinetry; integrated sink, induction hob, oven, dishwasher, fridge.
 with g.scope(fixture='kitchen'):
  for k in range(modules):
   xx=x+k*.6
   g.box(name+'_PLINTH',(xx,y,.10),(.55,.50,.15),'Black',.01);g.box(name+'_BASE',(xx,y,.48),(.59,.59,.74),'Teal',.015)
   if k==2:
    g.box(name+'_OVEN_GLASS',(xx,y-.31,.49),(.52,.025,.48),'Black',.015);g.box(name+'_OVEN_TRIM',(xx,y-.33,.77),(.54,.03,.08),'Steel');g.rod(name+'_OVEN_HANDLE',(xx-.21,y-.36,.69),(xx+.21,y-.36,.69),.016,'Steel')
    for dx in [-.16,0,.16]:g.sphere(name+'_OVEN_DIAL',(xx+dx,y-.35,.77),(.035,.025,.035),'Steel',10,6)
   elif k==3:
    g.box(name+'_DISHWASHER_DOOR',(xx,y-.315,.47),(.54,.03,.62),'Steel',.015)
    g.box(name+'_DISHWASHER_CONTROL',(xx,y-.335,.80),(.54,.025,.06),'Black',.005)
    g.rod(name+'_DISHWASHER_PULL',(xx-.18,y-.36,.70),(xx+.18,y-.36,.70),.012,'Bronze')
    for dx in [-.18,-.10,.14]:g.sphere(name+'_DISHWASHER_BUTTON',(xx+dx,y-.353,.80),(.025,.016,.025),'Steel',8,6)
   else:
    for zz in [.37,.68]:g.box(name+'_DRAWER',(xx,y-.31,zz),(.54,.024,.25),'Oak',.009);g.rod(name+'_PULL',(xx-.15,y-.34,zz+.07),(xx+.15,y-.34,zz+.07),.009,'Bronze')
   # Worktop split around sink opening rather than covering its bowl.
   if k==0:
    for dx in [-.235,.235]:g.box(name+'_SINK_RIM_TOP',(xx+dx,y,.885),(.13,.65,.045),'Terrazzo',.005)
    for dy in [-.245,.245]:g.box(name+'_SINK_RIM_TOP',(xx,y+dy,.885),(.35,.16,.045),'Terrazzo',.005)
    bowl=g.lathe(name+'_SINK_BOWL',(xx,y,.70),[(.03,0),(.14,.01),(.20,.17),(.22,.18),(.20,.19),(.18,.17),(.12,.03),(.02,.025)],'Steel',24);bowl.scale.x=.8;faucet(name,xx,y+.21,.91)
   else:g.box(name+'_WORKTOP',(xx,y,.885),(.60,.65,.045),'Terrazzo',.008)
   g.box(name+'_BACKSPLASH',(xx,y+.315,1.13),(.6,.025,.44),'Tile',.005)
   if k<modules-1:
    g.box(name+'_UPPER',(xx,y+.11,1.94),(.58,.34,.70),'Linen',.015);g.box(name+'_UPPER_FRONT',(xx,y-.07,1.94),(.54,.025,.65),'Oak',.008)
    g.rod(name+'_UPPER_HANDLE',(xx-.14,y-.09,1.71),(xx+.14,y-.09,1.71),.009,'Bronze')
  xx=x+1.2
  g.box(name+'_HOOD',(xx,y+.02,1.53),(.56,.39,.08),'Steel',.012)
  for k in range(5):g.box(name+'_HOOD_FILTER',(xx-.2+k*.1,y-.02,1.485),(.035,.26,.007),'Black')
  g.box(name+'_HOOD_LIGHT',(xx,y-.14,1.48),(.37,.018,.008),'Glow')
  g.box(name+'_INDUCTION',(xx,y,.917),(.54,.49,.014),'Black',.01)
  for dx in [-.13,.13]:
   for dy in [-.12,.12]:g.torus(name+'_HOB_RING',(xx+dx,y+dy,.928),.085,.004,'Steel')
  g.lathe(name+'_SAUCEPAN',(xx-.13,y-.12,.93),[(.07,0),(.08,.10),(.075,.105),(.065,.02)],'Steel',20);g.rod(name+'_PAN_HANDLE',(xx-.20,y-.12,1.01),(xx-.40,y-.12,1.01),.02,'Black')
  # Refrigerator separate tall appliance, not an unarticulated box.
  xx=x+modules*.6;g.box(name+'_FRIDGE_CARCASS',(xx,y,1.11),(.66,.67,2.17),'Steel',.035)
  for zz,hh in [(.52,.75),(1.57,1.27)]:g.box(name+'_FRIDGE_DOOR',(xx,y-.35,zz),(.62,.055,hh),'Linen',.025)
  g.rod(name+'_FRIDGE_PULL',(xx-.23,y-.40,1.2),(xx-.23,y-.40,1.7),.018,'Steel')
  # Small but modeled counter accessories.
  g.box(name+'_CUTTING_BOARD',(x+2.4,y-.10,.925),(.37,.25,.025),'Oak',.035);g.lathe(name+'_CARAFE',(x+1.8,y,.91),[(.05,0),(.08,.05),(.07,.22),(.04,.26)],'Glass',20)

def _at(x,y,angle=0):
 o=g.ORIGIN.copy();a=g.ANGLE
 return g.scope(origin=(o.x+math.cos(a)*x-math.sin(a)*y,o.y+math.sin(a)*x+math.cos(a)*y,o.z),angle=a+angle,fixture='bathroom')

def vanity(name,px,py,angle=0):
 with _at(px,py,angle):
  x=y=0
  g.box(name+'_VANITY',(x,y,.47),(1.12,.58,.70),'Oak',.035)
  for q in [-.27,.27]:g.box(name+'_VANITY_DOOR',(x+q,y+.305,.48),(.51,.026,.61),'Teal',.012);g.sphere(name+'_KNOB',(x+q-.15,y+.33,.61),(.035,.035,.035),'Bronze',10,6)
  g.box(name+'_VANITY_TOP',(x,y,.85),(1.17,.62,.05),'Terrazzo',.012)
  g.lathe(name+'_BASIN',(x,y+.03,.88),[(.09,0),(.16,.025),(.23,.16),(.24,.18),(.22,.185),(.20,.15),(.12,.04),(.035,.035)],'Porcelain',28)
  
  o=g.ORIGIN.copy();a=g.ANGLE
  with g.scope(origin=(o.x+math.cos(a)*x-math.sin(a)*(y-.2),o.y+math.sin(a)*x+math.cos(a)*(y-.2),o.z),angle=a+math.pi):faucet(name,0,0,.89)
  g.box(name+'_MIRROR_FRAME',(x,y-.28,1.57),(1.02,.04,.93),'Bronze',.04);g.box(name+'_MIRROR',(x,y-.25,1.57),(.93,.015,.84),'Steel',.03)
  g.box(name+'_MIRROR_LIGHT',(x,y-.18,2.08),(.80,.10,.04),'Glow',.015)

def toilet(name,px,py,angle=0):
 with _at(px,py,angle):
  x=y=0
  g.lathe(name+'_WC_PEDESTAL',(x,y-.12,.06),[(.15,0),(.17,.12),(.13,.3)],'Porcelain',24)
  bowl=g.lathe(name+'_WC_BOWL',(x,y-.12,.25),[(.12,0),(.2,.04),(.27,.15),(.28,.18),(.24,.19),(.20,.14),(.11,.05),(.01,.05)],'Porcelain',28);bowl.scale.x=.82;bowl.scale.y=1.2
  seat=g.torus(name+'_WC_SEAT',(x,y-.12,.45),.255,.025,'Porcelain');seat.scale.x=.85;seat.scale.y=1.2
  g.box(name+'_WC_TANK',(x,y+.20,.65),(.46,.20,.49),'Porcelain',.07);g.box(name+'_WC_LID',(x,y+.20,.91),(.48,.23,.04),'Porcelain',.025);g.cylinder(name+'_WC_FLUSH',(x+.12,y+.20,.94),.025,.015,'Steel')

def shower(name,px,py,angle=0):
 with _at(px,py,angle):
  x=y=0
  g.box(name+'_SHOWER_TRAY',(x,y,.09),(1.15,1.15,.10),'Porcelain',.035)
  for xx in [x-.58,x+.58]:g.box(name+'_SHOWER_GLASS',(xx,y,1.06),(.014,1.15,1.90),'Glass');g.rod(name+'_SHOWER_POST',(xx,y+.56,.14),(xx,y+.56,2.04),.014,'Steel')
  g.box(name+'_SHOWER_FRONT',(x+.30,y-.58,1.06),(.56,.014,1.90),'Glass');g.rod(name+'_SHOWER_HANDLE',(x+.08,y-.60,.95),(x+.08,y-.60,1.25),.016,'Steel')
  g.rod(name+'_SHOWER_PIPE',(x,y+.48,.98),(x,y+.48,2.03),.018,'Steel');g.rod(name+'_SHOWER_ARM',(x,y+.48,2.03),(x,y+.15,2.03),.018,'Steel');g.cylinder(name+'_SHOWER_HEAD',(x,y+.15,2.00),.12,.035,'Steel')
  g.cylinder(name+'_DRAIN',(x,y,.147),.05,.01,'Steel')

def bathroom(name,x0,y0,w,d):
 with g.scope(fixture='bathroom'):
  if d>4:
   # North entry: keep its landing clear; stagger fixtures down the long room.
   vanity(name,x0+w-.38,y0+d-1.35,math.pi/2)
   toilet(name,x0+.42,y0+2.35,math.pi/2)
   shower(name,x0+w-.68,y0+.68,math.pi)
  else:
   vanity(name,x0+w-.8,y0+.40)
   toilet(name,x0+.65,y0+d-.65)
   shower(name,x0+w-.68,y0+d-.68)
  g.box(name+'_BATHMAT',(x0+w/2,y0+d/2,.06),(.85,.55,.025),'Linen',.04)
  g.rod(name+'_TOWEL_RAIL',(x0+.25,y0+.20,1.15),(x0+.25,y0+.85,1.15),.015,'Bronze');g.box(name+'_TOWEL',(x0+.27,y0+.52,.94),(.025,.49,.45),'Linen',.015)
