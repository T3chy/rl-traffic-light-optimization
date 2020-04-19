import numpy as np

class TileCoder:

    def __init__(self, num_tilings, num_tiles, state_ranges):
        self.num_tilings = num_tilings
        self.num_tiles = num_tiles
        self.state_ranges = state_ranges
        self.tile_size  = (self.state_ranges[1] - self.state_ranges[0])/(self.num_tiles + 1/self.num_tilings - 1)
        self.tiling_origins = self.get_tiling_origins()

    def get_tiling_origins(self):
        origins = []
        for tiling in range(self.num_tilings):
            origin = self.state_ranges[0] - (self.num_tilings - 1 - tiling)*self.tile_size/self.num_tilings
            origins.append(origin)
        return origins

    def get_features(self, state):
        feature_vec = []
        for tiling in range(self.num_tilings):
            tile_vec = (np.array(state) - self.tiling_origins[tiling])/self.tile_size
            tile_vec = tile_vec.astype(int)
            tile_vec = np.where(tile_vec == self.num_tiles, self.num_tiles - 1, tile_vec)
            tile_num = np.sum(np.flip(tile_vec) * (self.num_tiles ** np.array(range(len(tile_vec)))))
            tiling_ft = np.zeros(self.num_tiles ** len(tile_vec)) != 0
            tiling_ft[tile_num] = True
            feature_vec += list(tiling_ft)
        return np.array(feature_vec)
