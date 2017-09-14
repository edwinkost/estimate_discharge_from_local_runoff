
set -x

# go to the working directory
cd /scratch-shared/edwinhs/data_for_will/subcatchment_maps

# clean existing pcraster maps
rm *.map

# copy ldd map as the reference/clone map
cp /projects/0/dfguu/data/hydroworld/PCRGLOBWB20/input5min/routing/lddsound_05min.map .

# manually - prepare a column file of "reservoir_pcraster_ids.txt"
# - Based on Will's excel table (see e.g. the sheet "GeneratorsUpdate_Edwin20170824" of https://github.com/edwinkost/estimate_discharge_from_local_runoff/blob/master/data/table_from_will.xlsx). 
# - The column file contains the coordinates (lat/lon) of reservoir outlets. 
# - The table should be sorted based on the upper reservoir capacity (largest to smallest), upper reservoir name (A to Z) and power station ID (smallest to largest). In this case, largest reservoirs are prioritized with their nearby smaller reservoirs that are falling in the same cells are merged.   
 
# convert the column file to pcraster maps
col2map --progress --clone lddsound_05min.map -S -M -x 2 -y 1 -v 3 reservoir_pcraster_ids.txt reservoir_pcraster_ids.map
pcrcalc reservoir_pcraster_ids.nom.map = "nominal(reservoir_pcraster_ids.map)"

# making the subcatchment maps
pcrcalc subcatchments_of_reservoir_pcraster_ids.nom.map = "subcatchment(lddsound_05min.map, reservoir_pcraster_ids.nom.map)"
pcrcalc subcatchments_of_reservoir_pcraster_ids.nom.bigger_than_zero.map = "if(scalar(subcatchments_of_reservoir_pcraster_ids.nom.map) gt 0, subcatchments_of_reservoir_pcraster_ids.nom.map)"

# identify downstream reservoirs
pcrcalc downstreams_of_subcatchments_of_reservoir_pcraster_ids.nom.map = "if(defined(reservoir_pcraster_ids.nom.map), downstream(lddsound_05min.map, subcatchments_of_reservoir_pcraster_ids.nom.map))"

# make a table/column file listing reservoirs and their downstream ones
map2col reservoir_pcraster_ids.nom.map downstreams_of_subcatchments_of_reservoir_pcraster_ids.nom.map reservoirs_and_their_downstreams_version_20170824.txt

# manually - prepare a clone map (in order to reduce sizes of output netcdf files)
pcrcalc xmin.map = "mapminimum(xcoordinate(defined(subcatchments_of_reservoir_pcraster_ids.nom.bigger_than_zero.map)))"
pcrcalc xmax.map = "mapmaximum(xcoordinate(defined(subcatchments_of_reservoir_pcraster_ids.nom.bigger_than_zero.map)))"
pcrcalc ymin.map = "mapminimum(ycoordinate(defined(subcatchments_of_reservoir_pcraster_ids.nom.bigger_than_zero.map)))"
pcrcalc ymax.map = "mapmaximum(ycoordinate(defined(subcatchments_of_reservoir_pcraster_ids.nom.bigger_than_zero.map)))"
mapattr -p xmin.map ymin.map xmax.map ymax.map
mapattr -p xmin.map ymin.map xmax.map ymax.map > corner_coordinates.txt
geany corner_coordinates.txt &
mapattr clone_version_20170824.map
gdalinfo clone_version_20170824.map
