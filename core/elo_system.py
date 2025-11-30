"""
Hybrid ELO Difficulty System
----------------------------
Manages player skill rating and adapts AI difficulty dynamically.
"""
import json
import os
import math

class EloSystem:
    def __init__(self, save_file="data/player_rating.json"):
        self.save_file = save_file
        self.player_rating = 1000  # Lower default starting rating (was 1200)
        self.k_factor = 50         # Higher volatility (was 32) -> Adapts faster
        
        # AI Difficulty Parameters (Min/Max)
        self.min_speed = 2.0       # Slower (was 3.0)
        self.max_speed = 10.0      # Slower max (was 12.0)
        self.min_error = 10.0      # Even perfect AI makes small mistakes
        self.max_error = 150.0     # HUGE error margin (was 50.0) -> AI will miss a lot
        
        self.load_rating()
        
    def load_rating(self):
        """Load rating from file"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.player_rating = data.get('rating', 1200)
                    print(f"Loaded Player Rating: {self.player_rating}")
            except Exception as e:
                print(f"Error loading rating: {e}")
                
    def save_rating(self):
        """Save rating to file"""
        try:
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            with open(self.save_file, 'w') as f:
                json.dump({'rating': self.player_rating}, f)
        except Exception as e:
            print(f"Error saving rating: {e}")

    def update_rating(self, player_won):
        """
        Update rating after a point/game.
        Using simplified ELO: Expected win rate is 0.5 for balanced match.
        """
        actual_score = 1.0 if player_won else 0.0
        expected_score = 0.5 # We assume the AI *should* be matched to you
        
        # ELO Formula: R' = R + K * (Actual - Expected)
        change = self.k_factor * (actual_score - expected_score)
        self.player_rating += change
        
        # Clamp rating to reasonable bounds
        self.player_rating = max(100, min(3000, self.player_rating))
        
        self.save_rating()
        return change

    def get_ai_parameters(self):
        """
        Map current ELO to AI difficulty parameters.
        Higher Rating -> Faster AI, Less Error.
        """
        # Normalize rating between 0.0 (800) and 1.0 (2000)
        # We cap "Perfect AI" at 2000 ELO
        normalized = (self.player_rating - 800) / (2000 - 800)
        normalized = max(0.0, min(1.0, normalized))
        
        # Calculate Speed (Linear interpolation)
        speed = self.min_speed + (self.max_speed - self.min_speed) * normalized
        
        # Calculate Error (Inverse interpolation - Higher rating = Lower error)
        error = self.max_error - (self.max_error - self.min_error) * normalized
        
        return {
            'speed': speed,
            'error_margin': error,
            'reaction_delay': max(0, 15 - int(normalized * 15)) # 15 frames delay (was 10)
        }
