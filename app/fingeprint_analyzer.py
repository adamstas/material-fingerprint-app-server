import logging

import torch
import numpy as np
import clip
import yaml

from typing import Tuple

from app.source import get_plot_res, get_polar_plot, RATING_NAMES, RATING_CHANGE, MEANS, STDS

from app.veronika_features import StatisticalFeatures
from app.fingerprint_clip import MLP, clip_preprocess

class ImageStats:

    def __init__(self, statistics: np.ndarray, normalized_statistics: np.ndarray, ratings: np.ndarray):
        self.statistics = statistics
        self.normalized_statistics = normalized_statistics

    
class MaterialRatings:

    def __init__(self, ratings: np.ndarray):
        self.ratings = ratings

    def get_line_plot(self, color="blue", label="Predicted PHOTO"):

        return get_plot_res([self.ratings], colors=[color], labels=[label])

    def get_polar_plot(self, color="blue"):


        return get_polar_plot([self.ratings], order=RATING_CHANGE)


class FingerPrintAnalyzer:

    def __init__(self):
        
        logging.debug("Initializing StatisticalFeatures object.")
        
        self.sf = StatisticalFeatures()


        logging.debug("Initializing clip model")
        # clip model
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.clip_model, _ = clip.load("ViT-B/32", device=self.device)
        self.clip_model.eval()


        logging.debug("Initializing custom MLP model")
        # mlp model

        with open('app/config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        model_path = config['mlp_model_path']

        self.mlp_model = MLP((2*512,512,512,16)).to(device=self.device)
        checkpoint = torch.load(model_path, map_location=self.device)
        self.mlp_model.load_state_dict(checkpoint["model"])
        self.mlp_model.eval()



    def get_material_ratings(self, non_specular_image: np.ndarray, specular_image: np.ndarray) -> MaterialRatings:

        

        logging.debug("Preprocessing images for clip and MLP features computation")
        target_sz = 256 # smaller of the two dimensions after resize; this size needs to be set so that it corresponds in DPI to height=256 on the training set (the trainig set images are downscaled from 412 to 256 in height)
        imgs = [clip_preprocess(image, target_sz) for image in (non_specular_image, specular_image)]
        imgs = torch.stack(imgs, dim=0).to(device=self.device) # input frames as batch

        with torch.no_grad():

            logging.debug("Computing features with clip model")
            # run clip
            features = self.clip_model.encode_image(imgs)

            logging.debug("Computing rating using MLP model")
            # run mlp
            features = features.reshape(1, 2*512).to(dtype=torch.float32)
            fingerprint = self.mlp_model(features).cpu().numpy()


            ratings = fingerprint[0]
        

        return MaterialRatings(ratings)
    
    def get_image_statistics(self, non_specular_image: np.ndarray, specular_image: np.ndarray) -> Tuple[ImageStats, ImageStats]:
        
        logging.debug("Computing non-specular image stats")
        non_specular_stats= self.sf.compute(non_specular_image)

        logging.debug("Computing specular image stats")
        specular_stats = self.sf.compute(specular_image)
    
        non_specular_means = MEANS[:len(MEANS)//2]
        non_specular_stds = STDS[:len(STDS)//2]
        specular_means = MEANS[len(MEANS)//2:]
        specular_stds = STDS[len(STDS)//2:]

        non_specular_stats_normalized = (non_specular_stats - non_specular_means) / non_specular_stds
        specular_stats_normalized = (specular_stats - specular_means) / specular_stds

        non_specular_image_stats = ImageStats(non_specular_stats, non_specular_stats_normalized)
        specular_image_stats = ImageStats(specular_stats, specular_stats_normalized)

        return non_specular_image_stats, specular_image_stats