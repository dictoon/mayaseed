import maya.cmds as cmds

matrix = cmds.xform(q=True, ws=True, m=True) #get matrix from selected object

m = [matrix[0],matrix[1],matrix[2],matrix[3]], [matrix[4],matrix[5],matrix[6],matrix[7]], [matrix[8],matrix[9],matrix[10],matrix[11]], [matrix[12],matrix[13],matrix[14],matrix[15]]


print "{0:.16f} {1:.16f} {2:.16f} {3:.16f}".format(matrix[ 0], matrix[ 4], matrix[ 8], matrix[12])
print "{0:.16f} {1:.16f} {2:.16f} {3:.16f}".format(matrix[ 1], matrix[ 5], matrix[ 9], matrix[13])
print "{0:.16f} {1:.16f} {2:.16f} {3:.16f}".format(matrix[ 2], matrix[ 6], matrix[10], matrix[14])
print "{0:.16f} {1:.16f} {2:.16f} {3:.16f}".format(matrix[ 3], matrix[ 7], matrix[11], matrix[15])

#git test  p
         
         
         