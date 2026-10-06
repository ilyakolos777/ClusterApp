import random
from typing import List, Tuple, Dict
from data_provider import Car, euclidean_distance

class KMeansClustering:
    def __init__(self, k: int = 2, max_iters: int = 100):
        self.k = k
        self.max_iters = max_iters
        self.centroids: List[Tuple[float, float, float]] = []
        self.clusters: Dict[int, List[Car]] = {}

    def fit(self, data: List[Car]) -> None:
        random.seed(42)
        initial = random.sample(data, self.k)
        self.centroids = [(c.power, c.consumption, c.acceleration) for c in initial]
        
        for _ in range(self.max_iters):
            self.clusters = {i: [] for i in range(self.k)}
            for item in data:
                pt = (item.power, item.consumption, item.acceleration)
                dists = [euclidean_distance(pt, c) for c in self.centroids]
                self.clusters[dists.index(min(dists))].append(item)
                
            new_centroids = []
            for i in range(self.k):
                c_items = self.clusters[i]
                if not c_items:
                    new_centroids.append(self.centroids[i])
                    continue
                avg_p = sum(x.power for x in c_items) / len(c_items)
                avg_c = sum(x.consumption for x in c_items) / len(c_items)
                avg_a = sum(x.acceleration for x in c_items) / len(c_items)
                new_centroids.append((avg_p, avg_c, avg_a))
                
            if self.centroids == new_centroids:
                break
            self.centroids = new_centroids

    def predict(self, pt: Tuple[float, float, float]) -> Tuple[int, float]:
        dists = [euclidean_distance(pt, c) for c in self.centroids]
        idx = dists.index(min(dists))
        return idx, dists[idx]