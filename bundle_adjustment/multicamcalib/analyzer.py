import numpy as np
import json
import cv2
import os
import math
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from helper import load_corner_txt, load_img_paths, load_img

def reproject(param, world_pts):
    # world_pts: (N, 3)
    R = param["R"]
    t = param["t"]
    fx = param["fx"]
    fy = param["fy"]
    cx = param["cx"]
    cy = param["cy"]
    k1 = param["k1"]
    k2 = param["k2"]
    p1 = param["p1"]
    p2 = param["p2"]
    k3 = param["k3"]

    # world to camera frame
    x = np.dot(world_pts, R.T) + t

    # camera to image frame
    x = x[:, 0:2] / x[:, 2][:, None]
    xp = x[:,0]
    yp = x[:,1]

    # lens distortions following opencv lens model
    # 1. radial
    r2 = xp**2 + yp**2
    radial = 1 + k1*r2 + k2*r2**2 + k3*r2**3
    xp = xp*radial
    yp = yp*radial

    # 2. tangential
    r2 = xp**2 + yp**2
    u = xp + (p2 * (r2 + 2*xp**2) + 2*p1*xp*yp)
    v = yp + (p1 * (r2 + 2*yp**2) + 2*p2*xp*yp)

    # following pinhole camera model
    u = fx*u + cx
    v = fy*v + cy
    
    return np.vstack([u, v]).T

def reproject_world_points(logger, cam_param_path, world_points_path, paths, reprojection_save_path):
    os.makedirs(paths["analysis"], exist_ok=True)

    # load camera parameters
    with open(cam_param_path, "r") as f:
        cam_params = json.load(f)
        for cam_idx, param in cam_params.items():
            rvec = np.float32(param["rvec"])
            R, _ = cv2.Rodrigues(rvec)
            t = np.float32(param["tvec"])
            cam_params[cam_idx]["R"] = R
            cam_params[cam_idx]["t"] = t

    # load world points to reproject
    with open(world_points_path, "r") as f:
        world_points = json.load(f)["frames"]
    
    # reproject each image points
    reprojections = {"config": {"cam_param_path": cam_param_path, "world_points_path": world_points_path}, "frames": {}}
    pbar = tqdm(total=len(world_points.keys()))
    for img_name, d in world_points.items():
        pbar.update(1)

        world_pts = np.float32(d["world_pts"])
        reprojections["frames"][img_name] = {}
        for cam_idx in cam_params.keys():
            fname = "{}_{}".format(cam_idx, img_name)

            corner_path = os.path.join(paths["corners"], "cam_{}".format(cam_idx), "{}.txt".format(fname))
            img_pts, _ = load_corner_txt(corner_path)

            if img_pts is None:
                continue

            reprojections["frames"][img_name][cam_idx] = {}
            img_pts_pred = reproject(cam_params[cam_idx], world_pts)
            dudv = img_pts - img_pts_pred
            err_each = np.sqrt(np.sum(dudv**2, axis=1))
            err_sum = float(np.sum(err_each))
            reprojections["frames"][img_name][cam_idx] = {"error_sum": err_sum, "img_pts_pred": img_pts_pred.tolist()}
    pbar.close()

    # save reprojections as json
    with open(reprojection_save_path, "w+") as f:
        json.dump(reprojections, f, indent=4)
        logger.info("Reprojections saved: {}".format(reprojection_save_path))

    return 1

