import maya.cmds as cmds
import random


# deformer Klasse, welche mir deformern und modifiern arbeitet

class Deformer(object):
    def __init__(self):
        print("Deformer Object created")
        # user paramaters
        self.amount = 0
        self.minLength = 0
        self.maxLength = 0
        self.curvature_Up = 0
        self.curvature_Whole = 0
        self.random_rot = 0
        self.random_length = 0
        self.color = 0
        self.scale = 0
        self.arc = True
        self.speed = 0
        self.amplitude = 0
        # admin variables
        self.lashes = []
        self.bends = []
        self.lashesGroup = ""
        self.material = 0
        # save translate positions
        # for recreation of group
        self.expressionSet = False
        self.pos = [0,0,0]
        self.rot = [0,0,0]

    def getName(self):
        return "deformer"

    def createLashesTemplate(self, amount, minlength, maxlength, curvature_Up, curvature_Whole, random_rot, random_length, color, scale, *args):
        # parameter initialization
        self.amount = amount
        self.minLength = minlength
        self.maxLength = maxlength
        self.curvature_Up = curvature_Up
        self.curvature_Whole = curvature_Whole
        self.random_rot = random_rot
        self.random_length = random_length
        self.color = color
        self.scale = scale
        self.lashes = []
        self.bends = []
        self.expressionSet = False
        self.lashesGroup = cmds.group(em=True, name="lashesGroup")
        print("lashes created")
        distance = 1 / float(amount)
        radius = distance / 2
        for i in range(amount):
            # calculate position
            posX = distance * i
            # create lash
            new_object = self.createLash(i, posX, radius)
            self.createBendUp(new_object[0])
            # administrate lashes
            self.lashes.append(new_object)
            cmds.parent(new_object[0], self.lashesGroup)
        # center pivot point
        cmds.xform(self.lashesGroup, cp=True)
        self.createBendWhole()
        #apply colorshader
        self.material = cmds.shadingNode('lambert', asShader=True, n="lashesColor")
        cmds.sets(r=True,nss=True, em=True, n='lashesColorSG')
        cmds.connectAttr(self.material + '.outColor', 'lashesColorSG.surfaceShader', f=True)
        cmds.select(self.lashesGroup, add=False)
        cmds.sets(e=True, fe='lashesColorSG')
        cmds.move(self.pos[0], self.pos[1], self.pos[2], self.lashesGroup, absolute=True)
        cmds.rotate(self.rot[0], self.rot[1], self.rot[2], self.lashesGroup, absolute=True)
        #final adjustments
        self.adjustcolor(self.color)
        self.adjustlength(minlength, maxlength, random_length)
        self.adjustrandomRot(self.random_rot)
        self.adjustscale(self.scale)
        self.adjustbend_Up(curvature_Up)

    def createBendUp(self, animatedObject, *args):
        # select all lashes
        cmds.select(animatedObject, add=False)
        self.bendUp = cmds.nonLinear(type="bend", lowBound=0, highBound=2, curvature=self.curvature_Up, split=False)
        self.bends.append(self.bendUp)
        cmds.setAttr(self.bendUp[1] + ".visibility", 0)
        cmds.parent(self.bendUp, animatedObject)
        cmds.rotate(0, '90deg', 0, r=True)
        cmds.move(0, 0, 0)

    def createBendWhole(self, *args):
        # has to be called AFTER createBendUp,
        # due to the selection-method.
        # select all lashes
        for lash in self.lashes:
            cmds.select(self.lashesGroup+"|"+lash[0], add=True)
        self.bendWhole = cmds.nonLinear(type="bend", lowBound=-1, highBound=1, curvature=self.curvature_Whole, split=False)
        cmds.parent(self.bendWhole, self.lashesGroup)
        cmds.rotate('360deg', '180deg', '270deg', r=True)
        cmds.move(0.5, 0, 0)

    def createLash(self, nameSuff, posX, width, *args):
        if len(self.lashesGroup) == 11:
            name = "lash"
        else:
            name = "lash"+self.lashesGroup[11]+"ID"
        newObject = cmds.polyCone(name=name + str(nameSuff), sx=3, sy=5, sz=1, r=width, h=1)
        cmds.move(0, - 0.5, 0, newObject[0]+".scalePivot", newObject[0]+".rotatePivot", absolute=True)
        cmds.move(posX, 0.5, 0, newObject[0], absolute=True)
        return newObject

    def calculateRandomLength(self, pos, rand, *args):
        posNeg = random.random()
        rand_factor = random.random() * rand
        if posNeg > 0.5:
            rand_factor = -rand_factor
        if self.arc:
            length = self.maxLength - ((self.maxLength - self.minLength) / (min(self.amount - pos, pos + 1)))
            random_length = length * (1 + (rand_factor*0.1))
        else:
            length = self.minLength + (((self.maxLength - self.minLength) * pos) / self.amount)
            random_length = length * (1 + (rand_factor*0.1))
        return random_length

    def adjustcolor(self, color, *args):
        cmds.setAttr(self.material + '.color', type='float3', *color)
        self.color = color

    def adjustlength(self, minlength, maxlength, random_length, *args):
        print("adjustlength is called")
        self.minLength = minlength
        self.maxLength = maxlength
        self.random_length = random_length
        # set value of random and rotation to 0,
        # to ensure that the results of bounding_box are correct
        counter = 0
        for lash in self.lashes:
            new_length = self.calculateRandomLength(counter, random_length)
            # change length
            cmds.setAttr(lash[0]+".scaleY", new_length)
            cmds.setAttr(self.bends[counter][1]+".scaleX", new_length*0.5)
            cmds.setAttr(self.bends[counter][1]+".scaleZ", new_length*0.5)
            counter += 1

    def adjustbend_Whole(self, curvature, *args):
        cmds.nonLinear(self.bendWhole[0], e=True, curvature=curvature)
        self.curvature_Whole = curvature

    def adjustbend_Up(self, curvature, *args):
        self.curvature_Up = curvature
        self.adjustAnimation(self.speed, self.amplitude)

    def adjustscale(self, scale):
        cmds.scale(scale, scale, scale, self.lashesGroup, absolute=True)
        self.scale = scale

    def adjustrandomRot(self, random_parm, *args):
        pos = 0
        for lash in self.lashes:
            pos += 1
            # random.seed(pos)
            posNeg = random.random()
            rand_factor = random.random() * self.scale * float(random_parm)
            if posNeg > 0.5:
                rand_factor = -rand_factor
            # randomisation only on x and z axis because of aesthetic reasons
            cmds.rotate(rand_factor, 0, rand_factor, self.lashesGroup+"|"+lash[0], absolute=True)
        self.random_rot = random_parm

    def adjustDistribution(self, distribution, *args):
        if distribution == 1:
            self.arc = True
        else:
            self.arc = False
        self.adjustlength(self.minLength, self.maxLength, self.random_length)

    def adjustPoly(self, quality, *args):
        if quality == 1:
            for lash in self.lashes:
                cmds.polyCone(lash, edit=True, sx=3)
                cmds.polyCone(lash, edit=True, sy=5)
        elif quality == 2:
            for lash in self.lashes:
                cmds.polyCone(lash, edit=True, sx=5)
                cmds.polyCone(lash, edit=True, sy=10)
        else:
            for lash in self.lashes:
                cmds.polyCone(lash, edit=True, sx=10)
                cmds.polyCone(lash, edit=True, sy=30)

    def adjustSmoothness(self, smoothness, *args):
        self.selectall()
        if smoothness == 0:
            cmds.displaySmoothness( polygonObject=1 )
        else:
            cmds.displaySmoothness( polygonObject=3 )

    def adjustAnimation(self, speed, amplitude):
        self.speed = speed
        self.amplitude = amplitude
        if not self.expressionSet:
            for bend in self.bends:
                cmds.expression( s=bend[0]+'.curvature = ' + str(self.curvature_Up)+ '+(sin(time*' + str(speed)+')*'+str(amplitude)+')', n = "expression"+bend[0] )
            self.expressionSet = True
        else:
            for bend in self.bends:
                cmds.expression( "expression"+bend[0], edit = True, s=bend[0]+'.curvature = ' + str(self.curvature_Up)+ '+(sin(time*' + str(speed)+')*'+str(amplitude)+')' )

    def deleteLashes(self, *args):
        self.pos = cmds.xform(self.lashesGroup, q = True, ws = True, t = True)
        self.rot = cmds.xform(self.lashesGroup, q = True, ws = True, ro = True)
        cmds.delete(self.lashesGroup)
        cmds.delete(self.material)

    def selectall(self, *args):
        cmds.select(self.lashesGroup, add=False)
