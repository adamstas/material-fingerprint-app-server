import numpy as np
from scipy.stats import pearsonr

# Dan’s code
# returns float -1 <= 0 <= 1 where the more negative it is the more dissimilarity two arrays have (their aspects move in opposite directions); 0 is no similarity; 1 is absolute similarity (e.g. for two same arrays)
def calculate_similarity(v1: np.array, v2: np.array, alpha=0.5) -> float:
    assert v1.ndim == 1 and v1.ndim == v2.ndim

    size = len(v1)
    corr, _ = pearsonr(v1, v2)
    l1 = np.linalg.norm(v1 - v2, ord=1)

    return alpha * corr + (1 - alpha) * (1 - (l1 / (2 * size)))