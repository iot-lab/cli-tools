generate:
	docker run --rm -v ${PWD}:/local openapitools/openapi-generator-cli generate -g python -i /local/swagger.yaml -o /local/iotlabclient -DpackageName=iotlabclient
