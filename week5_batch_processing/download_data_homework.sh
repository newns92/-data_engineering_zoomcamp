
set -e

URL_PREFIX="https://github.com/DataTalksClub/nyc-tlc-data/releases/download"

TAXI_TYPE="fhvhv"
YEAR=2021
MONTH=06

FMONTH=`printf "%02d" ${MONTH}`

URL="${URL_PREFIX}/${TAXI_TYPE}/${TAXI_TYPE}_tripdata_${YEAR}-${FMONTH}.csv.gz"

LOCAL_PREFIX="data/raw/${TAXI_TYPE}/${YEAR}/${FMONTH}"
LOCAL_FILE="${TAXI_TYPE}_tripdata_${YEAR}_${FMONTH}.csv.gz"
LOCAL_PATH="${LOCAL_PREFIX}/${LOCAL_FILE}"

echo "Downloading ${URL} to ${LOCAL_PATH}"
mkdir -p ${LOCAL_PREFIX}
wget ${URL} -O ${LOCAL_PATH}


# run via `./download_data_homework.sh`