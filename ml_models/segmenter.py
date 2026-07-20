import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

class CustomerSegmenter:
    def __init__(self, n_clusters=3, random_state=42):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init='auto')
        self.feature_cols = ['TenureMonths', 'TotalSpend']
        self.is_fitted = False

    def fit_predict(self, df: pd.DataFrame):
        """
        Fits the scaler and KMeans model on customers.
        Returns a DataFrame with appended 'Cluster' and 'ClusterLabel' columns.
        """
        if len(df) < self.n_clusters:
            raise ValueError(f"Insufficient customer records for clustering. Need at least {self.n_clusters} samples.")
            
        X = df[self.feature_cols].copy()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit and Predict
        clusters = self.model.fit_predict(X_scaled)
        
        # Silhouette Score
        sil_score = silhouette_score(X_scaled, clusters)
        
        result_df = df.copy()
        result_df['Cluster'] = clusters
        
        # Interpret clusters based on center spend
        centers = self.model.cluster_centers_
        # Inverse transform to get real centers
        real_centers = self.scaler.inverse_transform(centers)
        
        # Sort clusters by spend (ascending) to assign meaningful labels
        # e.g., index 0 = lowest spend, index 2 = highest spend
        spend_idx = 1 # index of TotalSpend
        sorted_clusters_by_spend = np.argsort(real_centers[:, spend_idx])
        
        label_mapping = {
            sorted_clusters_by_spend[0]: "Low Value / At Risk",
            sorted_clusters_by_spend[1]: "Mid Value / Core",
            sorted_clusters_by_spend[2]: "High Value / Champions"
        }
        
        result_df['ClusterLabel'] = result_df['Cluster'].map(label_mapping)
        self.is_fitted = True
        
        metrics = {
            "SilhouetteScore": float(sil_score),
            "Inertia": float(self.model.inertia_),
            "ClusterCenters": real_centers.tolist()
        }
        
        return result_df, metrics
