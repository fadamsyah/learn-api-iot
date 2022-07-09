#!/bin/bash
function close_port {
    kill $(lsof -t -i:8080)
    kill $(lsof -t -i:5672)
    kill $(lsof -t -i:5001)
}
trap close_port EXIT
close_port
conda activate api-iot
python src/dht-api-data.py &
python src/dht-db.py &
python src/arduino.py &
sleep 5
streamlit run src/dht-app.py --server.port 8080 &
wait