"""Common utilities for analyzing the radiation pattern of the Marlin antenna
boards.
"""

from enum import StrEnum

import numpy as np
import pandas as pd


class RadiationPatternSlice(StrEnum):
    """Radiation pattern slice enumeration."""
    AZIMUTH = "azimuth"
    ELEVATION = "elevation"


def prune_hfss_simulation_result(hfss_df: pd.DataFrame,
                                 slice: RadiationPatternSlice) -> pd.DataFrame:
    """Prunes the HFSS simulation result dataframe.

    Args:
        hfss_df: HFSS simulation result dataframe.
        slice: Radiation pattern slice.

    Returns:
        A dataframe containing the frequency, the angle, and the antenna gain.
    """
    (
        frequency_column,
        azimuth_column,
        elevation_column,
        *data_columns,
    ) = hfss_df.columns

    # In the HFSS design, the elevation is swept from the boresight from 0
    # degrees to 180 degrees, so to get the full radiation pattern for the
    # forward hemisphere, combine the elevation data from 0 to 90 degrees for
    # opposing azimuths.
    # For azimuth slices, -90 degrees refers to the left while +90 degrees
    # refers to the right relative to the boresight. For elevation slices, -90
    # degrees refers to below the boresight while +90 degrees refers to above
    # the boresight.
    pruned_df = hfss_df.copy()
    match slice:
        case RadiationPatternSlice.AZIMUTH:
            pruned_df = pruned_df[pruned_df[azimuth_column] % 180 == 0]
            pruned_df = pruned_df[pruned_df[elevation_column] <= 90]

            azimuth_0_mask = np.isclose(pruned_df[azimuth_column], 0)
            pruned_df.loc[azimuth_0_mask, elevation_column] *= -1

            # At boresight, azimuth=0 and azimuth=180 point in the same
            # direction, so only keep the azimuth=0 value.
            boresight_mask = (np.isclose(pruned_df[elevation_column], 0) &
                              ~np.isclose(pruned_df[azimuth_column], 0))
            pruned_df = pruned_df[~boresight_mask]
        case RadiationPatternSlice.ELEVATION:
            pruned_df = pruned_df[pruned_df[azimuth_column] % 180 != 0]
            pruned_df = pruned_df[pruned_df[elevation_column] <= 90]
            azimuth_270_mask = pruned_df[azimuth_column] == -90
            pruned_df.loc[azimuth_270_mask, elevation_column] *= -1

            # At boresight, azimuth=-90 and azimuth=90 point in the same
            # direction, so only keep the azimuth=90 value.
            boresight_mask = (np.isclose(pruned_df[elevation_column], 0) &
                              np.isclose(pruned_df[azimuth_column], -90))
            pruned_df = pruned_df[~boresight_mask]
        case _:
            raise ValueError(f"Invalid radiation pattern slice: {slice}.")
    return pruned_df[[frequency_column, elevation_column,
                      *data_columns]].sort_values(by=elevation_column)
