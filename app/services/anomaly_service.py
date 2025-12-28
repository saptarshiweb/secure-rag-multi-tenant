from sklearn.ensemble import IsolationForest
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        # Dictionary to store one Isolation Forest model per tenant
        self.models = {} 
        # History of query embeddings per tenant to train the models
        self.history = defaultdict(list) 
        # Minimum samples required before we start flagging anomalies
        self.min_samples_to_train = 5

    def log_query(self, tenant_id: str, embedding: list[float]):
        """
        Logs a query embedding for a tenant and retrains the model if enough data is collected.
        """
        self.history[tenant_id].append(embedding)
        
        # In a real system, training would be async/background job.
        # For PoC, we check and train inline if we hit the threshold or periodically.
        # Here we retrain every time we get a new batch of data (simplified).
        if len(self.history[tenant_id]) >= self.min_samples_to_train:
            self._train_model(tenant_id)

    def _train_model(self, tenant_id: str):
        try:
            data = np.array(self.history[tenant_id])
            # contamination='auto' or a small float (e.g., 0.05) for 5% expected anomalies
            clf = IsolationForest(random_state=42, contamination=0.1) 
            clf.fit(data)
            self.models[tenant_id] = clf
            logger.info(f"Updated Anomaly Detection model for tenant {tenant_id}")
            print(f"DEBUG: Trained anomaly model for {tenant_id} with {len(data)} samples.")
        except Exception as e:
            logger.error(f"Failed to train anomaly model for {tenant_id}: {e}")

    def is_anomalous(self, tenant_id: str, embedding: list[float]) -> bool:
        """
        Returns True if the query is statistically anomalous for this tenant.
        """
        if tenant_id not in self.models:
            # Not enough data yet to judge. Fail open (allow).
            return False
            
        # Reshape for single sample prediction
        prediction = self.models[tenant_id].predict([embedding])
        
        # IsolationForest returns -1 for anomaly, 1 for normal
        is_anomaly = prediction[0] == -1
        
        if is_anomaly:
            logger.warning(f"Anomaly detected for tenant {tenant_id}!")
            
        return is_anomaly
