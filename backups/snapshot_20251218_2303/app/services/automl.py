from tpot import TPOTClassifier
import numpy as np

class AutoMLService:
    def __init__(self, generations=5, population_size=20, random_state=42):
        self.generations = generations
        self.population_size = population_size
        self.random_state = random_state

    def run(self, X, y):
        automl = TPOTClassifier(generations=self.generations, population_size=self.population_size, verbosity=2, random_state=self.random_state, config_dict='TPOT light')
        automl.fit(X, y)
        return {
            'score': automl.score(X, y),
            'pipeline': automl.fitted_pipeline_.steps
        } 