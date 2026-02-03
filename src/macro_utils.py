import time
import random
import math
from utils import pynput_mouse

class MacroUtils:
    """Utility functions for macro execution"""
    
    def __init__(self, app):
        self.app = app
    
    def vary(self, ms):
        """Apply random variance to a single timing value (in ms). Returns ms."""
        variance_pct = self.app.timing_variance_var.get()
        if variance_pct == 0:
            return ms
        max_delta = ms * variance_pct / 100.0
        delta = random.uniform(-max_delta, max_delta)
        return max(1, ms + delta)  # Never go below 1ms

    def vsleep(self, ms):
        """Sleep for ms with variance applied. Checks stop flags every 50ms for responsiveness."""
        total_ms = self.vary(ms)
        chunk_ms = 50  # Check every 50ms for stop signals
        elapsed = 0
        while elapsed < total_ms:
            # Check all stop flags
            if self.app.mine_stop or self.app.triggernade_stop:
                return  # Exit sleep early if any stop requested
            sleep_time = min(chunk_ms, total_ms - elapsed)
            time.sleep(sleep_time / 1000.0)
            elapsed += sleep_time

    def vary_balanced(self, ms, count):
        """Generate 'count' delays that each vary but sum to exactly ms*count.
        This makes loops look human while keeping total timing identical."""
        variance_pct = self.app.timing_variance_var.get()
        if variance_pct == 0 or count <= 1:
            return [ms] * count

        # Generate random variations
        max_delta = ms * variance_pct / 100.0
        deltas = [random.uniform(-max_delta, max_delta) for _ in range(count)]

        # Adjust so they sum to zero (balanced)
        avg_delta = sum(deltas) / count
        deltas = [d - avg_delta for d in deltas]

        # Apply to base timing, ensure minimum 1ms
        return [max(1, ms + d) for d in deltas]

    def curved_drag(self, start, end, steps=20, step_delay=5):
        """Perform a drag from start to end with a randomized curved path"""
        start_x, start_y = start
        end_x, end_y = end
        dx = end_x - start_x
        dy = end_y - start_y

        # Random curve offset perpendicular to the path
        # Magnitude is 5-15% of the path length
        path_length = math.sqrt(dx*dx + dy*dy)
        curve_magnitude = path_length * random.uniform(0.05, 0.15)
        # Random direction (left or right of path)
        curve_sign = random.choice([-1, 1])
        # Perpendicular vector (normalized)
        if path_length > 0:
            perp_x = -dy / path_length * curve_magnitude * curve_sign
            perp_y = dx / path_length * curve_magnitude * curve_sign
        else:
            perp_x, perp_y = 0, 0

        # Move mouse through curved path using quadratic bezier
        for i in range(steps + 1):
            t = i / steps
            # Quadratic bezier: P = (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
            # P0 = start, P2 = end, P1 = midpoint + perpendicular offset
            mid_x = (start_x + end_x) / 2 + perp_x
            mid_y = (start_y + end_y) / 2 + perp_y

            x = (1-t)**2 * start_x + 2*(1-t)*t * mid_x + t**2 * end_x
            y = (1-t)**2 * start_y + 2*(1-t)*t * mid_y + t**2 * end_y

            # Add tiny random jitter
            jitter = random.uniform(-2, 2)
            x += jitter
            y += jitter

            pynput_mouse.position = (int(x), int(y))
            self.vsleep(step_delay)
