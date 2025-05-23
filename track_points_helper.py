"""
Created on Sat March  30, 2024

@author: Anders Bjorholm Dahl
e-mail: abda@dtu.dk

This program is free software: you can redistribute it and/or modify it under the 
terms of the GNU General Public License as published by the Free Software Foundation, 
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 
this program. If not, see <https://www.gnu.org/licenses/>.
"""

# Class for fiber tracking from detected center points


import numpy as np
import matplotlib.pyplot as plt

class TrackPoints:
    def __init__(self, int_thres=0.1, max_jump=5, max_skip=5, momentum=0.1, track_min_length=3):
        '''
        Initialization of the fiber tracker. The fiber tracker tracks fibers in the z-direction.

        Parameters
        ----------
        int_thres : float, optional
            Threshold for minimum intensity value of areas containing fibers. The default is 0.1.
        max_jump : float, optional
            Maximum distance between detected points in two consecutive frames. Threshold in pixels. The default is 5.
        max_skip : int, optional
            Maximum number of frames along one track where no points are detected. The default is 5.
        momentum : float, optional
            Parameter in the range [0;1] that gives momentum to the tracking direction. 
            The momentum gives the fraction of the current direction that is kept.
            The default is 0.1.
        track_min_length : int, optional
            Minimum number of points in a track.

        Returns
        -------
        None.

        '''
        self.int_thres = int_thres # Intensity threshold

        self.max_jump = max_jump**2 # not move more than max_jump pixels (using squared distance)
        if self.max_jump < 1: # should be at least 1 pixel
            self.max_jump = 1
        
        self.max_skip = max_skip # maximum number of slides that can be skipped in a track. If set to 0, then no slides can be skipped.
        if self.max_skip < 0:
            self.max_skip = 0

        self.momentum = momentum # direction momentum that must be between 0 and 1
        if self.momentum < 0:
            self.momentum = 0
        elif self.momentum > 1:
            self.momentum = 1
        
        self.track_min_length = track_min_length # minimum length of tracks that should be at least 1
        if self.track_min_length < 1:
            self.track_min_length = 1

        
    def __call__(self, coords):
        '''
        Call function for FiberTracker

        Parameters
        ----------
        coords : list of numpy arrays
            list of 2D numpy arrays with row and column indices of detected points. One per slice, which
            means that z is gives as the index of the list.
            
        Returns
        -------
        list
            list of numpy arrays each containing coordinates of tracked fibers.
        
        '''
        r = [coord[:,0] for coord in coords]
        c = [coord[:,1] for coord in coords]
        return self.track_fibers(r, c)
 
    def get_dist(self, ra, ca, rb, cb):
        '''
        Computes a 2D distance array between row and column coordinates in set a (ra, ca) and set b (rb, cb) 

        Parameters
        ----------
        ra : numpy array
            1D array of row coordinates of point a.
        ca : numpy array
            1D array of column coordinates of point a.
        rb : numpy array
            1D array of row coordinates of point b.
        cb : numpy array
            1D array of column coordinates of point b.

        Returns
        -------
        numpy array
            n_a x n_b 2D eucledian distance array between the two point sets.

        '''
        ra = np.array(ra)
        ca = np.array(ca)
        rb = np.array(rb)
        cb = np.array(cb)
        return ((np.outer(ra, np.ones((1,len(rb)))) - np.outer(np.ones((len(ra),1)), rb))**2 + 
                (np.outer(ca, np.ones((1,len(cb)))) - np.outer(np.ones((len(ca),1)), cb))**2)
    
    
    def swap_place(self, tr, id_first, id_second):
        '''
        Swaps the place of two elements in a list.

        Parameters
        ----------
        tr : list
            List of elements.
        id_to : integer
            Index of first element.
        id_from : integer
            Index of second element.

        Returns
        -------
        tr : list
            Updated list of elements.

        '''
        tmp = tr[id_first]
        tr[id_first] = tr[id_second]
        tr[id_second] = tmp
        return tr
    

    def track_fibers(self, r, c):
        '''
        Tracks fibers throughout the volume. Sets the parameters 
            - rr and cc (row and column coordinates where poitns closer than 
              max_jump have been removed. The point with highes intensity is kept)
            - tracks_all, which is a lsit of all tracked fibers
            - tracks, which is a list of tracks that are longer than track_min_length

        Returns
        -------
        None.

        '''
        
        tracks_all = [] # Coordinates
        ntr_ct = [] # count of not found points
        
        # initialize tracks (row, col, layer, drow, dcol) and counter for tracks
        for ra, ca in zip(r[0], c[0]):
            tracks_all.append([(ra, ca, 0, 0, 0)])
            ntr_ct.append(0)

        coord_r = r[0].copy()
        coord_c = c[0].copy()
        
        nf_counter = 0
        for i in range(1, len(r)):
            
            # Match nearest point
            d = self.get_dist(coord_r, coord_c, r[i], c[i])
            
            id_from = d.argmin(axis=0) # id from
            id_to = d.argmin(axis=1) # id to
            
            d_from = d.min(axis=0)
                
            id_match_from = id_to[id_from] # matched id from
            idx = id_match_from == np.arange(len(id_from)) # look up coordinates
            for j in range(len(idx)):
                if idx[j] and d_from[j] < self.max_jump:
                    drow = (self.momentum*(r[i][j] - tracks_all[id_from[j] + nf_counter][-1][0]) + 
                            (1-self.momentum)*tracks_all[id_from[j] + nf_counter][-1][3])
                    dcol = (self.momentum*(c[i][j] - tracks_all[id_from[j] + nf_counter][-1][1]) +
                            (1-self.momentum)*tracks_all[id_from[j] + nf_counter][-1][4])
                    tracks_all[id_from[j] + nf_counter].append((r[i][j], c[i][j], i, drow, dcol))
                else:
                    tracks_all.append([(r[i][j], c[i][j], i, 0, 0)])
                    ntr_ct.append(0)
                    
            not_matched = np.ones(len(coord_r), dtype=int)
            not_matched[id_from] = 0
            for j in range(len(not_matched)):
                if not_matched[j]:
                    ntr_ct[j + nf_counter] += 1
            
            coord_r = []
            coord_c = []
                        
            for j in range(nf_counter, len(tracks_all)):
                if ntr_ct[j] > self.max_skip:
                    ntr_ct = self.swap_place(ntr_ct, j, nf_counter)
                    tracks_all = self.swap_place(tracks_all, j, nf_counter)
                    nf_counter += 1
            
            for j in range(nf_counter, len(tracks_all)):
                coord_r.append(tracks_all[j][-1][-5] + (i-tracks_all[j][-1][-3])*tracks_all[j][-1][-2])
                coord_c.append(tracks_all[j][-1][-4] + (i-tracks_all[j][-1][-3])*tracks_all[j][-1][-1])
            if i%10 == 9:
                print(f'\rTracking slide {i+1} out of {len(r)}', end='\r')
        
        tracks = []
        for track in tracks_all:
            track_len = 0
            track_arr = np.stack(track)
            for i in range(1, len(track)):
                # track_len += ((track_arr[i] - track_arr[i-1])**2).sum()**0.5
                track_len += np.linalg.norm(track_arr[i]-track_arr[i-1])
            if track_len > self.track_min_length:
                track_arr = np.stack(track)
                tracks.append(track_arr[:,:3])
        
        return tracks
    
    def fill_track(self, track):
        '''
        Fills in missing points in a track by linear interpolation. 
            
        track : numpy array 
            Is a numpy array with columns (row, col, layer)
        
        Returns
        -------
        t : numpy array
            Filled track.
        '''
        n = int(track[-1,2] - track[0,2] + 1)
        t = np.zeros((n,3))
        ct = 1
        t[0] = track[0]
        for i in range(1,n):
            if track[ct,2] == i + track[0,2]:
                t[i] = track[ct]
                ct += 1
            else:
                nom = (track[ct,2] - track[ct-1,2])
                den1 = track[ct,2] - track[0,2] - i
                den2 = i - (track[ct-1,2] - track[0,2])
                w1 = den1/nom
                w2 = den2/nom
                t[i,0:2] = track[ct-1,0:2]*w1 + track[ct,0:2]*w2
                t[i,2] = i + track[0,2]
        return t.astype(int)
    
    def fill_tracks(self, tracks):
        '''
        Fills in missing points in a list of tracks by linear interpolation. 
            
        tracks : list
            Is a list of numpy arrays with columns (row, col, layer)
        
        Returns
        -------
        tracks_filled : list
            List of filled tracks.
        '''
        tracks_filled = []
        for track in tracks:
            tracks_filled.append(self.fill_track(track))
        return tracks_filled

def trackpoints(int_thres=0.1, max_jump=5, max_skip=5, momentum=0.1, track_min_length=3):
    return TrackPoints(int_thres=int_thres, max_jump=max_jump, max_skip=max_skip,
                        momentum=momentum, track_min_length=track_min_length)

if __name__ == '__main__':
    import pickle
    # Load coordinates from file
    with open('coords.pkl', 'rb') as file: 
        coords = pickle.load(file)
    # Track fibers
    fib_tracker = trackpoints()
    tracks = fib_tracker(coords)
    # Plot tracks larger than 50 pixels
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    for track in tracks:
        if (track[-1, 2] - track[0, 2]) > 50:
            ax.plot(track[:,0], track[:,1], track[:,2], '-')
    ax.set_aspect('equal')
    plt.show()

