"""Mixture distribution implementation for skewed distributions"""

import numpy as np


class MixtureDistribution:
    """Simple mixture of distributions for modeling skewed bid distributions"""
    
    def __init__(self, components, weights):
        """
        Initialize mixture distribution
        
        Args:
            components: List of scipy distribution objects
            weights: List of weights (should sum to 1)
        """
        self.components = components
        self.weights = np.array(weights) / np.sum(weights)  # Normalize weights
    
    def pdf(self, x):
        """Probability density function"""
        result = np.zeros_like(x, dtype=float)
        for component, weight in zip(self.components, self.weights):
            result += weight * component.pdf(x)
        return result
    
    def cdf(self, x):
        """Cumulative distribution function"""
        result = np.zeros_like(x, dtype=float)
        for component, weight in zip(self.components, self.weights):
            result += weight * component.cdf(x)
        return result
    
    def mean(self):
        """Expected value of the mixture"""
        result = 0
        for component, weight in zip(self.components, self.weights):
            result += weight * component.mean()
        return result
    
    def std(self):
        """Standard deviation of the mixture (approximate)"""
        # Use law of total variance for approximation
        mean_of_means = self.mean()
        
        # E[Var(X|Z)] - expected variance
        expected_variance = 0
        for component, weight in zip(self.components, self.weights):
            expected_variance += weight * (component.std() ** 2)
        
        # Var(E[X|Z]) - variance of means
        variance_of_means = 0
        for component, weight in zip(self.components, self.weights):
            variance_of_means += weight * ((component.mean() - mean_of_means) ** 2)
        
        total_variance = expected_variance + variance_of_means
        return np.sqrt(total_variance) 