
# clean existing pcraster maps
rm *.map

# copy ldd map as the reference/clone map
cp /projects/0/dfguu/data/hydroworld/PCRGLOBWB20/input5min/routing/lddsound_05min.map .

# manually - prepare a column file of "reservoir_pcraster_ids.txt"
# - Based on Will's excel table (see e.g. ). 
# - The table should be sorted based on the upper reservoir capacity (largest to smallest), upper reservoir name (A to Z) and power station ID (smallest to largest). In this case, largest reservoirs will be prioritized with their nearby smaller reservoirs will be merged.   
 

# convert the column file to a pcraster map (scalar)
col2map --progress --clone lddsound_05min.map -S -l -x 2 -y 1 -v 3 reservoir_pcraster_ids.txt reservoir_pcraster_ids.map

# 
