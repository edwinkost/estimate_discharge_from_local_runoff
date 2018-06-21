
set -x

#~ # go to the working directory
#~ cd /scratch-shared/edwinvua/data_for_diede/subcatchment_map

# clean existing pcraster maps
rm *.map

# copy ldd map as the reference/clone map
cp /projects/0/dfguu/data/hydroworld/PCRGLOBWB20/input5min/routing/lddsound_05min.map .

# manually - prepare a column file of "station_pcraster_ids.txt"
# - Based on Will's excel table (see e.g. the sheet "GeneratorsUpdate_Edwin20180202" of https://github.com/edwinkost/estimate_discharge_from_local_runoff/blob/master/data/table_from_will.xlsx). 
# - The column file contains the power station (lat/lon) coordinates based on PCR-GLOBWB river network.   
# - The table should be sorted, e.g. based on hydro power capacities. In this case, largest power stations are prioritized with their nearby smaller ones falling in the same (5 arcmin) cells are merged.   
 
# convert the column file to pcraster maps
col2map --progress --clone lddsound_05min.map -S -M -x 3 -y 2 -v 1 station_pcraster_ids.txt station_pcraster_ids.map
pcrcalc station_pcraster_ids.nom.map = "nominal(station_pcraster_ids.map)"
aguila station_pcraster_ids.nom.map

# making the subcatchment maps
pcrcalc subcatchments_of_station_pcraster_ids.nom.map = "subcatchment(lddsound_05min.map, station_pcraster_ids.nom.map)"
pcrcalc subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map = "if(scalar(subcatchments_of_station_pcraster_ids.nom.map) gt 0, subcatchments_of_station_pcraster_ids.nom.map)"

# identify downstream ids
pcrcalc downstreams_of_subcatchments_of_station_pcraster_ids.nom.map = "if(defined(station_pcraster_ids.nom.map), downstream(lddsound_05min.map, subcatchments_of_station_pcraster_ids.nom.map))"

# make a table/column file listing stations and their downstream ones
map2col station_pcraster_ids.nom.map downstreams_of_subcatchments_of_station_pcraster_ids.nom.map stations_and_their_downstreams_version_20180202.txt



# making clone maps
#########################################


# making the 'path" and catcment maps from the subcatchment map
pcrcalc path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map = "path(lddsound_05min.map, defined(subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map))"
pcrcalc catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map = "catchment(lddsound_05min.map, path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map)"
pcrcalc catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map = "if(catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map, catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map)"
# - extend until 1 arc degree
pcrcalc catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map = "cover(catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map, boolean(windowmaximum(scalar(catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map), 1.0)))"
aguila catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map


# manually - prepare a clone map (in order to reduce sizes of output netcdf files)
pcrcalc xmin.map = "mapminimum(xcoordinate(defined(catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map)))"
pcrcalc xmax.map = "mapmaximum(xcoordinate(defined(catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map)))"
pcrcalc ymin.map = "mapminimum(ycoordinate(defined(catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map)))"
pcrcalc ymax.map = "mapmaximum(ycoordinate(defined(catchment_path_subcatchments_of_station_pcraster_ids.nom.bigger_than_zero.map)))"
mapattr -p xmin.map ymin.map xmax.map ymax.map
mapattr -p xmin.map ymin.map xmax.map ymax.map > corner_coordinates.txt
geany corner_coordinates.txt &
mapattr clone_version_20180202.map
gdalinfo clone_version_20180202.map




