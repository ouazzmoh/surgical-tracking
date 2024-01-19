import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import json
from tqdm import tqdm
import cv2
import os
from helper import load_corner_txt
from analyzer import reproject

def _draw_camera(ax, cam_idx, rvec, tvec, zorder=10, color="k"):
    w = 700
    h = w/2
    rect0 = np.float32([[-w/2, -h/2, 0], [-w/2, h/2, 0], [w/2, h/2, 0], [w/2, -h/2, 0], [0, 0, -w*2/3]])
    R, _ = cv2.Rodrigues(rvec)
    R_SE3 = R.T
    t_SE3 = -R.T.dot(tvec)
    
    rect = []
    for r in rect0:
        rect.append(R_SE3@r + t_SE3)
    rect = np.float32(rect)
    ax.plot([rect[0, 0], rect[1,0]], [rect[0, 1], rect[1,1]], [rect[0, 2], rect[1,2]], c=color, zorder=zorder)
    ax.plot([rect[1, 0], rect[2,0]], [rect[1, 1], rect[2,1]], [rect[1, 2], rect[2,2]], c=color, zorder=zorder)
    ax.plot([rect[2, 0], rect[3,0]], [rect[2, 1], rect[3,1]], [rect[2, 2], rect[3,2]], c=color, zorder=zorder)
    ax.plot([rect[3, 0], rect[0,0]], [rect[3, 1], rect[0,1]], [rect[3, 2], rect[0,2]], c=color, zorder=zorder)

    ax.plot([rect[0, 0], rect[4,0]], [rect[0, 1], rect[4,1]], [rect[0, 2], rect[4,2]], c=color, zorder=zorder)
    ax.plot([rect[1, 0], rect[4,0]], [rect[1, 1], rect[4,1]], [rect[1, 2], rect[4,2]], c=color, zorder=zorder)
    ax.plot([rect[2, 0], rect[4,0]], [rect[2, 1], rect[4,1]], [rect[2, 2], rect[4,2]], c=color, zorder=zorder)
    ax.plot([rect[3, 0], rect[4,0]], [rect[3, 1], rect[4,1]], [rect[3, 2], rect[4,2]], c=color, zorder=zorder)

    L = 500
    x = R_SE3@np.float32([L, 0, 0]) + t_SE3
    y = R_SE3@np.float32([0, L, 0]) + t_SE3
    z = R_SE3@np.float32([0, 0, L]) + t_SE3
    ax.plot([t_SE3[0], x[0]], [t_SE3[1], x[1]], [t_SE3[2], x[2]], c="r", zorder=zorder-1)
    ax.plot([t_SE3[0], y[0]], [t_SE3[1], y[1]], [t_SE3[2], y[2]], c="g", zorder=zorder-1)
    ax.plot([t_SE3[0], z[0]], [t_SE3[1], z[1]], [t_SE3[2], z[2]], c="b", zorder=zorder-1)

    # ax.plot([t_SE3[0], t_SE3[0]], [t_SE3[1], t_SE3[1]], [0, t_SE3[2]], linestyle=":", linewidth=1, c="k")
    ax.text(t_SE3[0], t_SE3[1], t_SE3[2]+L, cam_idx, fontsize=12, zorder=zorder)

def render_config(paths, in_cam_param_path, center_cam_idx=None, center_img_name=None, in_world_points_path=None, title="Configuration", compute_reproj_errs=False, save_path=None):
    with open(in_cam_param_path, "r") as f:
        cam_params = json.load(f)

        if compute_reproj_errs:
            for cam_idx, param in cam_params.items():
                rvec = np.float32(param["rvec"])
                R, _ = cv2.Rodrigues(rvec)
                t = np.float32(param["tvec"])
                cam_params[cam_idx]["R"] = R
                cam_params[cam_idx]["t"] = t

    ax = plt.axes(projection='3d')
    L = 1000
    ax.plot([0, L], [0, 0], [0, 0], c="r", linewidth=4)
    ax.plot([0, 0], [0, L], [0, 0], c="g", linewidth=4)
    ax.plot([0, 0], [0, 0], [0, L], c="b", linewidth=4)

    mean_err = 0
    n_errs = 0
    if in_world_points_path is not None:
        with open(in_world_points_path, "r") as f:
            world_pts_json = json.load(f)
            world_pts = world_pts_json["frames"]
            chb = world_pts_json["checkerboard"]

            # compute reprojection errors
            if compute_reproj_errs:
                pbar = tqdm(total=len(world_pts.keys()))
                for img_name, d in world_pts.items():
                    pbar.update(1)

                    world_pts_curr = np.float32(d["world_pts"])
                    for cam_idx in cam_params.keys():
                        fname = "{}_{}".format(cam_idx, img_name)

                        corner_path = os.path.join(paths["corners"], "cam_{}".format(cam_idx), "{}.txt".format(fname))
                        img_pts, _ = load_corner_txt(corner_path)

                        if img_pts is None:
                            continue
                        
                        img_pts_pred = reproject(cam_params[cam_idx], world_pts_curr)
                        dudv = img_pts - img_pts_pred
                        err_each = np.sqrt(np.sum(dudv**2, axis=1))
                        err_sum = float(np.sum(err_each))
                        mean_err += (err_sum / len(img_pts_pred))
                        n_errs += 1
                pbar.close()
            if n_errs > 0:
                mean_err /= n_errs
        k = 0

        # render initial checkerboard points (world points)
        r = chb["n_rows"]
        c = chb["n_cols"]
        for img_name, d in world_pts.items():
            if d["n_detected"] > 0:
                p = np.float32(d["world_pts"])
                # ax.scatter(p[:,0], p[:,1], p[:,2], c='lime', s=0.1, zorder=1)

                if img_name == center_img_name:
                    color = "r"
                    zorder=9
                else:
                    color = "lime"
                    zorder = 2
                ax.plot([p[0, 0], p[c-1, 0]], [p[0, 1], p[c-1, 1]], [p[0, 2], p[c-1, 2]], c=color, linewidth=0.5, zorder=zorder)
                ax.plot([p[0, 0], p[(r-1)*c, 0]], [p[0, 1], p[(r-1)*c, 1]], [p[0, 2], p[(r-1)*c, 2]], c=color, linewidth=0.5, zorder=zorder)
                ax.plot([p[c-1, 0], p[r*c-1, 0]], [p[c-1, 1], p[r*c-1, 1]], [p[c-1, 2], p[r*c-1, 2]], c=color, linewidth=0.5, zorder=zorder)
                ax.plot([p[(r-1)*c, 0], p[r*c-1, 0]], [p[(r-1)*c, 1], p[r*c-1, 1]], [p[(r-1)*c, 2], p[r*c-1, 2]], c=color, linewidth=0.5, zorder=zorder)
                
                k += 1
    
    # render initial camera configurations
    for cam_idx, v in cam_params.items():
        tvec = np.float32(v["tvec"]).flatten()
        rvec = np.float32(v["rvec"]).flatten()

        if int(cam_idx) == center_cam_idx:
            color = "r"
        else:
            color = "k"
        _draw_camera(ax, cam_idx, rvec, tvec, zorder=10, color=color)

    # ax.set_xlim([-3000, 3000])
    # ax.set_ylim([-3000, 3000])
    # ax.set_zlim([-500, 2500])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    if compute_reproj_errs:
        plt.title("{}\nMean reprojection error = {:.4f} [pixels]".format(title, mean_err), loc='left')
    else:
        plt.title("{}".format(title))

    if save_path is not None:
        plt.savefig(save_path, dpi=150)
        plt.close()
    else:
        plt.show()