def render_reprojection_results(logger, paths, save_reproj_err_histogram=True, save_reproj_images=True, error_thres=5):
    reprojection_path = os.path.join(paths["analysis"], "reprojections.json")
    with open(reprojection_path, "r") as f:
        reprojections = json.load(f)
        
        with open(reprojections["config"]["cam_param_path"], "r") as f:
            cam_params = json.load(f)

    # load outliers
    outliers_path = os.path.join(paths["outliers"], "outliers.json")
    if outliers_path is not None:
        with open(outliers_path, "r") as f:
            outliers_json = json.load(f)
            outliers = []
            for _, v in outliers_json.items():
                outliers.append(v["img_name"])
            outliers = set(outliers)
    else:
        outliers = []
        
    corner_errors = []
    corner_errors_2d = []
    errors_for_lookup = {} # img_name: max_error
    img_pts_measured = {} # img_name: {cam_idx: np.array}
    pbar = tqdm(total=len(reprojections["frames"].keys()))
    ceres_loss = 0.0
    for img_name, d in reprojections["frames"].items():
        errors_for_lookup[img_name] = -1
        img_pts_measured[img_name] = {}
        pbar.update(1)
        ceres_loss_curr = 0.0
        n_cams_used = 0
        for cam_idx, dd in d.items():
            fname = "{}_{}".format(cam_idx, img_name)
            if fname in outliers:
                logger.debug("Skipping outlier image during reprojection result rendering: {}".format(fname))
                continue

            corner_path = os.path.join(paths["corners"], "cam_{}".format(cam_idx), "{}.txt".format(fname))
            img_pts, _ = load_corner_txt(corner_path)

            if img_pts is None:
                continue
            
            img_pts_measured[img_name][cam_idx] = img_pts
            img_pts_pred = dd["img_pts_pred"]
            dudv = img_pts - img_pts_pred
            err_each = np.sqrt(np.sum(dudv**2, axis=1))
            corner_errors.extend(err_each)
            corner_errors_2d.extend(dudv)

            ceres_loss_curr += 0.5 * np.sum(dudv**2)
            n_cams_used += 1
            err_max = float(np.max(err_each))
            errors_for_lookup[img_name] = max(errors_for_lookup[img_name], err_max)
        ceres_loss_curr /= (n_cams_used**2)
        ceres_loss += ceres_loss_curr
    pbar.close()

    logger.info("(Cross-check) manually recalculated Ceres loss: {:,.2f} (excluding regularization loss)".format(ceres_loss))

    corner_errors = np.float32(corner_errors)
    corner_errors_2d = np.float32(corner_errors_2d)

    # plot historgrams
    if save_reproj_err_histogram:
        fs = 28
        fig = plt.figure(figsize=(22, 8))
        
        gs = GridSpec(1, 10, figure=fig)
        ax1 = fig.add_subplot(gs[0, 0:6])
        ax2 = fig.add_subplot(gs[0, 7:])

        bins_scale = min(3, int(np.log10(len(corner_errors))))
        ax1.grid(True)
        ax1.hist(corner_errors, bins=10**bins_scale)
        ax1.set_xlim(left=0)
        ax1.set_yscale('log')
        ax1.set_xlabel("Reprojection error [pixel]", fontsize=fs)
        ax1.set_ylabel("Bin count (log-scale)", fontsize=fs)
        ax1.set_title("Reprojection errors: {:,} points\n(mean={:.2f}, max={:.2f}, stdv={:.2f})".format(len(corner_errors), np.mean(corner_errors), np.max(corner_errors), np.std(corner_errors)), fontsize=fs)
        
        ax2.grid(True)
        ax2.scatter(corner_errors_2d[:,0], corner_errors_2d[:,1], edgecolors="k", linewidth=0.5, s=10)
        ax2.set_xlabel("du [pixel]", fontsize=fs)
        ax2.set_ylabel("dv [pixel]", fontsize=fs)
        ax2.set_title("Reprojection errors in 2D", fontsize=fs)

        max_err = np.max(corner_errors_2d)
        min_err = np.min(corner_errors_2d)
        L = max(abs(max_err), abs(min_err))
        ax2.set_xlim([-L, L])
        ax2.set_ylim([-L, L])

        cam_param_path = reprojections["config"]["cam_param_path"]
        world_points_path = reprojections["config"]["world_points_path"]
        plt.suptitle("Camera parameters: {}\nWorld points: {}".format(cam_param_path, world_points_path), fontsize=fs/2.5)
        fig.tight_layout()
        plot_save_path = os.path.join(paths["analysis"], "reproj_err_histograms.png")
        plt.savefig(plot_save_path, dpi=200)
        plt.close()
        logger.info("Plot saved: {}".format(plot_save_path))

    if save_reproj_images:
        save_dir = os.path.join(paths["analysis"], "images")
        os.makedirs(save_dir, exist_ok=True)
        logger.info("Saving images to: {}".format(save_dir))

        img_paths = load_img_paths(paths["abs_image_paths_file"])
        img_paths_lookup = {}
        for cam_idx, paths in img_paths.items():
            for p in paths:
                img_name = os.path.basename(p).split(".")[0]
                img_paths_lookup[img_name] = p
        
        fs = 20

        # for tqdm bar
        n_total = 0
        for img_name, err in errors_for_lookup.items():
            if err > error_thres:
                n_total += 1

        pbar = tqdm(total=n_total)
        n_imgs = 0

        for img_name, err in errors_for_lookup.items():
            if err > error_thres:
                pbar.update(1)
                N_sqrt = np.sqrt(len(cam_params.keys()))
                c = math.floor(N_sqrt)
                if N_sqrt > c**2:
                    r = c+1
                else:
                    r = c

                fig, ax = plt.subplots(r, c, figsize=(40, 28))
                ax = ax.ravel()

                # 1st loop to compute errors
                errs = []
                for cam_idx in cam_params.keys():
                    if cam_idx in reprojections["frames"][img_name] and cam_idx in img_pts_measured[img_name]:
                        reproj = reprojections["frames"][img_name][cam_idx]
                        pred = np.float32(reproj["img_pts_pred"])
                        gt = img_pts_measured[img_name][cam_idx]
                        err = np.sqrt(np.sum((gt-pred)**2, axis=1))
                        errs.extend(err)

                # 2nd loop to render
                vmin = np.min(errs)
                vmax = np.max(errs)
                vmean = np.mean(errs)
                idx = 0
                for cam_idx in cam_params.keys():
                    img_path = img_paths_lookup["{}_{}".format(cam_idx, img_name)]
                    img = load_img(img_path)

                    a = ax[int(cam_idx)]
                    if cam_idx in reprojections["frames"][img_name] and cam_idx in img_pts_measured[img_name]:
                        reproj = reprojections["frames"][img_name][cam_idx]
                        pred = np.float32(reproj["img_pts_pred"])
                        gt = img_pts_measured[img_name][cam_idx]

                        err_curr = errs[idx:idx+len(pred)]

                        if img is not None:
                            a.imshow(img, cmap="gray")
                        sc = a.scatter(pred[:,0], pred[:,1], c=err_curr, s=2, vmin=vmin, vmax=vmax, zorder=2)
                        a.scatter(gt[:,0], gt[:,1], c="lime", s=2, vmin=vmin, vmax=vmax, zorder=1)
                        a.set_title("Camera {}\nErrors: mean={:.2f}, min={:.2f}, max={:.2f}".format(cam_idx, np.mean(err_curr), np.min(err_curr), np.max(err_curr)))
                        idx += len(pred)
                    else:
                        a.axis(False)

                # add colorbar
                cax = fig.add_axes([0.92, 0.1, 0.01, 0.8]) # l,b,w,h
                cbar = fig.colorbar(sc, cax=cax, ticks=[vmin, vmean, vmax])
                
                # add colorbar ticks
                cbar.ax.set_yticklabels(["{:.2f} (min.)".format(vmin), "{:.2f} (mean)".format(vmean), "{:.2f} (max)".format(vmax)], fontsize=fs)

                plt.suptitle("Image: {}\nErrors: mean={:.2f}, min={:.2f}, max={:.2f}".format(img_name, vmean, vmin, vmax), fontsize=fs)

                save_path = os.path.join(save_dir, "{:.3f}_{}.png".format(vmax, img_name))
                plt.savefig(save_path, dpi=300)
                plt.close()
                n_imgs += 1
                logger.debug("Image saved: {}".format(save_path))
        pbar.close()
        
        logger.info("Finished rendering: {} images".format(n_imgs))
        