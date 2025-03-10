import numpy as np
from scipy.stats import pearsonr


# todo otestovat jestli OK
def calculate_similarity(v1: np.array, v2: np.array, alpha=0.5) -> float:
    
    assert v1.ndim == 1 and v1.ndim == v2.ndim
    
    size = len(v1)
    
    corr, _ = pearsonr(v1, v2)
    
    l1 = np.linalg.norm(v1 - v2, ord=1)
    
    return alpha * corr + (1 - alpha) * (1 - (l1 / (2 * size)))