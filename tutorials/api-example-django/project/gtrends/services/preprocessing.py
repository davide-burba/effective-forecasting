from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import pandas as pd


class BasePreprocessor(ABC):
    @abstractmethod
    def build_x_y(self, data: Dict) -> Tuple[pd.DataFrame, pd.Series]:
        """Return features and target ready for training."""

    @abstractmethod
    def build_x_latest(self, data: Dict) -> pd.DataFrame:
        """Return only latest values of x, useful for inference"""


@dataclass
class Preprocessor(BasePreprocessor):
    horizon: int
    target_lags: List[int]
    feature_lags: List[int]

    def build_x_y(self, data: Dict) -> Tuple[pd.DataFrame, pd.Series]:
        # Build x and y.
        x = self.build_x(data)
        y = self.build_y(data["targets"])

        # Align x indexes with y indexes.
        x = pd.merge(y, x, left_index=True, right_index=True, how="left")
        x = x.iloc[:, 1:]

        # Drop missing values generated by lags/horizon.
        idx = ~(x.isnull().any(axis=1) | y.isnull())
        x = x.loc[idx]
        y = y.loc[idx]

        return x, y

    def build_x_latest(self, data: Dict) -> pd.DataFrame:
        x = self.build_x(data)
        return x[x.index == x.index.max()]

    def build_y(self, target_data: Dict) -> pd.DataFrame:
        y = {}
        for name, df in target_data.items():
            y[name] = (
                df["value"]
                .shift(-self.horizon)
                .rename(f"horizon_{self.horizon}")
            )
        return pd.concat(y.values())

    def build_x(self, data: Dict) -> pd.DataFrame:
        target_data = data["targets"]
        feature_data = data["features"]

        # Build x_target and x_features.
        x_targ = self._build_x_lags_targets(target_data)
        x_feat = self._build_x_lags_features(feature_data, target_data)

        # Combine x_target and x_features.
        if x_feat is None and x_targ is None:
            raise ValueError("Cannot have no target lags and no feature lags.")
        elif x_feat is None:
            return x_targ
        elif x_targ is None:
            return x_feat

        return pd.merge(
            x_targ, x_feat, left_index=True, right_index=True, how="left"
        )

    def _build_x_lags_targets(
        self, target_data: Dict
    ) -> Optional[pd.DataFrame]:
        if not self.target_lags:
            return None
        x = []
        for df in target_data.values():
            x.append(
                _build_lags(
                    df=df,
                    column="value",
                    lags=self.target_lags,
                    prefix="target",
                )
            )
        return pd.concat(x, axis=1)

    def _build_x_lags_features(
        self, feature_data: Dict, target_data: Dict
    ) -> Optional[pd.DataFrame]:
        if not self.feature_lags:
            return None
        x = []
        for name, df in feature_data.items():
            x.append(
                _build_lags(
                    df=df,
                    column="value",
                    lags=self.feature_lags,
                    prefix=name,
                )
            )
        # Concat features on axis 1.
        x = pd.concat(
            [df.reset_index().drop(columns=["ts_name"]) for df in x], axis=1
        )
        # Use target to "reindex" on axis 0.
        for_reindex = pd.concat(target_data.values(), axis=1).reset_index()
        x = pd.merge(for_reindex, x, how="left", on="time")
        return x.drop(columns=["value"]).set_index(["time", "ts_name"])


def _build_lags(
    df: pd.DataFrame, column: str, lags: List[int], prefix: str
) -> pd.DataFrame:
    return pd.concat(
        [
            df[[column]]
            .shift(lag)
            .rename(columns={column: f"{prefix}_lag_{lag}"})
            for lag in lags
        ],
        axis=1,
    )
