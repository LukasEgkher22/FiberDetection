import unittest
import numpy as np
import matplotlib.pyplot as plt

class TestParametricCurvature(unittest.TestCase):

    def compute_parametric_curvature(tracks):
        track_curvatures = []
        track_lengths = []
        
        for track in tracks:
            n_points = len(track)
            if n_points < 3:
                track_curvatures.append(np.array([]))
                continue
                
            curvatures = np.zeros(n_points)
            
            # Compute first derivatives using central differences
            velocity = np.zeros_like(track)
            velocity[1:-1] = (track[2:] - track[:-2]) / 2.0
            velocity[0] = track[1] - track[0] / 2.0
            velocity[-1] = track[-1] - track[-2] / 2.0
            
            # Compute second derivatives using central differences
            acceleration = np.zeros_like(track)
            acceleration[1:-1] = (track[2:] - 2*track[1:-1] + track[:-2])
            acceleration[0] = track[2] - 2*track[1] + track[0]
            acceleration[-1] = track[-1] - 2*track[-2] + track[-3]
            
            # Calculate curvature for each point using the formula:
            # κ = |r' × r''| / |r'|³
            for i in range(n_points):
                v = velocity[i]      # First derivative
                a = acceleration[i]  # Second derivative
                
                # Calculate cross product |r' × r''|
                cross_product = np.cross(v, a)
                numerator = np.linalg.norm(cross_product)
                
                # Calculate |r'|³
                v_magnitude = np.linalg.norm(v)
                denominator = v_magnitude**3
                
                # Calculate curvature (avoid division by zero)
                if denominator > 1e-10:
                    curvatures[i] = numerator / denominator
            
            track_curvatures.append(curvatures)
            track_lengths.append(n_points)
        
        return track_curvatures, track_lengths

    # Function to compute average curvature per track
    def compute_average_parametric_curvature(tracks):
        """
        Compute average parametric curvature for each track
        """
        avg_curvatures = []
        
        track_curvatures, track_lengths = TestParametricCurvature.compute_parametric_curvature(tracks)
        for curvatures in track_curvatures:
            valid_curvatures = curvatures[(curvatures > 0) & np.isfinite(curvatures) & (curvatures < 1e6)]
            if len(valid_curvatures) > 0:
                avg_curvatures.append(np.mean(valid_curvatures))
        
        return np.array(avg_curvatures), np.array(track_lengths)

    # Function to plot histograms of curvature
    def plot_curvature_histogram(curvatures_UD, curvatures_Mock):
        """
        Plot histograms of fiber curvatures
        
        Parameters:
        -----------
        curvatures_UD : np.array
            Array of curvature values for UD fibers
        curvatures_Mock : np.array
            Array of curvature values for Mock fibers
        """
        plt.figure(figsize=(12, 6))
        
        # Define bins based on the range of curvatures
        max_curvature = max(np.percentile(curvatures_UD, 99), np.percentile(curvatures_Mock, 99))
        bins = np.linspace(0, max_curvature, 50)
        
        plt.hist(curvatures_UD, bins=bins, alpha=0.5, label='UD')
        plt.hist(curvatures_Mock, bins=bins, alpha=0.5, label='Mock')
        
        plt.title('Fiber Curvature Distribution')
        plt.xlabel('Curvature')
        plt.ylabel('Frequency')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
        
        # Print statistics
        print("UD fiber curvatures:")
        print(f"  Mean: {np.mean(curvatures_UD):.6f}")
        print(f"  Median: {np.median(curvatures_UD):.6f}")
        print(f"  Min: {np.min(curvatures_UD):.6f}")
        print(f"  Max: {np.max(curvatures_UD):.6f}")
        
        print("\nMock fiber curvatures:")
        print(f"  Mean: {np.mean(curvatures_Mock):.6f}")
        print(f"  Median: {np.median(curvatures_Mock):.6f}")
        print(f"  Min: {np.min(curvatures_Mock):.6f}")
        print(f"  Max: {np.max(curvatures_Mock):.6f}")
    
    def test_circle_curvature(self):
        """Test curvature computation with a circle which has known curvature of 1/radius"""
        
        # Create a circle with radius 2.0 in the xy-plane
        radius = 2.0
        expected_curvature = 1.0 / radius
        
        # Generate points on a circle
        theta = np.linspace(0, 2*np.pi, 100)
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        z = np.zeros_like(theta)  # Circle in xy-plane
        
        # Create track in the format expected by the function
        circle_track = np.column_stack((x, y, z))
        tracks = [circle_track]
        
        # Compute curvature
        track_curvatures, _ = TestParametricCurvature.compute_parametric_curvature(tracks)
        
        # Get average curvature
        avg_curvatures, _ = TestParametricCurvature.compute_average_parametric_curvature(tracks)
        
        # Check curvature values (excluding endpoints which may have numerical issues)
        curvature_values = track_curvatures[0][10:-10]  # Skip first and last 10 points
        
        # Print mean computed curvature and expected curvature
        print(f"Expected curvature: {expected_curvature}")
        print(f"Mean computed curvature: {np.mean(curvature_values)}")
        print(f"Min computed curvature: {np.min(curvature_values)}")
        print(f"Max computed curvature: {np.max(curvature_values)}")
        
        # Verify curvature is close to expected value (with tolerance)
        self.assertTrue(
            np.abs(np.mean(curvature_values) - expected_curvature) < 0.05,
            f"Expected curvature ~{expected_curvature}, but got {np.mean(curvature_values)}"
        )
        
        # Verify average curvature function works correctly
        self.assertTrue(
            np.abs(avg_curvatures[0] - expected_curvature) < 0.05,
            f"Expected average curvature ~{expected_curvature}, but got {avg_curvatures[0]}"
        )
        
        # Visualization of computed curvature around the circle
        plt.figure(figsize=(10, 6))
        plt.plot(track_curvatures[0], label='Computed Curvature')
        plt.axhline(y=expected_curvature, color='r', linestyle='--', label=f'Expected Curvature = {expected_curvature}')
        plt.title('Circle Curvature Test')
        plt.xlabel('Point Index')
        plt.ylabel('Curvature')
        plt.legend()
        plt.grid(True)
        plt.show()
        
    def test_multiple_circles(self):
        """Test with multiple circles of different radii"""
        
        radii = [1.0, 2.0, 5.0]
        tracks = []
        expected_curvatures = []
        
        # Generate circles with different radii
        for radius in radii:
            theta = np.linspace(0, 2*np.pi, 100)
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            z = np.zeros_like(theta)
            
            circle_track = np.column_stack((x, y, z))
            tracks.append(circle_track)
            expected_curvatures.append(1.0 / radius)
        
        # Compute average curvatures
        avg_curvatures, _ = TestParametricCurvature.compute_average_parametric_curvature(tracks)
        
        # Check each circle's curvature
        for i, (expected, computed) in enumerate(zip(expected_curvatures, avg_curvatures)):
            print(f"Circle {i+1} (radius {radii[i]}): Expected = {expected}, Computed = {computed}")
            self.assertTrue(
                np.abs(computed - expected) < 0.05,
                f"Circle {i+1}: Expected curvature ~{expected}, but got {computed}"
            )

if __name__ == "__main__":
    unittest.main()