from typing import Dict

from gtrends.ml import load_engine
from gtrends.models import MLModel, MLModelVersion
from gtrends.tasks import (
    build_x_latest,
    load_data,
    preprocess,
    save_mlmodelversion,
    train,
)


def train_pipeline(ml_model: MLModel) -> MLModelVersion:
    target_ts = ml_model.data_config.targets.all()
    feature_ts = ml_model.data_config.features.all()
    prep_params = ml_model.preprocess_config.params
    model_params = ml_model.ml_config.params

    data, metadata = load_data(target_ts, feature_ts)
    x, y = preprocess(data, prep_params)
    engine = train(x, y, model_params)
    ml_model_version = save_mlmodelversion(engine, ml_model, metadata)

    return ml_model_version


def inference_pipeline(ml_model: MLModel) -> Dict:
    if ml_model.mlmodelversion_set.count() == 0:
        raise ValueError("No model has been trained yet!")

    target_ts = ml_model.data_config.targets.all()
    feature_ts = ml_model.data_config.features.all()
    prep_params = ml_model.preprocess_config.params

    data, _ = load_data(target_ts, feature_ts)
    x = build_x_latest(data, prep_params)
    engine = load_engine(ml_model.mlmodelversion_set.last().ml_file.path)
    y_pred = engine.predict(x)

    # Format predictions.
    horizon = ml_model.preprocess_config.params["horizon"]
    preds = {
        name: {"last_date": time, "prediction": pred, "horizon": horizon}
        for time, name, pred in zip(
            x.index.get_level_values("time"),
            x.index.get_level_values("ts_name"),
            y_pred,
        )
    }

    for k, v in preds.items():
        last_value = data["targets"][k].loc[v["last_date"]]["value"].item()
        preds[k]["last_value"] = last_value
        preds[k]["predicted_delta"] = v["prediction"] - last_value

    return preds
