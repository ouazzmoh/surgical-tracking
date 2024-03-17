import numpy as np
import matplotlib.pyplot as plt


R = np.array([[1, 0, 0],
             [0, 0.81733806, 0.57615839],
             [0, -0.57615839, 0.81733806]])
class Plot3DPoints:
    def __init__(self):
        # pass rotation as param ?
        self.R = R

    def plot(self, points_3d_01, T1, T2, T3):
        if points_3d_01:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            x1, y1, z1 = [pt[0] for pt in points_3d_01], [pt[1] for pt in points_3d_01], [pt[2] for pt in points_3d_01]
            # x2, y2, z2 = [pt[0] for pt in points_3d_02], [pt[1] for pt in points_3d_02], [pt[2] for pt in points_3d_02]
            # x3, y3, z3 = [pt[0] for pt in points_3d_03], [pt[1] for pt in points_3d_03], [pt[2] for pt in points_3d_03]
            # x4, y4, z4 = [pt[0] for pt in points_3d_12], [pt[1] for pt in points_3d_12], [pt[2] for pt in points_3d_12]
            # x5, y5, z5 = [pt[0] for pt in points_3d_31], [pt[1] for pt in points_3d_31], [pt[2] for pt in points_3d_31]
            # x6, y6, z6 = [pt[0] for pt in points_3d_32], [pt[1] for pt in points_3d_32], [pt[2] for pt in points_3d_32]
            # xm, ym, zm = [pt[0] for pt in mean3d], [pt[1] for pt in mean3d], [pt[2] for pt in mean3d]

            ax.scatter(x1, y1, z1, color='red', label='Camera 1')
            #ax.scatter(x2, y2, z2, color='blue', label='Camera 2')
            #ax.scatter(x3, y3, z3, color='green', label='Camera 3')
            #ax.scatter(x4, y4, z4, color='yellow', label='Camera 1')
            # ax.scatter(x5, y5, z5, color='black', label='Camera 2')
            # ax.scatter(x6, y6, z6, color='green', label='Camera 3')
            # ax.scatter(xm, ym, zm, color='red', label='mean')
            

            # Camera plot:
            RT_1 = np.dot(R, np.array([T1[0][0], T1[1][0], T1[2][0]]))
            RT_2 = np.dot(R, np.array([T2[0][0], T2[1][0], T2[2][0]]))
            RT_3 = np.dot(R, np.array([T3[0][0], T3[1][0], T3[2][0]]))

            ax.plot([0, RT_1[0]], [0, RT_1[1]], [0, RT_1[2]], color='black', linestyle='--', label='Camera 1 Orientation')
            ax.plot([0, RT_2[0]], [0, RT_2[1]], [0, RT_2[2]], color='black', linestyle='--', label='Camera 2 Orientation')
            ax.plot([0, RT_3[0]], [0, RT_3[1]], [0, RT_3[2]], color='black', linestyle='--', label='Camera 3 Orientation')

            ax.scatter([0], [0], [0], color='black', label='Camera 0 Position')
            ax.scatter([RT_1[0]], [RT_1[1]], [RT_1[2]], color='black', label='Camera 1 Position')
            ax.scatter([RT_2[0]], [RT_2[1]], [RT_2[2]], color='black', label='Camera 2 Position')
            ax.scatter([RT_3[0]], [RT_3[1]], [RT_3[2]], color='black', label='Camera 3 Position')

            ax.set_ylim([0, 120])
            ax.set_xlim([-60, 60])
            ax.set_zlim([0, 120])

            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')

            plt.show()
            plt.savefig('ReconstructionPlot.png')
