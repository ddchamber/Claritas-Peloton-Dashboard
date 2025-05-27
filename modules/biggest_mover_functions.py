import pandas as pd
import numpy as np


import pandas as pd
import numpy as np

def dma_change(df: pd.DataFrame,
               start_date: str = None,
               end_date: str = None,
               action: str = None,
               start_count: int = None,  # not used, just for interface compatibility
               end_count: int = None) -> pd.DataFrame:
    """
    Computes start and end hitCounts and weighted percent change per DMA.

    Returns:
        pd.DataFrame: ['dma', 'start_date', 'end_date', 'start_count', 'end_count', 'weighted_pct_change']
    """
    df = df.copy()

    start = pd.to_datetime(start_date) if start_date else df['date'].min()
    end = pd.to_datetime(end_date) if end_date else df['date'].max()

    if action:
        df = df[df['action'] == action]

    # Group hitCount by DMA
    start_group = df[df['date'] == start].groupby('dma')['hitCount'].sum().rename('start_count')
    end_group = df[df['date'] == end].groupby('dma')['hitCount'].sum().rename('end_count')

    combined = pd.concat([start_group, end_group], axis=1).fillna(0)
    combined['weighted_pct_change'] = (
        (combined['end_count'] - combined['start_count']) / combined['start_count']
    ) * 100 * np.log1p(combined['start_count'])

    combined.loc[combined['start_count'] == 0, 'weighted_pct_change'] = np.nan
    combined = combined.reset_index()

    combined['start_date'] = start.strftime('%Y-%m-%d')
    combined['end_date'] = end.strftime('%Y-%m-%d')

    combined['abs_change'] = combined['weighted_pct_change'].abs()
    result = combined.sort_values('abs_change', ascending=False).drop(columns='abs_change').reset_index(drop=True)

    return result




def prizm_change(df_peloton: pd.DataFrame,
                 df_prizm: pd.DataFrame,
                 start_date: str = None,
                 end_date: str = None,
                 action: str = None,
                 start_count: int = None,
                 end_count: int = None) -> pd.DataFrame:
    """
    Calculates weighted percent change in hitCount per PRIZM segment between two dates.

    Returns:
        pd.DataFrame: ['segment', 'start_date', 'end_date', 'start_count', 'end_count', 'weighted_pct_change']
    """
    pel = df_peloton.copy()
    prizm = df_prizm.copy()

    # Prepare PRIZM fractions
    prizm_frac = prizm.set_index('DMA_GCODE').div(100)

    # Parse date bounds
    pel['date'] = pd.to_datetime(pel['date'])
    start = pd.to_datetime(start_date) if start_date else pel['date'].min()
    end = pd.to_datetime(end_date) if end_date else pel['date'].max()

    if action:
        pel = pel[pel['action'] == action]

    # Aggregate hitCounts by DMA
    start_dma = pel[pel['date'] == start].groupby('dma')['hitCount'].sum()
    end_dma = pel[pel['date'] == end].groupby('dma')['hitCount'].sum()

    # Join and fill missing DMAs
    dma_counts = pd.concat([start_dma, end_dma], axis=1).fillna(0)
    dma_counts.columns = ['start_count', 'end_count']

    # Allocate to PRIZM segments
    start_seg = prizm_frac.mul(dma_counts['start_count'], axis=0).sum(axis=0)
    end_seg = prizm_frac.mul(dma_counts['end_count'], axis=0).sum(axis=0)

    seg_df = pd.concat([start_seg, end_seg], axis=1)
    seg_df.columns = ['start_count', 'end_count']

    seg_df['weighted_pct_change'] = (
        (seg_df['end_count'] - seg_df['start_count']) / seg_df['start_count']
    ) * 100 * np.log1p(seg_df['start_count'])

    seg_df.loc[seg_df['start_count'] == 0, 'weighted_pct_change'] = np.nan

    seg_df = seg_df.reset_index().rename(columns={'index': 'segment'})
    seg_df['start_date'] = start.strftime('%Y-%m-%d')
    seg_df['end_date'] = end.strftime('%Y-%m-%d')

    seg_df['abs_change'] = seg_df['weighted_pct_change'].abs()
    result = seg_df.sort_values('abs_change', ascending=False).drop(columns='abs_change').reset_index(drop=True)
    return result


def main():
    import pandas as pd

    df_peloton_grouped = pd.read_csv('/Users/lewk20/Desktop/MSBA/Spring/Claritas/created_data/peloton_dma_grouped.csv')
    df_peloton_grouped['date'] = pd.to_datetime(df_peloton_grouped['date'])

    df_peloton = pd.read_csv('/Users/lewk20/Desktop/MSBA/Spring/Claritas/created_data/peloton_dma.csv')
    df_peloton['date'] = pd.to_datetime(df_peloton['date'])

    df_prizm = pd.read_excel("/Users/lewk20/Desktop/MSBA/Spring/Claritas/base_data/PRIZM2DMA.xlsx")
    cols_to_pct = [col for col in df_prizm.columns if col != 'DMA_GCODE']
    row_sums = df_prizm[cols_to_pct].sum(axis=1)
    df_prizm[cols_to_pct] = df_prizm[cols_to_pct].div(row_sums, axis=0) * 100


    # Test DMA Change
    print("=== DMA Change ===")
    dma_result = dma_change(
        df=df_peloton_grouped,
        start_date="2025-01-01",  # Example date
        end_date=None,
        action=None             # Or None
    )
    print(dma_result.head())

    # Test PRIZM Change
    print("\n=== PRIZM Change ===")
    prizm_result = prizm_change(
        df_peloton=df_peloton,
        df_prizm=df_prizm,
        start_date="2025-01-01",  # Example date
        end_date=None,
        action=None           # Or None
    )
    print(prizm_result.head())


if __name__ == "__main__":
    main()