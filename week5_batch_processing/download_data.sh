
set -e  # quit when the wget returns the first 404 error (the first non-0 code)

URL_PREFIX="https://github.com/DataTalksClub/nyc-tlc-data/releases/download"

for TAXI_TYPE in "yellow" "green"
do
    for YEAR in 2020 2021
    do
        for MONTH in {1..12}
        do

        if [ $YEAR == 2020 ] || [ $MONTH -lt 8 ]
        then
            # Add a 0 to the month digit with a %02d template
            FMONTH=`printf "%02d" ${MONTH}`
            # echo ${FMONTH}

            URL="${URL_PREFIX}/${TAXI_TYPE}/${TAXI_TYPE}_tripdata_${YEAR}-${FMONTH}.csv.gz"

            LOCAL_PREFIX="data/raw/${TAXI_TYPE}/${YEAR}/${FMONTH}"
            LOCAL_FILE="${TAXI_TYPE}_tripdata_${YEAR}_${FMONTH}.csv.gz"
            LOCAL_PATH="${LOCAL_PREFIX}/${LOCAL_FILE}"

            echo "Downloading ${URL} to ${LOCAL_PATH}"
            mkdir -p ${LOCAL_PREFIX}  # create the directory to store the data
            wget ${URL} -O ${LOCAL_PATH}

            # # IF DOWNLOADING CSV DIRECTLY, zip/compress/archive the data
            # echo "Compressing ${LOCAL_PATH}"
            # gzip ${LOCAL_PATH}
        fi
        done
    done
done

# run via `./download_data.sh`