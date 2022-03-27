## Putting this work on hold due to performance issues it will cause

### Commands to run in Flask Shell to create workout point from a pickle file
```
import pandas as pd
import numpy as np
from app.model.workout_point import Workout_point

df = pd.read_pickle('/Users/mikeyb/Dropbox/Apps/personal_site/wrkt_files/1/2022/03/2022-03-12_135649_running_coros/workout.pickle')

df['delta_ts_sec'] = df['delta_timestamp'].dt.total_seconds()
df.rename(columns={'latitude': 'lat', 'longitude':'lon', 'timestamp':'ts', 'altitude':'altitude_m'}, inplace=True)
df.replace({np.nan:None}, inplace=True)

wrkt_pt_dict = Workout_point.from_pt_lst_dict(df.to_dict('records'), '1', '1423')
```



df = pd.DataFrame(Workout_interval.to_intrvl_lst_dict(intrvl_lst))

data = df.head().to_dict('records')

# Performance differences using workout_point versus pickle file, pickle file is about 800ms faster
2022-03-26 19:53:47,054 - workout - INFO - Read Workout_point
2022-03-26 19:53:47,425 - workout - INFO - Start wrkt_df process
zoom: 15
center:{'lat': Decimal('40.6012146826833475'), 'lon': Decimal('-89.45605878252536')}
2022-03-26 19:53:47,916 - workout - INFO - End wrkt_df process

2022-03-26 19:54:44,492 - workout - INFO - Read Workout_point
2022-03-26 19:54:44,528 - workout - INFO - Start wrkt_df process
zoom: 15
center:{'lat': 40.75189502444118, 'lon': -89.59141507744789}
2022-03-26 19:54:44,572 - workout - INFO - End wrkt_df process


2022-03-26 19:57:20,096 - workout - INFO - Read Workout_point
zoom: 15
center:{'lat': 40.60121468268335, 'lon': -89.45605878252536}
2022-03-26 19:57:20,168 - workout - INFO - End wrkt_df process
