UPDATE [dbo].[activity_data]
SET running_efficiency_index = 
  ROUND(
    100000.0 / (
      (
        CAST(LEFT(grade_adjusted_avg_pace_min_per_km, CHARINDEX(':', grade_adjusted_avg_pace_min_per_km) - 1) AS FLOAT) + 
        CAST(RIGHT(grade_adjusted_avg_pace_min_per_km, LEN(grade_adjusted_avg_pace_min_per_km) - CHARINDEX(':', grade_adjusted_avg_pace_min_per_km)) AS FLOAT) / 60.0
      ) * avg_heart_rate
    ), 2
  )
WHERE 
  grade_adjusted_avg_pace_min_per_km IS NOT NULL
  AND CHARINDEX(':', grade_adjusted_avg_pace_min_per_km) > 0