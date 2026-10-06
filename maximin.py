from typing import List, Tuple, Dict
from data_provider import Car, euclidean_distance

class MaximinClustering:
    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
        self.centroids: List[Tuple[float, float, float]] = []
        self.clusters: Dict[int, List[Car]] = {}

    def fit(self, data: List[Car]) -> None:
        points = [(c.power, c.consumption, c.acceleration) for c in data]
        self.centroids = [points[0]]
        
        dists_to_first = [euclidean_distance(p, self.centroids[0]) for p in points]
        self.centroids.append(points[dists_to_first.index(max(dists_to_first))])
        
        while True:
            max_min_dist = -1.0
            candidate = None
            
            for p in points:
                if p in self.centroids:
                    continue
                min_to_c = min(euclidean_distance(p, c) for c in self.centroids)
                if min_to_c > max_min_dist:
                    max_min_dist = min_to_c
                    candidate = p
                    
            sum_dist = 0.0
            count = 0
            for i in range(len(self.centroids)):
                for j in range(i + 1, len(self.centroids)):
                    sum_dist += euclidean_distance(self.centroids[i], self.centroids[j])
                    count += 1
            avg_dist = sum_dist / count if count > 0 else 0.0
            
            if candidate and max_min_dist > self.alpha * avg_dist:
                self.centroids.append(candidate)
            else:
                break
                
        self.clusters = {i: [] for i in range(len(self.centroids))}
        for item in data:
            pt = (item.power, item.consumption, item.acceleration)
            dists = [euclidean_distance(pt, c) for c in self.centroids]
            self.clusters[dists.index(min(dists))].append(item)

    def predict(self, pt: Tuple[float, float, float]) -> Tuple[int, float]:
        if not self.centroids:
            return 0, 0.0
        dists = [euclidean_distance(pt, c) for c in self.centroids]
        idx = dists.index(min(dists))
        return idx, dists[idx]