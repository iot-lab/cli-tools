generate:
	rm -rf iotlabclient 2>/dev/null
	docker build -t open-api-generator generator
	docker run --rm --user $$(id -u) -v /tmp:/output -v ${PWD}:/local open-api-generator java -jar /opt/openapi-generator-cli/openapi-generator-cli.jar generate -g python -i /local/swagger.yaml -o /output/iotlab_client -DpackageName=iotlabclient
	cp -r /tmp/iotlab_client/iotlabclient .
	cp -r /tmp/iotlab_client/README.md iotlabclient/README.md
