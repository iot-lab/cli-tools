TM_SWAGGER = ../testbed-manager/swagger/swagger.yaml

generate:
	rm -rf iotlabclient 2>/dev/null
	rm -rf /tmp/iotlab_client 2>/dev/null
	docker build -t open-api-generator generator
ifeq (,$(wildcard $TM_SWAGGER))
	cp $(TM_SWAGGER) .
else
	wget http://api.iot-lab.info/swagger.yaml -O swagger.yaml
endif
	docker run --rm --user $$(id -u) -v /tmp:/output -v ${PWD}:/local open-api-generator java -jar /opt/openapi-generator-cli/openapi-generator-cli.jar generate --git-user-id iot-lab --git-repo-id cli-tools -g python -i /local/swagger.yaml -o /output/iotlab_client -DpackageName=iotlabclient
	cp -r /tmp/iotlab_client/iotlabclient .
	cp -r /tmp/iotlab_client/README.md iotlabclient/README.md
	cp -r /tmp/iotlab_client/docs iotlabclient/docs
