# ------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------
import numpy as np
from findpeaks import findpeaks
from matplotlib import pyplot as plt
import copy
import yaml

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


# File paths
# Current version of model parameters
MODEL_PARAM_1 = './modelParams'
# Current version of STDs and MEANs used in standardization

with open('app/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
file = config['stats-mean-std']

MEANS = np.loadtxt(file, dtype=float, usecols=0, delimiter=" ")
STDS = np.loadtxt(file, dtype=float, usecols=1, delimiter=" ")


# Constants
# Computational stats names
STAT_NAMES = ['Max','Min','Mean', 'Variance', 'Skewness', 'Kurtosis', 'Directionality',
              'Low frequencies', 'Middle frequencies', 'High frequencies',
              'Mean chroma', 'Pattern strength', 'Pattern number', 'Colors number']
# Rating stats names
RATING_NAMES = ['Color vibrancy', 'Surface roughness','Pattern complexity', 'Striped pattern',
                'Checkered pattern', 'Brightness', 'Shininess', 'Sparkle', 'Hardness',
                'Movement effect', 'Scale of pattern', 'Naturalness', 'Thickness',
                'Multicolored', 'Value', 'Warmth']
# Rearranging for polar plot
RATING_CHANGE = [6, 7, 2, 3, 4, 1, 10, 13, 0, 5, 11, 14, 15, 12, 8, 9]

def get_plot_res(data, colors=["blue"], labels=["Data"], SIZE=[15, 9], YLIM=[-2.5, 2.5, 0.5]):
    fig, ax = plt.subplots(figsize=(SIZE[0], SIZE[1]))
    for i in range(len(data)):
        ax.plot(RATING_NAMES, data[i], color=colors[i], marker="o", label=labels[i], linestyle='-', linewidth=2)
    ax.legend(loc='upper center', fontsize=12)
    ax.grid(alpha=0.5, linestyle='--', linewidth=0.5)
    ax.set_xticklabels(RATING_NAMES, rotation=45, ha="right", fontsize=10)  # Adjusted rotation and horizontal alignment for better fit
    ax.set_ylim(YLIM[0], YLIM[1])
    ax.set_yticks(np.arange(YLIM[0], YLIM[1]+YLIM[2], YLIM[2]))
    ax.set_ylabel('Rating', fontsize=12)
    ax.set_xlabel('Rating Categories', fontsize=12)
    ax.set_title('Rating Plot', fontsize=14)
    
    fig.tight_layout()  # Add this line to ensure labels fit within the figure
    
    canvas = FigureCanvas(fig)
    canvas.draw()

    image = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
    width, height = canvas.get_width_height()
    image = image.reshape(height, width, 3)

    plt.close(fig)

    return image

# General function for showing images
def show_images(images, SIZE=[20, 3]):
    fig, ax = plt.subplots(1, len(images), figsize=(SIZE[0], SIZE[1]))
    plt.subplots_adjust(wspace=0, hspace=0)
    for i in range(len(images)):
        ax[i].imshow(images[i])
        ax[i].set_xticks([])
        ax[i].set_yticks([])
        ax[i].set_axis_off()
    plt.show()

# Polar plot
def get_polar_plot(data_all_old, COLORS=["blue", "red", "green"], RATINGS=RATING_NAMES, LABELS=None, 
                    title=None, order=None, save=None, noticks=False,
                    SIZE=[15, 10], ZERO_WIDTH=0.01, ZERO_COLOR="black", LINE_WIDTH=2,
                    LABEL_SIZE_X=15, LABEL_SIZE_Y=15, YLIM=[-2.5, 2.5], LEGEND_SIZE=15,
                    TITLE_SIZE=15, FILL_RATE=0.05):
    # Rearranging order
    data_all = copy.deepcopy(data_all_old)
    if order is not None:
        for i in range(len(data_all)):
            data_all[i] = data_all[i][order]
        RATINGS = np.array(RATINGS)[order]
    
    fig = plt.figure(figsize=(SIZE[0], SIZE[1]))
    ax = fig.add_subplot(111, polar=True)
    theta = np.linspace(0, 2 * np.pi, len(RATINGS), endpoint=False)
    theta = np.concatenate((theta, [theta[0]]))
    
    # Black circle around 0
    ax.fill_between(np.linspace(0, 2*np.pi, 100), -ZERO_WIDTH, ZERO_WIDTH, color=ZERO_COLOR, zorder=10)
    
    # Data plotting
    for idx, data in enumerate(data_all):
        data = np.concatenate((data, [data[0]]))
        if LABELS is not None:
            ax.plot(theta, data, marker="o", color=COLORS[idx], label=LABELS[idx], linewidth=LINE_WIDTH)
        else:
            ax.plot(theta, data, marker="o", color=COLORS[idx], linewidth=LINE_WIDTH)
        ax.fill(theta, data, color=COLORS[idx], alpha=FILL_RATE)

    theta = np.linspace(0, 2 * np.pi, len(RATINGS), endpoint=False)
    ax.set_thetagrids((theta * 180/np.pi), RATINGS)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(direction='clockwise')
    
    # Positioning the labels around the circle
    for label, theta in zip(ax.get_xticklabels(), theta):
        if theta in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < theta < np.pi:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')
    
    ax.set_ylim(YLIM[0], YLIM[1])
    ax.tick_params(axis="y", labelsize=LABEL_SIZE_Y)
    ax.tick_params(axis="x", labelsize=LABEL_SIZE_X)
    ax.set_rlabel_position(180 / len(RATINGS))
    if LABELS is not None:
        ax.legend(bbox_to_anchor=(1.42,1.08), prop={'size': LEGEND_SIZE})
    
    if noticks:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.grid(False, axis="y")
    
    ax.set_title(title, fontsize=TITLE_SIZE)
    
    #if save is not None:
    #    plt.savefig(save, format="png", bbox_inches="tight", transparent=True)
    
    canvas = FigureCanvas(fig)
    canvas.draw()

    image = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')

    width, height = canvas.get_width_height()
    image = image.reshape(height, width, 3)

    plt.close(fig)
    return image