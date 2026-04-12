from abc import ABC, abstractmethod
import pandas as pd

class BaseModel(ABC):
    @abstractmethod
    def predict(self, df: pd.DataFrame) -> float:
        """
        Processes market data and returns a prediction.
        
        Args:
            df (pd.DataFrame): Input dataframe containing candles and/or feature data.
            
        Returns:
            float: A prediction value (e.g., expected return, signal strength, or price).
        """
        pass

"""
class RSIMessageModel(BaseModel):
    def predict(self, df: pd.DataFrame) -> float:
        # Simplified logic: return the last RSI value as a float
        return float(df['rsi'].iloc[-1])

# This would raise a TypeError if predict() was not defined
model = RSIMessageModel()
"""