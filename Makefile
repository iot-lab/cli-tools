generate:
	rm -rf iotlabclient 2>/dev/null
	docker build -t open-api-generator generator
	docker run --rm --user $$(id -u) -v ${PWD}:/local open-api-generator java -jar /opt/openapi-generator-cli/openapi-generator-cli.jar generate -g python -i /local/swagger.yaml -o /local/iotlabclient -DpackageName=iotlabclient
