import shap
import lime.lime_tabular
import numpy as np

class ExplainabilityService:
    def __init__(self, model, X_train):
        self.model = model
        self.X_train = X_train

    def shap_explain(self, X):
        explainer = shap.Explainer(self.model, self.X_train)
        shap_values = explainer(X)
        return shap_values.values.tolist()

    def lime_explain(self, X, feature_names=None):
        explainer = lime.lime_tabular.LimeTabularExplainer(
            self.X_train,
            feature_names=feature_names,
            class_names=['class_0', 'class_1'],
            discretize_continuous=True
        )
        explanations = []
        for i in range(X.shape[0]):
            exp = explainer.explain_instance(X[i], self.model.predict_proba, num_features=X.shape[1])
            explanations.append(exp.as_list())
        return explanations 