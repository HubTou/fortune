NAME=fortune
SOURCES=main.py
DESTROOTDIR=/usr/local

# Default action is to show this help message:
.help:
	@echo "Possible targets:"
	@echo "  check-code     Verify PEP 8 compliance (lint)"
	@echo "  check-security Verify security issues (audit)"
	@echo "  check-unused   Find unused code"
	@echo "  check-version  Find required Python version"
	@echo "  check-sloc     Count Single Lines of Code"
	@echo "  checks         Make all the previous tests"
	@echo "  format         Format code"
	@echo "  install        Install under ${DESTROOTDIR}"
	@echo "  uninstall      Uninstall from ${DESTROOTDIR}"
	@echo "  whatis         Rebuild the whatis(1) database"
	@echo "  clean          Remove the compressed man page"
	@echo "  distclean      Remove everything made"

check-code: /usr/local/bin/pylint
	-pylint ${SOURCES}

lint: check-code

check-security: /usr/local/bin/bandit
	-bandit -r ${SOURCES}

audit: check-security

check-unused: /usr/local/bin/vulture
	-vulture --sort-by-size ${SOURCES}

check-version: /usr/local/bin/vermin
	-vermin ${SOURCES}

check-sloc: /usr/local/bin/pygount
	-pygount --format=summary .

checks: check-code check-security check-unused check-version check-sloc

format: /usr/local/bin/black
	black ${SOURCES}

${NAME}.6.gz: ../../man/${NAME}.6
	@gzip -k9c ../../man/${NAME}.6 > ${NAME}.6.gz

install: ${NAME}.6.gz
	install -m 0755 -o root -g wheel main.py ${DESTROOTDIR}/bin/${NAME}
	install -m 0644 -o root -g wheel ${NAME}.6.gz ${DESTROOTDIR}/man/man6

uninstall:
	rm -f ${DESTROOTDIR}/bin/${NAME}
	rm -f ${DESTROOTDIR}/man/man1/${NAME}.6.gz

whatis:
	makewhatis

love:
	@echo "Not war!"

clean:
	@rm -f ${NAME}.6.gz

distclean: clean

