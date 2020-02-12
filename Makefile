SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

clean:
	@rm -f .coverage coverage.xml

install-dev:
	@pipenv install --dev

.PHONY: coverage
coverage:
	@printf "Running coverage"																	&& \
	 rm -f .coverage coverage.xml																&& \
	 pipenv run coverage run -m unittest discover -s tests

.PHONY: coverage-xml
coverage-xml: coverage
	@printf "Generating coverage XML"
	 pipenv run coverage xml