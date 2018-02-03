set - x

# climatology average
python estimate_discharge_from_local_runoff.py /scratch-shared/edwinvua/data_for_diede/netcdf_process/climatology_average/ /scratch-shared/edwinvua/data_for_diede/runoff_scenarios/climatology_average_totalRunoff_monthTot_output_1979-2015.nc 2015-01-31 2015-12-31 &

# year 2003 (dry year)
python estimate_discharge_from_local_runoff.py /scratch-shared/edwinvua/data_for_diede/netcdf_process/2003/ /scratch-shared/edwinvua/data_for_diede/runoff_scenarios/totalRunoff_monthTot_output_2003.nc 2003-01-31 2003-12-31 &

# year 2013 (wet year)
python estimate_discharge_from_local_runoff.py /scratch-shared/edwinvua/data_for_diede/netcdf_process/2013/ /scratch-shared/edwinvua/data_for_diede/runoff_scenarios/totalRunoff_monthTot_output_2013.nc 2013-01-31 2013-12-31 &

# climatology percentile 20 1979-2015
python estimate_discharge_from_local_runoff.py /scratch-shared/edwinvua/data_for_diede/netcdf_process/climatology_percentile20/ /scratch-shared/edwinvua/data_for_diede/runoff_scenarios/climatology_percentile20_totalRunoff_monthTot_output_1979-2015.nc 2015-01-31 2015-12-31 &

# climatology percentile 50 1979-2015 (median)
python estimate_discharge_from_local_runoff.py /scratch-shared/edwinvua/data_for_diede/netcdf_process/climatology_percentile50/ /scratch-shared/edwinvua/data_for_diede/runoff_scenarios/climatology_percentile50_totalRunoff_monthTot_output_1979-2015.nc 2015-01-31 2015-12-31 &

# climatology percentile 80 1979-2015
python estimate_discharge_from_local_runoff.py /scratch-shared/edwinvua/data_for_diede/netcdf_process/climatology_percentile80/ /scratch-shared/edwinvua/data_for_diede/runoff_scenarios/climatology_percentile80_totalRunoff_monthTot_output_1979-2015.nc 2015-01-31 2015-12-31 &

# full time series 1979-2015
python estimate_discharge_from_local_runoff.py /scratch-shared/edwinvua/data_for_diede/netcdf_process/1979-2015/ /scratch-shared/edwinvua/data_for_diede/runoff_scenarios/totalRunoff_monthTot_output_1979-2015.nc 1979-01-31 2015-12-31 &

wait
