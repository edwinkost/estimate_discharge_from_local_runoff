
set -x

# go to the working directory
cd /scratch-shared/edwinvua/data_for_diede/subcatchment_map

# clean existing pcraster maps
rm *.map

# copy ldd map as the reference/clone map
cp /projects/0/dfguu/data/hydroworld/PCRGLOBWB20/input5min/routing/lddsound_05min.map .

# manually - prepare a column file of "station_pcraster_ids.txt"
# - Based on Will's excel table (see e.g. the sheet "GeneratorsUpdate_Edwin20170824" of https://github.com/edwinkost/estimate_discharge_from_local_runoff/blob/master/data/table_from_will.xlsx). 
# - The column file contains the power station (lat/lon) coordinates based on PCR-GLOBWB river network.   
# - The table should be sorted based on the hydro power capacities. In this case, largest power stations are prioritized with their nearby smaller ones falling in the same cells are merged.   
 
# convert the column file to pcraster maps
col2map --progress --clone lddsound_05min.map -S -M -x 2 -y 1 -v 3 station_pcraster_ids.txt station_pcraster_ids.map
pcrcalc station_pcraster_ids.nom.map = "nominal(station_pcraster_ids.map)"

# making the subcatchment maps
pcrcalc subcatchments_of_station_pcraster_ids.nom.map = "subcatchment(lddsound_05min.map, station_pcraster_ids.nom.map)"
pcrcalc subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map = "if(scalar(subcatchments_of_station_pcraster_ids.nom.map) gt 0, subcatchments_of_station_pcraster_ids.nom.map)"

# identify downstream ids
pcrcalc downstreams_of_subcatchments_of_station_pcraster_ids.nom.map = "if(defined(station_pcraster_ids.nom.map), downstream(lddsound_05min.map, subcatchments_of_station_pcraster_ids.nom.map))"

# make a table/column file listing stations and their downstream ones
map2col station_pcraster_ids.nom.map downstreams_of_subcatchments_of_station_pcraster_ids.nom.map stations_and_their_downstreams_version_20170824.txt

# manually - prepare a clone map (in order to reduce sizes of output netcdf files)
pcrcalc xmin.map = "mapminimum(xcoordinate(defined(subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map)))"
pcrcalc xmax.map = "mapmaximum(xcoordinate(defined(subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map)))"
pcrcalc ymin.map = "mapminimum(ycoordinate(defined(subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map)))"
pcrcalc ymax.map = "mapmaximum(ycoordinate(defined(subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map)))"
mapattr -p xmin.map ymin.map xmax.map ymax.map
mapattr -p xmin.map ymin.map xmax.map ymax.map > corner_coordinates.txt
geany corner_coordinates.txt &
mapattr clone_version_20170824.map
gdalinfo clone_version_20170824.map




