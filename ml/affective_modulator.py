"""
Affective Modulator (Stub)
--------------------------
Adjusts game difficulty based on player state (Emotion/Frustration).
Currently implements a 'Pity System' based on loss streaks.
"""

class AffectiveModulator:
    def __init__(self):
        self.loss_streak = 0
        self.frustration_level = 0.0 # 0.0 to 1.0
        
    def update_outcome(self, player_won):
        """Update state based on game outcome"""
        if player_won:
            self.loss_streak = 0
            self.frustration_level = max(0.0, self.frustration_level - 0.5)
        else:
            self.loss_streak += 1
            self.frustration_level = min(1.0, self.frustration_level + 0.2)
            
    def update_emotion(self, emotion, valence, arousal):
        """
        Update state based on real-time emotion detection.
        Frustrated/Angry -> Increase Frustration
        Happy/Calm -> Decrease Frustration
        """
        if emotion == "Frustrated":
            self.frustration_level = min(1.0, self.frustration_level + 0.05)
        elif emotion == "Happy":
            self.frustration_level = max(0.0, self.frustration_level - 0.05)
            
        # High arousal + Negative valence = Stress
        if arousal > 0.6 and valence < -0.2:
             self.frustration_level = min(1.0, self.frustration_level + 0.02)
            
    def get_difficulty_modifier(self):
        """
        Return a multiplier for AI difficulty.
        High frustration -> Lower difficulty (Multiplier < 1.0)
        """
        # Pity Mode (Loss Streak)
        if self.loss_streak >= 3:
            print(f"🥺 Pity Mode Active! (Streak: {self.loss_streak})")
            return 0.2 # Make AI 5x clumsier
            
        # Emotional Support Mode (Frustration)
        # If player looks frustrated (> 0.7), reduce difficulty
        if self.frustration_level > 0.7:
            return 0.5 # Make AI 2x clumsier
        
        return 1.0
