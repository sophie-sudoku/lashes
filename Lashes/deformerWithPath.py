import maya.cmds as cmds
import random


# Deformer class:
# uses a bend-deformer to bend the lashes up
# and pathanimation for copying the lashes along the path

class Deformer(object):
    def __init__(self):
        print("Deformer Object along cutom path created")
        # user paramaters
        self.amount = 0
        self.minLength = 0
        self.maxLength = 0
        self.curvature = 0
        self.random_rot = 0
        self.random_length = 0
        self.color_parm = 0
        self.spacing = 0
        self.arc = True
        self.material = 0
        # admin varibles
        self.lashesPath = cmds.ls(selection=True)
        self.snapshotGroup = ""
        self.snapWrapGroup = ""
        self.groupAll = ""
        self.pathanim = ""
        self.lashTemp = ""
        self.bendUp = ""

    def getName(self):
        return "deformer"

    def reversePath(self, *args):
        cmds.reverseCurve(self.lashesPath[0])

    def createLashesTemplate(self, amount, minlength, maxlength, curvature, random_rot, random_length, color_parm, *args):
        self.amount = amount
        self.minLength = minlength
        self.maxLength = maxlength
        self.curvature = curvature
        self.random_rot = random_rot
        self.color_parm = color_parm
        self.random_length = random_length
        # create groups
        self.groupAll = cmds.group(em=True, name="lashesGroup")
        self.snapWrapGroup = cmds.group(em=True, name="wrapForSnapGroup")
        # CREATE LASH
        if len(self.groupAll) == 11:
            name = "lash"
        else:
            name = "lash"+self.groupAll[11]
        self.lashTemp = cmds.polyCone(name=name + str(1), sx=3, sy=5, sz=1, r= (cmds.arclen(self.lashesPath[0]) / float(amount) / 2), h=1)
        cmds.move(-0.5, self.lashTemp[0]+".scalePivot", self.lashTemp[0]+".rotatePivot", y = True, absolute=True)
        cmds.move(0.5, self.lashTemp[0], y=True, absolute=True)
        cmds.parent(self.lashTemp, self.snapWrapGroup)
        # curvature gets readjusted later
        self.createBendUp()
        # ANIMATE LASH ALONG PATH
        self.pathanim = cmds.pathAnimation(self.snapWrapGroup, stu=0, etu=amount, follow=True, fa='x', ua='y', iu=False, inverseFront=False, bank=False, wu=(0.0, 1.0, 0.0), wut="vector", fm=True, c=self.lashesPath[0])
        motionPath = [motionPath for motionPath in cmds.listHistory(self.snapWrapGroup) if motionPath.startswith('motionPath')][0]
        cmds.setAttr(motionPath+".frontTwist", 270)
        cmds.selectKey(motionPath+"_uValue", time=(0,amount), k=True)
        cmds.keyTangent(ott="linear", itt="linear", absolute=True)
        self.snapshotGroup = cmds.snapshot(self.snapWrapGroup, i=1, ch=1, st=1, et=amount, update="force")
        self.adjustlength(minlength, maxlength, random_length)
        # CLEAN UP ADMIN
        cmds.parent(self.snapWrapGroup, self.groupAll)
        cmds.parent(self.snapshotGroup, self.groupAll)
        #apply colorshader
        self.material = cmds.shadingNode('lambert', asShader=True, n="lashesColor")
        cmds.sets(r=True,nss=True, em=True, n='lashesColorSG')
        cmds.connectAttr(self.material + '.outColor', 'lashesColorSG.surfaceShader', f=True)
        cmds.select(self.groupAll, add=False)
        cmds.sets(e=True, fe='lashesColorSG')
        # final setup
        self.adjustcolor(self.color_parm)
        self.adjustrandomRot(self.random_rot)

    def createBendUp(self, *args):
        # select all lashes
        cmds.select(self.lashTemp)
        self.bendUp = cmds.nonLinear(type="bend", lowBound=0, highBound=2, curvature=self.curvature, split=False)
        cmds.rotate(0, '270deg', 0, r=True)
        cmds.move(0, -0.5, 0, relative=True)
        cmds.parent(self.bendUp, self.lashTemp)

    def adjustcolor(self, color_parm, *args):
        cmds.setAttr(self.material + '.color', type='float3', *color_parm)

    def adjustAmount(self, amount_parm, *args):
        increase = (amount_parm > self.amount)
        self.amount = amount_parm
        counter=0
        snapchildren = cmds.listRelatives(self.snapshotGroup[0], c=True)
        for lash in snapchildren:
            counter+=1
            if increase:
                if counter < amount_parm:
                    cmds.setAttr(lash+".visibility", 1)
            else:
                if counter > amount_parm:
                    cmds.setAttr(lash+".visibility", 0)
        coneName = [coneName for coneName in cmds.listHistory(self.lashTemp) if coneName.startswith('polyCone')][1]
        cmds.setAttr(coneName +'.radius', max(0.01, (cmds.arclen(self.lashesPath[0])-(self.spacing/self.amount)) / amount_parm / 2))
        cmds.pathAnimation(self.pathanim, edit=True, etu=amount_parm)
        cmds.snapshot(self.snapshotGroup, edit=True, et=amount_parm)
        self.adjustrandomRot(self.random_rot)
        # seems to be too slow for new lashes (works fine when amount is set to maximum once)
        self.adjustcolor(self.color_parm)
        self.adjustlength(self.minLength, self.maxLength, self.random_length)

    def adjustlength(self, minlength, maxlength, random_length, *args):
        self.minLength = minlength
        self.maxLength = maxlength
        self.random_length = random_length
        if random_length == 0:
            if self.arc:
                cmds.cutKey(self.lashTemp[0], attribute='scaleY', time = (0, self.amount), clear = True)
                cmds.setKeyframe(self.lashTemp[0], attribute='scaleY', t=0, v=minlength, itt="linear", ott="linear")
                cmds.setKeyframe(self.lashTemp[0], attribute='scaleY', t=(self.amount), v=minlength, itt="linear", ott="linear")
                cmds.setKeyframe(self.lashTemp[0], attribute='scaleY', t=(self.amount/2), v=maxlength, itt="spline", ott="spline")
            else:
                cmds.cutKey(self.lashTemp[0], attribute='scaleY', time = (0, self.amount), clear = True)
                cmds.setKeyframe(self.lashTemp[0], attribute='scaleY', t=0, v=minlength, itt="linear", ott="linear")
                cmds.setKeyframe(self.lashTemp[0], attribute='scaleY', t=(self.amount), v=maxlength, itt="linear", ott="linear")
        else:
            pos=0
            snapchildren = cmds.listRelatives(self.snapshotGroup[0], c=True)
            for lash in snapchildren:
                posNeg = random.random()
                rand_factor = random.random() * random_length
                if posNeg > 0.5:
                    rand_factor = -rand_factor
                new_length = self.calculaterandomLength(pos, rand_factor)
                pos+=1
                cmds.setKeyframe(self.lashTemp[0], attribute='scaleY', t=pos, v=new_length)
                if pos >= self.amount:
                    break
        # adjust size of bend deformer
        if self.arc:
            cmds.cutKey(self.bendUp[0] +'Handle', attribute='scaleX', time = (0, self.amount), clear = True)
            cmds.setKeyframe(self.bendUp[0]+'Handle', attribute='scaleX', t=0, v=minlength*cmds.getAttr(self.bendUp[0]+'Handle.scaleY'), itt="linear", ott="linear")
            cmds.setKeyframe(self.bendUp[0]+'Handle', attribute='scaleX', t=self.amount/2, v=maxlength*cmds.getAttr(self.bendUp[0]+'Handle.scaleY'), itt="spline", ott="spline")
            cmds.setKeyframe(self.bendUp[0]+'Handle', attribute='scaleX', t=self.amount, v=minlength*cmds.getAttr(self.bendUp[0]+'Handle.scaleY'), itt="linear", ott="linear")
        else:
            cmds.cutKey(self.bendUp[0] +'Handle', attribute='scaleX', time = (0, self.amount), clear = True)
            cmds.setKeyframe(self.bendUp[0]+'Handle', attribute='scaleX', t=0, v=minlength*cmds.getAttr(self.bendUp[0]+'Handle.scaleY'), itt="linear", ott="linear")
            cmds.setKeyframe(self.bendUp[0]+'Handle', attribute='scaleX', t=self.amount, v=maxlength*cmds.getAttr(self.bendUp[0]+'Handle.scaleY'), itt="linear", ott="linear")

    def calculaterandomLength(self, pos, rand_factor, *args):
        if self.arc:
            length = self.maxLength - ((self.maxLength - self.minLength) / (min(self.amount - pos, pos+1)))
            random_length = length * (1 + (rand_factor*0.1))
        else:
            length = self.minLength + (((self.maxLength-self.minLength)*pos)/self.amount)
            random_length = length * (1 + (rand_factor*0.1))
        return random_length

    def adjustbend_Up(self, curvature, *args):
        cmds.nonLinear(self.bendUp[0], e=True, curvature=curvature)
        self.curvature = curvature

    def adjustrandomRot(self, random_parm, *args):
        self.random_rot = random_parm
        pos=0
        snapchildren = cmds.listRelatives(self.snapshotGroup[0], c=True)
        for lash in snapchildren:
            pos+=1
            posNeg = random.random()
            #random.seed(pos)
            rand_factor = random.random() * random_parm
            if posNeg > 0.5:
                rand_factor = -rand_factor
            cmds.setKeyframe(self.lashTemp[0], attribute='rotateX', t=pos, v=rand_factor)
            cmds.setKeyframe(self.lashTemp[0], attribute='rotateY', t=pos, v=rand_factor)
            cmds.setKeyframe(self.lashTemp[0], attribute='rotateZ', t=pos, v=rand_factor)

    def adjustspacing(self, spacing, *args):
        self.spacing = spacing
        radius = ((cmds.arclen(self.lashesPath[0])-(self.spacing/self.amount)) / self.amount) / 2
        if radius > 0.01:
            coneName = [coneName for coneName in cmds.listHistory(self.lashTemp) if coneName.startswith('polyCone')][1]
            cmds.setAttr(coneName +'.radius', radius)

    def adjustPoly(self, quality,  *args):
        coneName = [coneName for coneName in cmds.listHistory(self.lashTemp) if coneName.startswith('polyCone')][1]
        if quality == 1:
            cmds.polyCone(coneName, edit=True, sx=3)
            cmds.polyCone(coneName, edit=True, sy=5)
        elif quality == 2:
            cmds.polyCone(coneName, edit=True, sx=5)
            cmds.polyCone(coneName, edit=True, sy=10)
        else:
            cmds.polyCone(coneName, edit=True, sx=10)
            cmds.polyCone(coneName, edit=True, sy=30)

    def adjustSmoothness(self, smoothness, *args):
        self.selectall()
        if smoothness == 0:
            cmds.displaySmoothness( polygonObject=1 )
        else:
            cmds.displaySmoothness( polygonObject=3 )

    def adjustDistribution(self, distribution, *args):
        if distribution == 1:
            self.arc = True
        else:
            self.arc = False
        self.adjustlength(self.minLength, self.maxLength, self.random_length)

    def deleteLashes(self, *args):
        cmds.delete(self.groupAll)
        cmds.delete(self.material)

    def applyLashes(self, *args):
        counter=1
        snapchildren = cmds.listRelatives(self.snapshotGroup[0], c=True)
        for lash in snapchildren:
            if counter > self.amount:
                cmds.delete(lash)
            counter+=1
        #cmds.delete(self.snapWrapGroup)
        cmds.setAttr(self.groupAll+'|'+self.snapWrapGroup+'.visibility', 0)

    def selectall(self, *args):
        cmds.select(self.groupAll, add=False)
