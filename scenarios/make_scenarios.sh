
# selecting the period 1979-2015
cdo -selyear,1979/2015 /scratch-shared/edwin/05min_runs_for_gmd_paper_30_oct_2017/05min_runs_4LCs_accutraveltime_cru-forcing_1958-2015/non-natural_starting_from_1958/merged_1958_to_2015/totalRunoff_monthTot_output_1958-01-31_to_2015-12-31.nc totalRunoff_monthTot_output_1979-2015.nc &

wait

# selecting the year 2003 (dry year)
cdo -selyear,2003 totalRunoff_monthTot_output_1979-2015.nc totalRunoff_monthTot_output_2003.nc &

# selecting the year 2013 (wet year)
cdo -selyear,2013 totalRunoff_monthTot_output_1979-2015.nc totalRunoff_monthTot_output_2013.nc &

# calculate climatology average 1979-2015
cdo -ymonavg totalRunoff_monthTot_output_1979-2015.nc climatology_average_totalRunoff_monthTot_output_1979-2015.nc &

# calculate climatology minimum 1979-2015
cdo -ymonmin totalRunoff_monthTot_output_1979-2015.nc climatology_minimum_totalRunoff_monthTot_output_1979-2015.nc &

# calculate climatology maximum 1979-2015
cdo -ymonmax totalRunoff_monthTot_output_1979-2015.nc climatology_maximum_totalRunoff_monthTot_output_1979-2015.nc &

wait

# calculate climatology percentile 20 1979-2015
cdo -L -ymonpctl,20 totalRunoff_monthTot_output_1979-2015.nc climatology_minimum_totalRunoff_monthTot_output_1979-2015.nc climatology_maximum_totalRunoff_monthTot_output_1979-2015.nc climatology_percentile20_totalRunoff_monthTot_output_1979-2015.nc &

# calculate climatology percentile 20 1979-2015
cdo -L -ymonpctl,80 totalRunoff_monthTot_output_1979-2015.nc climatology_minimum_totalRunoff_monthTot_output_1979-2015.nc climatology_maximum_totalRunoff_monthTot_output_1979-2015.nc climatology_percentile80_totalRunoff_monthTot_output_1979-2015.nc &

wait

