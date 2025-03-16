# Windows command
docker run --rm --name elasticsearch ^
  -d ^
  -p 127.0.0.1:9200:9200 ^
  -e http.port=9200 ^
  -e discovery.type=single-node ^
  -e http.max_content_length=10MB ^
  -e http.cors.enabled=true ^
  -e "http.cors.allow-origin=\"*\"" ^
  -e http.cors.allow-headers="X-Requested-With,X-Auth-Token,Content-Type,Content-Length,Authorization" ^
  -e http.cors.allow-credentials=true ^
  -e network.publish_host=localhost ^
  -e xpack.security.enabled=false ^
  -v %cd%/data:/usr/share/elasticsearch/data ^
  docker.elastic.co/elasticsearch/elasticsearch:8.15.1

docker run -d ^
  -v /home/azureuser/llm/models:/models ^
  -v /home/azureuser/llm/ollama_data:/root/.ollama ^
  -p 11434:11434 ^
  --name ollama ^
  ollama/ollama

docker exec -it ollama ollama pull bge-m3
docker exec -it ollama ollama pull llama3.2:1b