import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartq.settings')
django.setup()

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from queues import ml_model


def main():
    rows, targets = ml_model.build_dataset()
    real_count = len(targets)
    print(f'Real historical samples from PostgreSQL: {real_count}')

    if real_count < 50:
        sim_rows, sim_targets = ml_model.simulate_history()
        rows = rows + sim_rows
        targets = targets + sim_targets
        print(f'Augmented with simulated history: {len(targets)} total samples')

    X = np.array(rows, dtype=float)
    y = np.array(targets, dtype=float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    ml_mae = mean_absolute_error(y_test, model.predict(X_test))

    rule_pred = (X_test[:, 0] * X_test[:, 1]) / np.maximum(X_test[:, 2], 1)
    rule_mae = mean_absolute_error(y_test, rule_pred)

    print('\n--- Waiting-Time Model Investigation (Section 4.2) ---')
    print(f'Rule-based MAE : {rule_mae:.2f} minutes')
    print(f'ML model MAE   : {ml_mae:.2f} minutes')

    if ml_mae < rule_mae:
        improvement = (rule_mae - ml_mae) / rule_mae * 100
        print(f'Result: ML improves accuracy by {improvement:.1f}% - ML estimate enabled in SmartQ.')
    else:
        print('Result: rule-based estimator remains more accurate on this data.')

    joblib.dump(model, ml_model.MODEL_PATH)
    print(f'\nModel successfully saved to {ml_model.MODEL_PATH}')


if __name__ == '__main__':
    main()